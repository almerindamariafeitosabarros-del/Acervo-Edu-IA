import mimetypes

from django.db.models import Q
from django.http import FileResponse, Http404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsModeratorOrAdmin

from .models import AttachmentKind, MuralAttachment, MuralPost, PostStatus, ReportStatus
from .serializers import (
    ModerationEntrySerializer,
    MuralPostEditSerializer,
    MuralPostSerializer,
    MuralPostWriteSerializer,
    MuralReportSerializer,
)

BASE_QUERYSET = MuralPost.objects.select_related('author', 'author__institution').prefetch_related(
    'attachments', 'attachments__document'
)


class MuralPostListCreateView(generics.ListCreateAPIView):
    """GET /api/mural/posts/ — feed público, aberto a visitantes (RF20).
    POST — nova publicação, exige login (RF19)."""

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self):
        return MuralPostWriteSerializer if self.request.method == 'POST' else MuralPostSerializer

    def get_queryset(self):
        return BASE_QUERYSET.filter(parent__isnull=True, status=PostStatus.VISIBLE).order_by(
            '-created_at'
        )


class MuralCommentListView(generics.ListAPIView):
    """GET /api/mural/posts/{post_id}/comments/ (RF26). Comentar é um POST comum
    em /api/mural/posts/ com `parent` preenchido."""

    permission_classes = [AllowAny]
    serializer_class = MuralPostSerializer

    def get_queryset(self):
        post = BASE_QUERYSET.filter(pk=self.kwargs['post_id'], status=PostStatus.VISIBLE).first()
        if post is None:
            raise Http404
        return BASE_QUERYSET.filter(parent=post, status=PostStatus.VISIBLE).order_by('created_at')


class MuralPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET (aberto), PUT/DELETE (autor ou moderação — RF23)."""

    queryset = BASE_QUERYSET.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return MuralPostEditSerializer
        return MuralPostSerializer

    def get_object(self):
        post = super().get_object()
        if self.request.method == 'GET' and post.status != PostStatus.VISIBLE:
            user = self.request.user if self.request.user.is_authenticated else None
            visible_to_author = user is not None and post.author_id == user.id
            if not visible_to_author and not post.can_be_moderated_by(user):
                raise Http404
        return post

    def perform_update(self, serializer):
        post = self.get_object()
        if not post.can_be_edited_by(self.request.user):
            raise PermissionDenied('Você só pode editar as próprias publicações.')
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if not (post.can_be_edited_by(request.user) or post.can_be_moderated_by(request.user)):
            raise PermissionDenied('Você não tem permissão para excluir esta publicação.')
        # Exclusão lógica: preserva o histórico (mesma convenção do PRD para documentos).
        post.status = PostStatus.REMOVED
        post.save(update_fields=['status'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class MuralReportCreateView(APIView):
    """POST /api/mural/posts/{post_id}/report/ — uma denúncia por usuário (RF21)."""

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = BASE_QUERYSET.filter(pk=post_id, status=PostStatus.VISIBLE).first()
        if post is None:
            raise Http404
        serializer = MuralReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if post.reports.filter(reporter=request.user).exists():
            return Response(
                {'detail': 'Você já denunciou esta publicação.'}, status=status.HTTP_400_BAD_REQUEST
            )
        post.register_report(
            reporter=request.user,
            reason=serializer.validated_data['reason'],
            details=serializer.validated_data.get('details', ''),
        )
        post.refresh_from_db()
        return Response(
            MuralPostSerializer(post, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class ModerationQueueView(generics.ListAPIView):
    """GET /api/mural/moderation/ — fila de denúncias pendentes (RF22, Tela 8)."""

    permission_classes = [IsModeratorOrAdmin]
    serializer_class = ModerationEntrySerializer

    def get_queryset(self):
        return (
            BASE_QUERYSET.filter(Q(status=PostStatus.HIDDEN) | Q(reports__status=ReportStatus.PENDING))
            .distinct()
            .order_by('-report_count', '-created_at')
        )


class ModerationDecisionView(APIView):
    """POST /api/mural/moderation/{post_id}/decidir/ — {"decision": "hide"|"keep"}."""

    permission_classes = [IsModeratorOrAdmin]

    def post(self, request, post_id):
        post = MuralPost.objects.filter(pk=post_id).first()
        if post is None:
            raise Http404
        decision = request.data.get('decision')
        if decision not in ('hide', 'keep'):
            return Response(
                {'detail': 'Informe decision: "hide" ou "keep".'}, status=status.HTTP_400_BAD_REQUEST
            )
        report_status = ReportStatus.HIDDEN if decision == 'hide' else ReportStatus.KEPT
        post.reports.filter(status=ReportStatus.PENDING).update(
            status=report_status, reviewed_by=request.user, reviewed_at=timezone.now()
        )
        post.status = PostStatus.HIDDEN if decision == 'hide' else PostStatus.VISIBLE
        post.save(update_fields=['status'])
        return Response(MuralPostSerializer(post, context={'request': request}).data)


class MuralAttachmentFileView(APIView):
    """Anexos do mural são sempre públicos (seção 10.1 do PRD)."""

    permission_classes = [AllowAny]

    def get(self, request, pk):
        attachment = (
            MuralAttachment.objects.filter(pk=pk, kind=AttachmentKind.FILE)
            .select_related('post')
            .first()
        )
        if attachment is None or not attachment.file or attachment.post.status != PostStatus.VISIBLE:
            raise Http404
        content_type, _ = mimetypes.guess_type(attachment.original_filename or attachment.file.name)
        as_attachment = request.query_params.get('download') == '1'
        try:
            handle = attachment.file.open('rb')
        except FileNotFoundError:
            raise Http404
        response = FileResponse(
            handle,
            as_attachment=as_attachment,
            filename=attachment.original_filename or f'anexo-{attachment.pk}',
            content_type=content_type or 'application/octet-stream',
        )
        response['X-Content-Type-Options'] = 'nosniff'
        return response

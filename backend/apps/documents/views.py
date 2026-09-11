import mimetypes

from django.db.models import Count, Q
from django.http import FileResponse, Http404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsManagerOrAdmin

from .filters import AllDocumentFilter, MyDocumentFilter, PublicDocumentFilter
from .models import Document, Visibility
from .serializers import DocumentSerializer, DocumentWriteSerializer

BASE_QUERYSET = Document.objects.select_related(
    'owner', 'category', 'subject', 'subject__course', 'subject__course__institution'
).prefetch_related('tags')

SEARCH_FIELDS = ['title', 'description', 'material_author', 'tags__name']


class MyDocumentViewSet(viewsets.ModelViewSet):
    """/api/documents/mine/ — documentos do próprio usuário."""

    filterset_class = MyDocumentFilter
    search_fields = SEARCH_FIELDS
    ordering_fields = ['created_at', 'title']

    def get_queryset(self):
        return BASE_QUERYSET.filter(owner=self.request.user).distinct()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return DocumentWriteSerializer
        return DocumentSerializer


class PublicDocumentListView(ListAPIView):
    """/api/documents/public/ — Acervo Público, visível a todos os cadastrados."""

    serializer_class = DocumentSerializer
    filterset_class = PublicDocumentFilter
    search_fields = SEARCH_FIELDS
    ordering_fields = ['published_at', 'created_at', 'title']
    ordering = ['-published_at']

    def get_queryset(self):
        return BASE_QUERYSET.filter(visibility=Visibility.PUBLIC).distinct()


class AllDocumentListView(ListAPIView):
    """/api/documents/all/ — moderação de documentos (Gestor e Administrador)."""

    serializer_class = DocumentSerializer
    permission_classes = [IsManagerOrAdmin]
    filterset_class = AllDocumentFilter
    search_fields = SEARCH_FIELDS + ['owner__name', 'owner__email']
    ordering_fields = ['created_at', 'published_at', 'title']

    def get_queryset(self):
        return BASE_QUERYSET.all().distinct()


class DocumentDetailViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """/api/documents/{id}/ — detalhar, editar, excluir, publicar e baixar.

    Documento privado de outro usuário responde 404 (não revela a existência).
    O cadastro de documentos é feito por /api/documents/mine/.
    """

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return DocumentWriteSerializer
        return DocumentSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Document.objects.none()
        queryset = BASE_QUERYSET.all()
        if user.can_manage_catalog:
            return queryset
        return queryset.filter(Q(visibility=Visibility.PUBLIC) | Q(owner=user))

    def get_object(self):
        document = super().get_object()
        if not document.can_be_viewed_by(self.request.user):
            raise Http404
        return document

    def _require_edit(self, document):
        if not document.can_be_edited_by(self.request.user):
            raise PermissionDenied('Você não tem permissão para alterar este documento.')

    def update(self, request, *args, **kwargs):
        self._require_edit(self.get_object())
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        document = self.get_object()
        self._require_edit(document)
        document.file.delete(save=False)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        document = self.get_object()
        if not document.can_be_published_by(request.user):
            raise PermissionDenied('Você não tem permissão para publicar este documento.')
        document.publish()
        return Response(DocumentSerializer(document, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        document = self.get_object()
        if not document.can_be_published_by(request.user):
            raise PermissionDenied('Você não tem permissão para despublicar este documento.')
        document.unpublish()
        return Response(DocumentSerializer(document, context={'request': request}).data)

    @action(detail=True, methods=['get'])
    def file(self, request, pk=None):
        """Entrega o arquivo somente depois de checar o acesso."""
        document = self.get_object()
        if not document.file:
            raise Http404
        content_type, _ = mimetypes.guess_type(document.original_filename or document.file.name)
        filename = document.original_filename or f'documento-{document.pk}'
        as_attachment = request.query_params.get('download') == '1'
        try:
            handle = document.file.open('rb')
        except FileNotFoundError:
            raise Http404
        response = FileResponse(
            handle,
            as_attachment=as_attachment,
            filename=filename,
            content_type=content_type or 'application/octet-stream',
        )
        response['X-Content-Type-Options'] = 'nosniff'
        return response


class DocumentStatsView(APIView):
    """Contadores exibidos na tela de Início."""

    def get(self, request):
        user = request.user
        own = Document.objects.filter(owner=user).aggregate(
            total=Count('id'),
            published=Count('id', filter=Q(visibility=Visibility.PUBLIC)),
        )
        data = {
            'my_documents': own['total'],
            'my_published': own['published'],
            'public_documents': Document.objects.filter(visibility=Visibility.PUBLIC).count(),
        }
        if user.can_manage_catalog:
            from apps.accounts.models import User

            data['total_documents'] = Document.objects.count()
            data['total_private'] = Document.objects.filter(visibility=Visibility.PRIVATE).count()
            data['total_users'] = User.objects.filter(is_active=True).count()
        return Response(data)

from django.db.models import Count, ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsManagerOrAdmin, ReadOnlyOrAdmin, ReadOnlyOrManager

from .models import Category, Course, Institution, Subject, SubjectMember, Tag
from .serializers import (
    CategorySerializer,
    CourseSerializer,
    InstitutionSerializer,
    SubjectMemberSerializer,
    SubjectSerializer,
    TagSerializer,
)


class ProtectedDeleteMixin:
    """Devolve uma mensagem clara quando o registro está em uso."""

    in_use_message = 'Não é possível excluir: o registro está sendo usado.'

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response({'detail': self.in_use_message}, status=status.HTTP_400_BAD_REQUEST)


class InstitutionViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    """Instituições — leitura para todos; escrita apenas para Administrador."""

    serializer_class = InstitutionSerializer
    permission_classes = [ReadOnlyOrAdmin]
    search_fields = ['name', 'acronym']
    filterset_fields = ['is_active']
    pagination_class = None
    in_use_message = 'Não é possível excluir: existem cursos ou usuários nesta instituição.'

    def get_queryset(self):
        return Institution.objects.annotate(courses_count=Count('courses')).order_by('name')


class CourseViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    """Cursos — leitura para todos; escrita para Gestor e Administrador."""

    serializer_class = CourseSerializer
    permission_classes = [ReadOnlyOrManager]
    search_fields = ['name']
    filterset_fields = ['institution', 'is_active']
    pagination_class = None
    in_use_message = 'Não é possível excluir: existem disciplinas neste curso.'

    def get_queryset(self):
        return (
            Course.objects.select_related('institution')
            .annotate(subjects_count=Count('subjects'))
            .order_by('name')
        )


class SubjectViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    """Disciplinas — leitura para todos; escrita para Gestor e Administrador."""

    serializer_class = SubjectSerializer
    permission_classes = [ReadOnlyOrManager]
    search_fields = ['name']
    filterset_fields = ['course', 'course__institution', 'is_active']
    pagination_class = None
    in_use_message = 'Não é possível excluir: existem documentos nesta disciplina.'

    def get_queryset(self):
        return Subject.objects.select_related('course', 'course__institution').order_by('name')

    @action(detail=True, methods=['get', 'post'], permission_classes=[IsManagerOrAdmin])
    def members(self, request, pk=None):
        """Lista ou vincula usuários à disciplina — controla o acesso Restrito."""
        subject = self.get_object()
        if request.method == 'GET':
            members = subject.members.select_related('user').order_by('user__name')
            return Response(SubjectMemberSerializer(members, many=True).data)
        serializer = SubjectMemberSerializer(data=request.data, context={'subject': subject})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['delete'],
        url_path='members/(?P<member_id>[^/.]+)',
        permission_classes=[IsManagerOrAdmin],
    )
    def remove_member(self, request, pk=None, member_id=None):
        subject = self.get_object()
        member = get_object_or_404(SubjectMember, pk=member_id, subject=subject)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    """Categorias — leitura para todos; escrita para Gestor e Administrador."""

    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrManager]
    search_fields = ['name']
    filterset_fields = ['is_active']
    pagination_class = None
    in_use_message = 'Não é possível excluir: existem documentos nesta categoria.'
    queryset = Category.objects.all().order_by('name')


class TagViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    """Tags — leitura para todos; escrita para Gestor e Administrador."""

    serializer_class = TagSerializer
    permission_classes = [ReadOnlyOrManager]
    search_fields = ['name']
    pagination_class = None
    queryset = Tag.objects.all().order_by('name')

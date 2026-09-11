from django.db.models import Count, ProtectedError
from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.accounts.permissions import ReadOnlyOrAdmin, ReadOnlyOrManager

from .models import Category, Course, Institution, Subject, Tag
from .serializers import (
    CategorySerializer,
    CourseSerializer,
    InstitutionSerializer,
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

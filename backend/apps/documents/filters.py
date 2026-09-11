import django_filters as filters

from .models import Document


class PublicDocumentFilter(filters.FilterSet):
    """Filtros do Acervo Público: instituição, curso, disciplina, categoria e autor."""

    institution = filters.NumberFilter(field_name='subject__course__institution_id')
    course = filters.NumberFilter(field_name='subject__course_id')
    subject = filters.NumberFilter(field_name='subject_id')
    category = filters.NumberFilter(field_name='category_id')
    owner = filters.NumberFilter(field_name='owner_id')
    author = filters.CharFilter(field_name='material_author', lookup_expr='icontains')
    tag = filters.CharFilter(field_name='tags__name', lookup_expr='iexact')

    class Meta:
        model = Document
        fields = ['institution', 'course', 'subject', 'category', 'owner', 'author', 'tag']


class MyDocumentFilter(filters.FilterSet):
    """Filtros de Meus Documentos."""

    visibility = filters.CharFilter(field_name='visibility')
    category = filters.NumberFilter(field_name='category_id')
    subject = filters.NumberFilter(field_name='subject_id')

    class Meta:
        model = Document
        fields = ['visibility', 'category', 'subject']


class AllDocumentFilter(PublicDocumentFilter):
    """Filtros da aba Todos os Documentos (Gestor/Admin)."""

    visibility = filters.CharFilter(field_name='visibility')

    class Meta(PublicDocumentFilter.Meta):
        fields = PublicDocumentFilter.Meta.fields + ['visibility']

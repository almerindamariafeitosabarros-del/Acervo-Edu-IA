import os

from django.conf import settings
from rest_framework import serializers

from apps.academics.models import Tag

from .models import Document, Visibility


class DocumentTagField(serializers.ListField):
    """Recebe uma lista de nomes de tags e devolve os objetos Tag."""

    child = serializers.CharField(max_length=60)

    def to_internal_value(self, data):
        # multipart/form-data manda tags como itens repetidos ou separados por vírgula.
        if isinstance(data, str):
            data = [data]
        names = super().to_internal_value(data)
        tags = []
        vistas = set()
        for item in names:
            for raw in item.split(','):
                name = raw.strip()
                if not name or name.lower() in vistas:
                    continue
                vistas.add(name.lower())
                tag, _ = Tag.objects.get_or_create(name__iexact=name, defaults={'name': name})
                tags.append(tag)
        return tags


def validate_uploaded_file(value):
    extension = os.path.splitext(value.name)[1].lower().lstrip('.')
    if extension not in settings.ALLOWED_UPLOAD_EXTENSIONS:
        permitidos = ', '.join(e.upper() for e in settings.ALLOWED_UPLOAD_EXTENSIONS)
        raise serializers.ValidationError(f'Formato não permitido. Envie um arquivo {permitidos}.')
    if value.size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise serializers.ValidationError(
            f'Arquivo muito grande. O limite é {settings.MAX_UPLOAD_SIZE_MB} MB.'
        )
    return value


class DocumentSerializer(serializers.ModelSerializer):
    """Leitura de documento com os metadados exibidos nas telas."""

    owner_name = serializers.CharField(source='owner.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    subject_name = serializers.CharField(source='subject.name', read_only=True, default=None)
    course_name = serializers.CharField(source='subject.course.name', read_only=True, default=None)
    institution_name = serializers.CharField(
        source='subject.course.institution.name', read_only=True, default=None
    )
    course = serializers.IntegerField(source='subject.course_id', read_only=True, default=None)
    institution = serializers.IntegerField(
        source='subject.course.institution_id', read_only=True, default=None
    )
    tags = serializers.SlugRelatedField(slug_field='name', many=True, read_only=True)
    visibility_display = serializers.CharField(source='get_visibility_display', read_only=True)
    extension = serializers.CharField(read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'description', 'material_author',
            'subject', 'subject_name', 'course', 'course_name',
            'institution', 'institution_name',
            'category', 'category_name', 'tags',
            'original_filename', 'file_size', 'extension',
            'owner', 'owner_name', 'visibility', 'visibility_display',
            'published_at', 'created_at', 'updated_at', 'permissions',
        ]

    def get_permissions(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        return {
            'can_edit': obj.can_be_edited_by(user),
            'can_publish': obj.can_be_published_by(user),
        }


class DocumentWriteSerializer(serializers.ModelSerializer):
    """Criação e edição. Todo documento novo nasce privado."""

    tags = DocumentTagField(required=False)
    file = serializers.FileField(required=True, validators=[validate_uploaded_file])

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'description', 'material_author',
            'subject', 'category', 'tags', 'file',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Na edição o arquivo é opcional (mantém o já enviado).
        if self.instance is not None:
            self.fields['file'].required = False

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Informe o título do documento.')
        return value

    def _apply_file_metadata(self, instance, uploaded):
        instance.original_filename = uploaded.name[:255]
        instance.file_size = uploaded.size

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        uploaded = validated_data['file']
        document = Document(
            owner=self.context['request'].user,
            visibility=Visibility.PRIVATE,
            **validated_data,
        )
        self._apply_file_metadata(document, uploaded)
        document.save()
        document.tags.set(tags)
        return document

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        uploaded = validated_data.get('file')
        document = super().update(instance, validated_data)
        if uploaded:
            self._apply_file_metadata(document, uploaded)
            document.save(update_fields=['original_filename', 'file_size'])
        if tags is not None:
            document.tags.set(tags)
        return document

    def to_representation(self, instance):
        return DocumentSerializer(instance, context=self.context).data

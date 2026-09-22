import os

from django.conf import settings
from rest_framework import serializers

from apps.documents.models import Document, Visibility

from .models import (
    AttachmentKind,
    MuralAttachment,
    MuralPost,
    MuralReport,
    PostStatus,
    ReportStatus,
)


def validate_mural_file(value):
    extension = os.path.splitext(value.name)[1].lower().lstrip('.')
    if extension not in settings.MURAL_ALLOWED_ATTACHMENT_EXTENSIONS:
        permitidos = ', '.join(e.upper() for e in settings.MURAL_ALLOWED_ATTACHMENT_EXTENSIONS)
        raise serializers.ValidationError(f'Formato não permitido. Envie um arquivo {permitidos}.')
    if value.size > settings.MURAL_MAX_ATTACHMENT_SIZE_BYTES:
        raise serializers.ValidationError(
            f'Arquivo muito grande. O limite é {settings.MURAL_MAX_ATTACHMENT_SIZE_MB} MB.'
        )
    return value


class MuralAttachmentSerializer(serializers.ModelSerializer):
    kind_display = serializers.CharField(source='get_kind_display', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True, default=None)

    class Meta:
        model = MuralAttachment
        fields = [
            'id', 'kind', 'kind_display', 'original_filename', 'mime_type', 'size_bytes',
            'url', 'link_title', 'document', 'document_title', 'created_at',
        ]


class MuralPostSerializer(serializers.ModelSerializer):
    """Leitura de uma publicação (ou comentário) do mural — aberto a visitantes."""

    author_name = serializers.CharField(source='author.name', read_only=True)
    author_institution = serializers.CharField(
        source='author.institution.name', read_only=True, default=None
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    attachments = MuralAttachmentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = MuralPost
        fields = [
            'id', 'author', 'author_name', 'author_institution', 'parent',
            'text', 'status', 'status_display', 'report_count',
            'attachments', 'comments_count', 'permissions',
            'created_at', 'edited_at',
        ]

    def get_comments_count(self, obj):
        return obj.comments.filter(status=PostStatus.VISIBLE).count()

    def get_permissions(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        return {
            'can_edit': obj.can_be_edited_by(user),
            'can_moderate': obj.can_be_moderated_by(user),
        }


class MuralPostWriteSerializer(serializers.ModelSerializer):
    """Cria publicação (parent vazio) ou comentário (parent preenchido)."""

    attachment_file = serializers.FileField(
        required=False, write_only=True, validators=[validate_mural_file]
    )
    attachment_url = serializers.URLField(required=False, write_only=True, max_length=500)
    attachment_link_title = serializers.CharField(
        required=False, write_only=True, max_length=255, allow_blank=True
    )
    attachment_document_id = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = MuralPost
        fields = [
            'id', 'parent', 'text',
            'attachment_file', 'attachment_url', 'attachment_link_title', 'attachment_document_id',
        ]

    def validate(self, attrs):
        parent = attrs.get('parent')
        text = (attrs.get('text') or '').strip()
        has_attachment = any(
            attrs.get(key) for key in ('attachment_file', 'attachment_url', 'attachment_document_id')
        )

        if parent is not None:
            if parent.is_comment:
                raise serializers.ValidationError({'parent': 'Não é possível comentar em um comentário.'})
            if has_attachment:
                raise serializers.ValidationError('Comentários não podem ter anexo.')
            if not text:
                raise serializers.ValidationError({'text': 'Escreva um comentário.'})
        elif not text and not has_attachment:
            raise serializers.ValidationError('Escreva algo ou anexe um documento, artigo ou link.')

        provided_kinds = sum([
            bool(attrs.get('attachment_file')),
            bool(attrs.get('attachment_url')),
            bool(attrs.get('attachment_document_id')),
        ])
        if provided_kinds > 1:
            raise serializers.ValidationError('Envie apenas um tipo de anexo por publicação.')

        if attrs.get('attachment_document_id'):
            document = Document.objects.filter(pk=attrs['attachment_document_id']).first()
            if document is None or document.visibility != Visibility.PUBLIC or not document.is_published:
                raise serializers.ValidationError(
                    {'attachment_document_id': 'Só é possível compartilhar um documento do Acervo Público.'}
                )
            attrs['_document'] = document

        attrs['text'] = text
        return attrs

    def create(self, validated_data):
        attachment_file = validated_data.pop('attachment_file', None)
        attachment_url = validated_data.pop('attachment_url', '')
        attachment_link_title = validated_data.pop('attachment_link_title', '')
        validated_data.pop('attachment_document_id', None)
        document = validated_data.pop('_document', None)

        post = MuralPost.objects.create(author=self.context['request'].user, **validated_data)

        if attachment_file:
            MuralAttachment.objects.create(
                post=post,
                kind=AttachmentKind.FILE,
                file=attachment_file,
                original_filename=attachment_file.name[:255],
                mime_type=getattr(attachment_file, 'content_type', '') or '',
                size_bytes=attachment_file.size,
            )
        elif attachment_url:
            MuralAttachment.objects.create(
                post=post,
                kind=AttachmentKind.LINK,
                url=attachment_url,
                link_title=attachment_link_title,
            )
        elif document:
            MuralAttachment.objects.create(post=post, kind=AttachmentKind.DOCUMENT, document=document)

        return post

    def to_representation(self, instance):
        return MuralPostSerializer(instance, context=self.context).data


class MuralPostEditSerializer(serializers.ModelSerializer):
    """Edição: só o texto pode mudar (RF23)."""

    class Meta:
        model = MuralPost
        fields = ['text']

    def validate_text(self, value):
        value = value.strip()
        if not value and not self.instance.attachments.exists():
            raise serializers.ValidationError('Escreva algo ou mantenha o anexo.')
        return value

    def to_representation(self, instance):
        return MuralPostSerializer(instance, context=self.context).data


class MuralReportSerializer(serializers.ModelSerializer):
    """Criação de uma denúncia (POST /api/mural/posts/{id}/report/)."""

    class Meta:
        model = MuralReport
        fields = ['id', 'reason', 'details']


class MuralReportDetailSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source='reporter.name', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)

    class Meta:
        model = MuralReport
        fields = ['id', 'reporter_name', 'reason', 'reason_display', 'details', 'created_at']


class ModerationEntrySerializer(MuralPostSerializer):
    """Fila de moderação (Tela 8): publicação + denúncias pendentes."""

    reports = serializers.SerializerMethodField()

    class Meta(MuralPostSerializer.Meta):
        fields = MuralPostSerializer.Meta.fields + ['reports']

    def get_reports(self, obj):
        pending = obj.reports.filter(status=ReportStatus.PENDING).select_related('reporter')
        return MuralReportDetailSerializer(pending, many=True).data

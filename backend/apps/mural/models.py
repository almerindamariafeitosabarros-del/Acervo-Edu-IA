import os
import uuid

from django.conf import settings
from django.db import models

REPORT_THRESHOLD = 5


def mural_upload_path(instance, filename):
    """Guarda o anexo com nome aleatório dentro da pasta da publicação."""
    extension = os.path.splitext(filename)[1].lower()
    return f'mural/{instance.post_id}/{uuid.uuid4().hex}{extension}'


class PostStatus(models.TextChoices):
    VISIBLE = 'visible', 'Visível'
    HIDDEN = 'hidden', 'Oculta'
    REMOVED = 'removed', 'Removida'


class MuralPost(models.Model):
    """Publicação ou comentário do mural público. Visível a todos, inclusive
    visitantes sem login."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='autor',
        on_delete=models.CASCADE,
        related_name='mural_posts',
    )
    parent = models.ForeignKey(
        'self',
        verbose_name='publicação original',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comments',
    )
    text = models.CharField('texto', max_length=2000, blank=True)
    status = models.CharField(
        'status', max_length=9, choices=PostStatus.choices, default=PostStatus.VISIBLE
    )
    report_count = models.PositiveIntegerField('denúncias', default=0)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    edited_at = models.DateTimeField('editado em', auto_now=True)

    class Meta:
        verbose_name = 'publicação do mural'
        verbose_name_plural = 'publicações do mural'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status', '-created_at'])]

    def __str__(self):
        return f'{self.author} — {self.text[:50]}'

    @property
    def is_comment(self):
        return self.parent_id is not None

    def can_be_edited_by(self, user):
        """Só o autor edita ou exclui a própria publicação (RF23)."""
        if not user or not user.is_authenticated:
            return False
        return self.author_id == user.id

    def can_be_moderated_by(self, user):
        return bool(user) and user.is_authenticated and user.can_moderate_mural

    def register_report(self, reporter, reason, details=''):
        """Registra a denúncia (uma por usuário) e oculta com 5+ denúncias (RF21, HU06)."""
        report, created = MuralReport.objects.get_or_create(
            post=self,
            reporter=reporter,
            defaults={'reason': reason, 'details': details},
        )
        if not created:
            return report
        self.__class__.objects.filter(pk=self.pk).update(
            report_count=models.F('report_count') + 1
        )
        self.refresh_from_db(fields=['report_count'])
        if self.report_count >= REPORT_THRESHOLD and self.status == PostStatus.VISIBLE:
            self.status = PostStatus.HIDDEN
            self.save(update_fields=['status'])
        return report


class AttachmentKind(models.TextChoices):
    FILE = 'file', 'Arquivo'
    LINK = 'link', 'Link'
    DOCUMENT = 'document', 'Documento do acervo'


class MuralAttachment(models.Model):
    """Arquivo, link ou documento do acervo anexado a uma publicação."""

    post = models.ForeignKey(
        MuralPost, verbose_name='publicação', on_delete=models.CASCADE, related_name='attachments'
    )
    kind = models.CharField('tipo', max_length=9, choices=AttachmentKind.choices)

    file = models.FileField('arquivo', upload_to=mural_upload_path, null=True, blank=True)
    original_filename = models.CharField('nome original', max_length=255, blank=True)
    mime_type = models.CharField('tipo mime', max_length=100, blank=True)
    size_bytes = models.PositiveBigIntegerField('tamanho (bytes)', default=0)

    url = models.URLField('url', max_length=500, blank=True)
    link_title = models.CharField('título do link', max_length=255, blank=True)

    # Só pode referenciar documento PÚBLICO (regra validada no serializer).
    document = models.ForeignKey(
        'documents.Document',
        verbose_name='documento do acervo',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='mural_attachments',
    )

    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'anexo do mural'
        verbose_name_plural = 'anexos do mural'

    def __str__(self):
        return f'{self.get_kind_display()} — publicação #{self.post_id}'


class ReportReason(models.TextChoices):
    SPAM = 'spam', 'Spam'
    OFFENSIVE = 'offensive', 'Ofensivo'
    COPYRIGHT = 'copyright', 'Direitos autorais'
    OTHER = 'other', 'Outro'


class ReportStatus(models.TextChoices):
    PENDING = 'pending', 'Pendente'
    KEPT = 'kept', 'Mantida'
    HIDDEN = 'hidden', 'Ocultada'


class MuralReport(models.Model):
    """Denúncia de publicação do mural (uma por denunciante)."""

    post = models.ForeignKey(
        MuralPost, verbose_name='publicação', on_delete=models.CASCADE, related_name='reports'
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='denunciante',
        on_delete=models.CASCADE,
        related_name='mural_reports',
    )
    reason = models.CharField('motivo', max_length=20, choices=ReportReason.choices)
    details = models.TextField('detalhes', blank=True)
    status = models.CharField(
        'status', max_length=9, choices=ReportStatus.choices, default=ReportStatus.PENDING
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='revisado por',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mural_reports_reviewed',
    )
    reviewed_at = models.DateTimeField('revisado em', null=True, blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'denúncia do mural'
        verbose_name_plural = 'denúncias do mural'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['post', 'reporter'], name='unique_mural_report'),
        ]

    def __str__(self):
        return f'Denúncia de {self.reporter} em #{self.post_id}'

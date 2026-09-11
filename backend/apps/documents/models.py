import os
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


def document_upload_path(instance, filename):
    """Guarda o arquivo com nome aleatório dentro da pasta do dono."""
    extension = os.path.splitext(filename)[1].lower()
    return f'documents/{instance.owner_id}/{uuid.uuid4().hex}{extension}'


class Visibility(models.TextChoices):
    PRIVATE = 'private', 'Privado'
    PUBLIC = 'public', 'Público'


class Document(models.Model):
    """Documento educacional enviado por um usuário."""

    title = models.CharField('título', max_length=200)
    description = models.TextField('descrição', blank=True)
    material_author = models.CharField('autor do material', max_length=200, blank=True)

    subject = models.ForeignKey(
        'academics.Subject',
        verbose_name='disciplina',
        on_delete=models.PROTECT,
        related_name='documents',
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        'academics.Category',
        verbose_name='categoria',
        on_delete=models.PROTECT,
        related_name='documents',
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField(
        'academics.Tag', verbose_name='tags', related_name='documents', blank=True
    )

    file = models.FileField('arquivo', upload_to=document_upload_path)
    original_filename = models.CharField('nome original do arquivo', max_length=255, blank=True)
    file_size = models.PositiveBigIntegerField('tamanho do arquivo (bytes)', default=0)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='dono',
        on_delete=models.CASCADE,
        related_name='documents',
    )
    visibility = models.CharField(
        'visibilidade', max_length=10, choices=Visibility.choices, default=Visibility.PRIVATE
    )
    published_at = models.DateTimeField('publicado em', null=True, blank=True)

    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'documento'
        verbose_name_plural = 'documentos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['visibility', '-published_at']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_public(self):
        return self.visibility == Visibility.PUBLIC

    @property
    def extension(self):
        name = self.original_filename or (self.file.name if self.file else '')
        return os.path.splitext(name)[1].lower().lstrip('.')

    # ------------------------------------------------------------------
    # Regras de acesso (sempre validadas no backend)
    # ------------------------------------------------------------------
    def can_be_viewed_by(self, user):
        """Público: todos os cadastrados. Privado: dono, Gestor e Admin."""
        if not user or not user.is_authenticated:
            return False
        if self.is_public:
            return True
        return self.owner_id == user.id or user.can_manage_catalog

    def can_be_edited_by(self, user):
        """Dono, Gestor e Administrador editam/excluem."""
        if not user or not user.is_authenticated:
            return False
        return self.owner_id == user.id or user.can_manage_catalog

    def can_be_published_by(self, user):
        """Professor dono (ou acima), Gestor e Administrador publicam."""
        if not user or not user.is_authenticated:
            return False
        if user.can_manage_catalog:
            return True
        return self.owner_id == user.id and user.can_publish_own

    # ------------------------------------------------------------------
    def publish(self):
        self.visibility = Visibility.PUBLIC
        self.published_at = timezone.now()
        self.save(update_fields=['visibility', 'published_at', 'updated_at'])

    def unpublish(self):
        self.visibility = Visibility.PRIVATE
        self.published_at = None
        self.save(update_fields=['visibility', 'published_at', 'updated_at'])

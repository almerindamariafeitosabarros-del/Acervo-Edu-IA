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
    PUBLIC = 'public', 'Público'
    COMMUNITY = 'community', 'Comunidade'
    RESTRICTED = 'restricted', 'Restrito'


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
    institution = models.ForeignKey(
        'academics.Institution',
        verbose_name='instituição',
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
        'visibilidade', max_length=10, choices=Visibility.choices, default=Visibility.COMMUNITY
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
        constraints = [
            models.CheckConstraint(
                check=~models.Q(visibility=Visibility.RESTRICTED) | models.Q(subject__isnull=False),
                name='document_restricted_requires_subject',
            ),
        ]

    def __str__(self):
        return self.title

    @property
    def is_public(self):
        return self.visibility == Visibility.PUBLIC

    @property
    def is_published(self):
        return self.published_at is not None

    @property
    def extension(self):
        name = self.original_filename or (self.file.name if self.file else '')
        return os.path.splitext(name)[1].lower().lstrip('.')

    def _is_institution_staff(self, user):
        """Gestor/Admin com poder sobre este documento: Admin geral (sem
        instituição) vê tudo; Gestor só a própria instituição."""
        if not user.can_manage_catalog:
            return False
        if user.is_admin_role:
            return True
        return user.institution_id is not None and user.institution_id == self.institution_id

    def _is_subject_member(self, user):
        return self.subject_id is not None and self.subject.members.filter(user_id=user.id).exists()

    # ------------------------------------------------------------------
    # Regras de acesso (sempre validadas no backend)
    # ------------------------------------------------------------------
    def can_be_viewed_by(self, user):
        """Rascunho: só dono e gestor/admin da instituição. Publicado:
        Público a todos; Comunidade à mesma instituição; Restrito a membro
        da disciplina, dono ou gestor/admin da instituição."""
        authenticated = bool(user) and user.is_authenticated
        if authenticated and self.owner_id == user.id:
            return True
        if authenticated and self._is_institution_staff(user):
            return True
        if not self.is_published:
            return False
        if self.visibility == Visibility.PUBLIC:
            return True
        if not authenticated:
            return False
        if self.visibility == Visibility.COMMUNITY:
            return user.institution_id is not None and user.institution_id == self.institution_id
        if self.visibility == Visibility.RESTRICTED:
            return self._is_subject_member(user)
        return False

    def can_be_edited_by(self, user):
        """Dono, Gestor e Administrador (da própria instituição) editam/excluem."""
        if not user or not user.is_authenticated:
            return False
        return self.owner_id == user.id or self._is_institution_staff(user)

    def can_be_published_by(self, user):
        """Professor dono (ou acima), Gestor e Administrador (da própria
        instituição) publicam."""
        if not user or not user.is_authenticated:
            return False
        if self._is_institution_staff(user):
            return True
        return self.owner_id == user.id and user.can_publish_own

    # ------------------------------------------------------------------
    def publish(self):
        self.published_at = timezone.now()
        self.save(update_fields=['published_at', 'updated_at'])

    def unpublish(self):
        self.published_at = None
        self.save(update_fields=['published_at', 'updated_at'])

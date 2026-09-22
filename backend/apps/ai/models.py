from django.conf import settings
from django.db import models


class AIQuery(models.Model):
    """Histórico de perguntas feitas ao assistente de IA local."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='usuário',
        on_delete=models.CASCADE,
        related_name='ai_queries',
    )
    document = models.ForeignKey(
        'documents.Document',
        verbose_name='documento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_queries',
    )
    # Preenchido quando a pergunta usou um arquivo avulso (não guardado no acervo).
    uploaded_filename = models.CharField('arquivo avulso', max_length=255, blank=True)

    prompt = models.TextField('pergunta')
    answer = models.TextField('resposta', blank=True)
    model = models.CharField('modelo', max_length=100, blank=True)
    response_time_ms = models.PositiveIntegerField('tempo de resposta (ms)', default=0)
    truncated = models.BooleanField('documento truncado', default=False)
    created_at = models.DateTimeField('data', auto_now_add=True)

    class Meta:
        verbose_name = 'consulta de IA'
        verbose_name_plural = 'consultas de IA'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} — {self.prompt[:50]}'

    @property
    def document_label(self):
        if self.document_id and self.document:
            return self.document.title
        return self.uploaded_filename or 'Documento removido'

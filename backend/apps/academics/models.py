from django.db import models
from django.utils.text import slugify


class Institution(models.Model):
    """Instituição de ensino. Primeiro nível da organização acadêmica."""

    name = models.CharField('nome', max_length=150, unique=True)
    acronym = models.CharField('sigla', max_length=20, blank=True)
    is_active = models.BooleanField('ativa', default=True)
    created_at = models.DateTimeField('criada em', auto_now_add=True)

    class Meta:
        verbose_name = 'instituição'
        verbose_name_plural = 'instituições'
        ordering = ['name']

    def __str__(self):
        return self.name


class Course(models.Model):
    """Curso pertencente a uma instituição."""

    institution = models.ForeignKey(
        Institution, verbose_name='instituição', on_delete=models.CASCADE, related_name='courses'
    )
    name = models.CharField('nome', max_length=150)
    is_active = models.BooleanField('ativo', default=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'curso'
        verbose_name_plural = 'cursos'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['institution', 'name'], name='unique_course_per_institution'),
        ]

    def __str__(self):
        return f'{self.name} ({self.institution.name})'


class Subject(models.Model):
    """Disciplina pertencente a um curso."""

    course = models.ForeignKey(
        Course, verbose_name='curso', on_delete=models.CASCADE, related_name='subjects'
    )
    name = models.CharField('nome', max_length=150)
    is_active = models.BooleanField('ativa', default=True)
    created_at = models.DateTimeField('criada em', auto_now_add=True)

    class Meta:
        verbose_name = 'disciplina'
        verbose_name_plural = 'disciplinas'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['course', 'name'], name='unique_subject_per_course'),
        ]

    def __str__(self):
        return f'{self.name} ({self.course.name})'


class Category(models.Model):
    """Categoria do material (ex.: Apostila, Slide, Artigo)."""

    name = models.CharField('nome', max_length=100, unique=True)
    description = models.CharField('descrição', max_length=255, blank=True)
    is_active = models.BooleanField('ativa', default=True)

    class Meta:
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Palavra-chave livre associada aos documentos."""

    name = models.CharField('nome', max_length=60, unique=True)
    slug = models.SlugField('identificador', max_length=70, unique=True, blank=True)

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        if not self.slug:
            self.slug = slugify(self.name)[:70] or 'tag'
        return super().save(*args, **kwargs)

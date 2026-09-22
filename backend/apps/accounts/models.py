from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class Role(models.TextChoices):
    """Perfis de acesso da plataforma, do menor para o maior privilégio."""

    STUDENT = 'student', 'Aluno'
    TEACHER = 'teacher', 'Professor'
    MODERATOR = 'moderator', 'Moderador'
    MANAGER = 'manager', 'Gestor'
    ADMIN = 'admin', 'Administrador'


# Versão vigente dos Termos de Uso e da Política de Privacidade. Ao mudar o
# texto da política, suba esta versão: o consentimento registrado deixa de valer
# e o usuário precisa aceitar de novo (LGPD, art. 8º).
TERMS_VERSION = '1.0'


# Ordem hierárquica usada pelas permissões (quanto maior, mais poderes).
# Moderador não participa da hierarquia acadêmica (não publica nem gerencia
# catálogo por causa do cargo): seu poder vem só de can_moderate_mural.
ROLE_LEVEL = {
    Role.STUDENT: 1,
    Role.MODERATOR: 1,
    Role.TEACHER: 2,
    Role.MANAGER: 3,
    Role.ADMIN: 4,
}


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório.')
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', Role.STUDENT)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário precisa ter is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Usuário da plataforma. O login é feito pelo e-mail."""

    name = models.CharField('nome', max_length=150)
    email = models.EmailField('e-mail', unique=True)
    role = models.CharField('perfil', max_length=20, choices=Role.choices, default=Role.STUDENT)
    institution = models.ForeignKey(
        'academics.Institution',
        verbose_name='instituição',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
    )
    is_active = models.BooleanField('ativo', default=True)
    is_staff = models.BooleanField('acessa o admin do Django', default=False)
    date_joined = models.DateTimeField('cadastrado em', default=timezone.now)

    # Registro do consentimento (LGPD, art. 8º, § 1º): guarda quando o titular
    # aceitou e qual versão do texto estava vigente.
    accepted_terms_at = models.DateTimeField('aceitou os termos em', null=True, blank=True)
    accepted_terms_version = models.CharField('versão dos termos aceita', max_length=10, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} <{self.email}>'

    def save(self, *args, **kwargs):
        self.email = self.email.lower().strip()
        return super().save(*args, **kwargs)

    # ------------------------------------------------------------------
    # Regras de perfil
    # ------------------------------------------------------------------
    @property
    def role_level(self):
        return ROLE_LEVEL.get(self.role, 0)

    def has_role_at_least(self, role):
        return self.role_level >= ROLE_LEVEL.get(role, 99)

    @property
    def is_student(self):
        return self.role == Role.STUDENT

    @property
    def is_teacher(self):
        return self.role == Role.TEACHER

    @property
    def is_manager(self):
        return self.role == Role.MANAGER

    @property
    def is_admin_role(self):
        return self.role == Role.ADMIN

    @property
    def is_moderator(self):
        return self.role == Role.MODERATOR

    @property
    def can_moderate_mural(self):
        """Moderador e Administrador ocultam/mantêm publicações e analisam denúncias (RF22)."""
        return self.is_moderator or self.is_admin_role

    @property
    def can_publish_own(self):
        """Professor, Gestor e Administrador publicam os próprios documentos."""
        return self.has_role_at_least(Role.TEACHER)

    @property
    def can_manage_catalog(self):
        """Gestor e Administrador gerenciam qualquer documento e o catálogo."""
        return self.has_role_at_least(Role.MANAGER)

    @property
    def can_manage_users(self):
        """Apenas o Administrador gerencia usuários e instituições."""
        return self.has_role_at_least(Role.ADMIN)

    @property
    def terms_accepted(self):
        """O consentimento vale apenas para a versão vigente dos termos."""
        return bool(self.accepted_terms_at) and self.accepted_terms_version == TERMS_VERSION

    def register_consent(self):
        self.accepted_terms_at = timezone.now()
        self.accepted_terms_version = TERMS_VERSION

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name.split(' ')[0] if self.name else self.email

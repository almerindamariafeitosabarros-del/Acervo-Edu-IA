from django.contrib.auth import authenticate, password_validation
from django.utils.crypto import get_random_string
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import TERMS_VERSION, Role, User


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    terms_accepted = serializers.BooleanField(read_only=True)
    institution_name = serializers.CharField(source='institution.name', read_only=True, default=None)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'role', 'role_display',
            'institution', 'institution_name', 'is_active', 'date_joined', 'permissions',
            'terms_accepted', 'accepted_terms_at', 'accepted_terms_version',
        ]
        read_only_fields = [
            'id', 'email', 'role', 'date_joined',
            'terms_accepted', 'accepted_terms_at', 'accepted_terms_version',
        ]

    def get_permissions(self, obj):
        return {
            'can_publish_own': obj.can_publish_own,
            'can_manage_catalog': obj.can_manage_catalog,
            'can_manage_users': obj.can_manage_users,
        }


class RegisterSerializer(serializers.Serializer):
    """Cadastro pela tela inicial: sempre cria um usuário Aluno."""

    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    # Consentimento livre e informado (LGPD, art. 8º): sem o aceite não há cadastro.
    accept_terms = serializers.BooleanField(write_only=True)

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Já existe uma conta com este e-mail.')
        return value

    def validate_accept_terms(self, value):
        if not value:
            raise serializers.ValidationError(
                'É preciso aceitar os Termos de Uso e a Política de Privacidade.'
            )
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'As senhas não conferem.'})
        password_validation.validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'].strip(),
            role=Role.STUDENT,
        )
        user.register_consent()
        user.save(update_fields=['accepted_terms_at', 'accepted_terms_version'])
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    # Mensagem sempre genérica, para não revelar se o e-mail existe.
    default_error_message = 'E-mail ou senha inválidos.'

    def validate(self, attrs):
        # authenticate() já recusa contas desativadas; a mensagem é a mesma de
        # senha errada, para não revelar quais e-mails existem.
        user = authenticate(
            request=self.context.get('request'),
            username=attrs['email'].lower().strip(),
            password=attrs['password'],
        )
        if user is None:
            raise serializers.ValidationError({'detail': self.default_error_message})
        attrs['user'] = user
        return attrs


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Edição do próprio perfil: somente o nome."""

    class Meta:
        model = User
        fields = ['name']

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Informe seu nome.')
        return value


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Senha atual incorreta.')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'As senhas não conferem.'})
        password_validation.validate_password(attrs['new_password'], self.context['request'].user)
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user


class AccountDeletionSerializer(serializers.Serializer):
    """Exclusão da própria conta (LGPD, art. 18, VI).

    Pede a senha e uma confirmação escrita, porque a operação é irreversível.
    """

    password = serializers.CharField(write_only=True)
    confirmation = serializers.CharField(write_only=True)

    EXPECTED_CONFIRMATION = 'EXCLUIR'

    def validate_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Senha incorreta.')
        return value

    def validate_confirmation(self, value):
        if value.strip().upper() != self.EXPECTED_CONFIRMATION:
            raise serializers.ValidationError(
                f'Digite {self.EXPECTED_CONFIRMATION} para confirmar a exclusão.'
            )
        return value


class ConsentSerializer(serializers.Serializer):
    """Aceite dos termos por quem se cadastrou antes da versão vigente."""

    accept_terms = serializers.BooleanField()

    def validate_accept_terms(self, value):
        if not value:
            raise serializers.ValidationError('É preciso aceitar para continuar.')
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.register_consent()
        user.save(update_fields=['accepted_terms_at', 'accepted_terms_version'])
        return user


class AdminUserSerializer(serializers.ModelSerializer):
    """Gestão de usuários pelo Administrador."""

    role_display = serializers.CharField(source='get_role_display', read_only=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    documents_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'role', 'role_display', 'institution',
            'is_active', 'date_joined', 'password', 'documents_count',
        ]
        read_only_fields = ['id', 'date_joined']

    def validate_email(self, value):
        value = value.lower().strip()
        queryset = User.objects.filter(email__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('Já existe uma conta com este e-mail.')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', '') or get_random_string(16)
        user = User.objects.create_user(password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', '')
        user = super().update(instance, validated_data)
        if password:
            password_validation.validate_password(password, user)
            user.set_password(password)
            user.save(update_fields=['password'])
        return user


def tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'access': str(refresh.access_token), 'refresh': str(refresh)}

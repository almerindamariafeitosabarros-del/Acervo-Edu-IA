from django.contrib.auth import authenticate, password_validation
from django.utils.crypto import get_random_string
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Role, User


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    institution_name = serializers.CharField(source='institution.name', read_only=True, default=None)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'role', 'role_display',
            'institution', 'institution_name', 'is_active', 'date_joined', 'permissions',
        ]
        read_only_fields = ['id', 'email', 'role', 'date_joined']

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

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Já existe uma conta com este e-mail.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'As senhas não conferem.'})
        password_validation.validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'].strip(),
            role=Role.STUDENT,
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    # Mensagem sempre genérica, para não revelar se o e-mail existe.
    default_error_message = 'E-mail ou senha inválidos.'

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get('request'),
            username=attrs['email'].lower().strip(),
            password=attrs['password'],
        )
        if user is None:
            raise serializers.ValidationError({'detail': self.default_error_message})
        if not user.is_active:
            raise serializers.ValidationError({'detail': 'Esta conta está desativada.'})
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

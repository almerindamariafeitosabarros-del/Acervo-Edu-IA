from django.db.models import Count
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TERMS_VERSION, User
from .permissions import IsAdmin
from .privacy import delete_user_account, export_user_data
from .serializers import (
    AccountDeletionSerializer,
    AdminUserSerializer,
    ChangePasswordSerializer,
    ConsentSerializer,
    LoginSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
    tokens_for_user,
)


class RegisterView(APIView):
    """Cadastro pela tela inicial. Cria um Aluno e já devolve os tokens."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'user': UserSerializer(user).data, **tokens_for_user(user)},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response({'user': UserSerializer(user).data, **tokens_for_user(user)})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Senha alterada com sucesso.'})


class ExportMyDataView(APIView):
    """GET /api/auth/me/export/ — baixa todos os dados do titular em JSON.

    Atende ao direito de acesso e de portabilidade (LGPD, art. 18, II e V).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        dados = export_user_data(request.user)
        dados['gerado_em'] = timezone.now().isoformat()
        resposta = JsonResponse(dados, json_dumps_params={'ensure_ascii': False, 'indent': 2})
        nome_arquivo = f'meus-dados-acervo-edu-ia-{timezone.now():%Y-%m-%d}.json'
        resposta['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
        return resposta


class DeleteMyAccountView(APIView):
    """POST /api/auth/me/delete/ — elimina a conta e todos os dados (art. 18, VI)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AccountDeletionSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        resumo = delete_user_account(request.user)
        return Response(
            {
                'detail': 'Sua conta e seus dados foram excluídos definitivamente.',
                **resumo,
            }
        )


class ConsentView(APIView):
    """Informa a versão vigente dos termos e registra um novo aceite."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                'version': TERMS_VERSION,
                'accepted': request.user.terms_accepted,
                'accepted_at': request.user.accepted_terms_at,
                'accepted_version': request.user.accepted_terms_version or None,
            }
        )

    def post(self, request):
        serializer = ConsentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class UserViewSet(viewsets.ModelViewSet):
    """Gestão de usuários — apenas Administrador."""

    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
    search_fields = ['name', 'email']
    filterset_fields = ['role', 'is_active', 'institution']
    ordering_fields = ['name', 'date_joined']

    def get_queryset(self):
        return User.objects.annotate(documents_count=Count('documents')).order_by('name')

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Ativa ou desativa a conta, sem permitir que o Admin desative a si mesmo."""
        user = self.get_object()
        if user.id == request.user.id:
            return Response(
                {'detail': 'Você não pode desativar a própria conta.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        return Response(AdminUserSerializer(user).data)

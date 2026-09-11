from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Role, User


class AuthTests(APITestCase):
    def test_cadastro_cria_aluno_e_devolve_tokens(self):
        response = self.client.post(
            reverse('auth-register'),
            {
                'name': 'Maria Silva',
                'email': 'Maria@Exemplo.com',
                'password': 'senhaSegura123',
                'password_confirm': 'senhaSegura123',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['role'], Role.STUDENT)
        self.assertEqual(response.data['user']['email'], 'maria@exemplo.com')

    def test_cadastro_com_senhas_diferentes_falha(self):
        response = self.client.post(
            reverse('auth-register'),
            {
                'name': 'Maria',
                'email': 'maria2@exemplo.com',
                'password': 'senhaSegura123',
                'password_confirm': 'outraSenha123',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalido_tem_mensagem_generica(self):
        User.objects.create_user(email='ana@exemplo.com', password='senhaSegura123', name='Ana')
        response = self.client.post(
            reverse('auth-login'),
            {'email': 'ana@exemplo.com', 'password': 'errada'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('E-mail ou senha inválidos.', str(response.data))

    def test_me_sem_login_retorna_401(self):
        response = self.client.get(reverse('auth-me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_com_login_retorna_usuario(self):
        user = User.objects.create_user(email='ana@exemplo.com', password='senhaSegura123', name='Ana')
        self.client.force_authenticate(user)
        response = self.client.get(reverse('auth-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'ana@exemplo.com')

    def test_troca_de_senha(self):
        user = User.objects.create_user(email='ana@exemplo.com', password='senhaSegura123', name='Ana')
        self.client.force_authenticate(user)
        response = self.client.post(
            reverse('auth-change-password'),
            {
                'current_password': 'senhaSegura123',
                'new_password': 'novaSenhaForte456',
                'new_password_confirm': 'novaSenhaForte456',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password('novaSenhaForte456'))


class UserManagementTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@exemplo.com', password='x', name='Admin', role=Role.ADMIN
        )
        self.aluno = User.objects.create_user(
            email='aluno@exemplo.com', password='x', name='Aluno', role=Role.STUDENT
        )

    def test_aluno_nao_lista_usuarios(self):
        self.client.force_authenticate(self.aluno)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_altera_perfil(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(
            f'/api/users/{self.aluno.id}/', {'role': Role.TEACHER}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.aluno.refresh_from_db()
        self.assertEqual(self.aluno.role, Role.TEACHER)

    def test_admin_nao_desativa_a_si_mesmo(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(f'/api/users/{self.admin.id}/toggle_active/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

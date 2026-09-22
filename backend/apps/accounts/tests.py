import json
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.ai.models import AIQuery
from apps.documents.models import Document

from .models import TERMS_VERSION, Role, User

TEMP_MEDIA = tempfile.mkdtemp()


class AuthTests(APITestCase):
    def test_cadastro_cria_aluno_e_devolve_tokens(self):
        response = self.client.post(
            reverse('auth-register'),
            {
                'name': 'Maria Silva',
                'email': 'Maria@Exemplo.com',
                'password': 'senhaSegura123',
                'password_confirm': 'senhaSegura123',
                'accept_terms': True,
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
                'accept_terms': True,
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

    def test_conta_desativada_nao_entra(self):
        User.objects.create_user(
            email='inativo@exemplo.com', password='senhaSegura123', name='Inativo', is_active=False
        )
        response = self.client.post(
            reverse('auth-login'),
            {'email': 'inativo@exemplo.com', 'password': 'senhaSegura123'},
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


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class LGPDTests(APITestCase):
    """Direitos do titular previstos na Lei 13.709/2018 (LGPD)."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.dados_cadastro = {
            'name': 'Joana Titular',
            'email': 'joana@exemplo.com',
            'password': 'senhaSegura123',
            'password_confirm': 'senhaSegura123',
            'accept_terms': True,
        }

    def test_cadastro_sem_aceite_e_recusado(self):
        dados = {**self.dados_cadastro, 'accept_terms': False}
        response = self.client.post(reverse('auth-register'), dados, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Termos de Uso', str(response.data))
        self.assertFalse(User.objects.filter(email='joana@exemplo.com').exists())

    def test_cadastro_registra_data_e_versao_do_consentimento(self):
        response = self.client.post(
            reverse('auth-register'), self.dados_cadastro, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        usuario = User.objects.get(email='joana@exemplo.com')
        self.assertIsNotNone(usuario.accepted_terms_at)
        self.assertEqual(usuario.accepted_terms_version, TERMS_VERSION)
        self.assertTrue(usuario.terms_accepted)
        self.assertTrue(response.data['user']['terms_accepted'])

    def test_consentimento_de_versao_antiga_nao_vale(self):
        usuario = User.objects.create_user(email='ana@t.com', password='x', name='Ana')
        usuario.register_consent()
        usuario.accepted_terms_version = '0.1'
        usuario.save()
        self.assertFalse(usuario.terms_accepted)

        self.client.force_authenticate(usuario)
        response = self.client.post(reverse('auth-consent'), {'accept_terms': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usuario.refresh_from_db()
        self.assertTrue(usuario.terms_accepted)

    def test_exportacao_traz_os_dados_do_titular(self):
        usuario = User.objects.create_user(
            email='ana@t.com', password='x', name='Ana Titular'
        )
        self.client.force_authenticate(usuario)
        response = self.client.get(reverse('auth-export-data'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('attachment', response['Content-Disposition'])

        conteudo = json.loads(response.content)
        self.assertEqual(conteudo['titular']['email'], 'ana@t.com')
        self.assertEqual(conteudo['titular']['nome'], 'Ana Titular')
        self.assertIn('documentos', conteudo)
        self.assertIn('consultas_ao_assistente', conteudo)

    def test_exportacao_exige_login(self):
        self.assertEqual(
            self.client.get(reverse('auth-export-data')).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_exclusao_exige_senha_e_confirmacao(self):
        usuario = User.objects.create_user(
            email='ana@t.com', password='senhaSegura123', name='Ana'
        )
        self.client.force_authenticate(usuario)

        sem_confirmacao = self.client.post(
            reverse('auth-delete-account'),
            {'password': 'senhaSegura123', 'confirmation': 'sim'},
            format='json',
        )
        self.assertEqual(sem_confirmacao.status_code, status.HTTP_400_BAD_REQUEST)

        senha_errada = self.client.post(
            reverse('auth-delete-account'),
            {'password': 'errada', 'confirmation': 'EXCLUIR'},
            format='json',
        )
        self.assertEqual(senha_errada.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.filter(email='ana@t.com').exists())

    def test_exclusao_remove_conta_documentos_e_historico(self):
        usuario = User.objects.create_user(
            email='ana@t.com', password='senhaSegura123', name='Ana'
        )
        documento = Document.objects.create(
            title='Material da Ana',
            owner=usuario,
            file=SimpleUploadedFile('m.txt', b'conteudo', content_type='text/plain'),
            original_filename='m.txt',
            file_size=8,
        )
        AIQuery.objects.create(user=usuario, document=documento, prompt='p', answer='r')

        self.client.force_authenticate(usuario)
        response = self.client.post(
            reverse('auth-delete-account'),
            {'password': 'senhaSegura123', 'confirmation': 'EXCLUIR'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['documentos_excluidos'], 1)
        self.assertFalse(User.objects.filter(email='ana@t.com').exists())
        self.assertEqual(Document.objects.filter(owner_id=usuario.id).count(), 0)
        self.assertEqual(AIQuery.objects.filter(user_id=usuario.id).count(), 0)

    def test_exclusao_nao_afeta_dados_de_outro_usuario(self):
        usuario = User.objects.create_user(
            email='ana@t.com', password='senhaSegura123', name='Ana'
        )
        outro = User.objects.create_user(email='outro@t.com', password='x', name='Outro')
        Document.objects.create(
            title='Material do outro',
            owner=outro,
            file=SimpleUploadedFile('o.txt', b'conteudo', content_type='text/plain'),
            original_filename='o.txt',
            file_size=8,
        )

        self.client.force_authenticate(usuario)
        self.client.post(
            reverse('auth-delete-account'),
            {'password': 'senhaSegura123', 'confirmation': 'EXCLUIR'},
            format='json',
        )
        self.assertTrue(User.objects.filter(email='outro@t.com').exists())
        self.assertEqual(Document.objects.filter(owner=outro).count(), 1)

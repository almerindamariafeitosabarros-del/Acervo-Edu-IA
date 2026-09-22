from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User

from .models import Category, Course, Institution, Subject


class AcademicsPermissionTests(APITestCase):
    def setUp(self):
        self.instituicao = Institution.objects.create(name='Instituto Teste', acronym='IT')
        self.curso = Course.objects.create(institution=self.instituicao, name='ADS')
        Subject.objects.create(course=self.curso, name='Banco de Dados')
        Category.objects.create(name='Apostila')

        self.aluno = User.objects.create_user(email='a@t.com', password='x', name='A', role=Role.STUDENT)
        self.gestor = User.objects.create_user(email='g@t.com', password='x', name='G', role=Role.MANAGER)
        self.admin = User.objects.create_user(email='ad@t.com', password='x', name='Ad', role=Role.ADMIN)

    def test_qualquer_usuario_autenticado_le_o_catalogo(self):
        self.client.force_authenticate(self.aluno)
        for rota in ['institutions', 'courses', 'subjects', 'categories', 'tags']:
            with self.subTest(rota=rota):
                response = self.client.get(f'/api/{rota}/')
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sem_login_retorna_401(self):
        self.assertEqual(
            self.client.get('/api/institutions/').status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_aluno_nao_cria_curso(self):
        self.client.force_authenticate(self.aluno)
        response = self.client.post(
            '/api/courses/', {'name': 'Novo', 'institution': self.instituicao.id}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_gestor_cria_curso_e_disciplina(self):
        self.client.force_authenticate(self.gestor)
        curso = self.client.post(
            '/api/courses/', {'name': 'Redes', 'institution': self.instituicao.id}, format='json'
        )
        self.assertEqual(curso.status_code, status.HTTP_201_CREATED)
        disciplina = self.client.post(
            '/api/subjects/', {'name': 'Redes I', 'course': curso.data['id']}, format='json'
        )
        self.assertEqual(disciplina.status_code, status.HTTP_201_CREATED)

    def test_gestor_nao_cria_instituicao(self):
        self.client.force_authenticate(self.gestor)
        response = self.client.post('/api/institutions/', {'name': 'Nova'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cria_instituicao(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post('/api/institutions/', {'name': 'Nova'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_filtro_de_disciplinas_por_curso(self):
        self.client.force_authenticate(self.aluno)
        response = self.client.get(f'/api/subjects/?course={self.curso.id}')
        self.assertEqual(len(response.data), 1)

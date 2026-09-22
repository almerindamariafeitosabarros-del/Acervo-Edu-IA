import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from apps.academics.models import Category, Course, Institution, Subject
from apps.accounts.models import Role, User

from .models import Document, Visibility

TEMP_MEDIA = tempfile.mkdtemp()


def arquivo(nome='material.pdf', conteudo=b'%PDF-1.4 conteudo de teste'):
    return SimpleUploadedFile(nome, conteudo, content_type='application/pdf')


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class DocumentTestBase(APITestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.instituicao = Institution.objects.create(name='Instituto Teste')
        self.curso = Course.objects.create(institution=self.instituicao, name='ADS')
        self.disciplina = Subject.objects.create(course=self.curso, name='Banco de Dados')
        self.categoria = Category.objects.create(name='Apostila')

        self.aluno = User.objects.create_user(
            email='aluno@t.com', password='x', name='Aluno', role=Role.STUDENT
        )
        self.professor = User.objects.create_user(
            email='prof@t.com', password='x', name='Professor', role=Role.TEACHER
        )
        self.gestor = User.objects.create_user(
            email='gestor@t.com', password='x', name='Gestor', role=Role.MANAGER
        )
        self.outro = User.objects.create_user(
            email='outro@t.com', password='x', name='Outro', role=Role.STUDENT
        )

    def criar_documento(self, owner=None, visibility=Visibility.PRIVATE, title='Documento'):
        documento = Document.objects.create(
            title=title,
            owner=owner or self.aluno,
            subject=self.disciplina,
            category=self.categoria,
            file=arquivo(),
            original_filename='material.pdf',
            file_size=26,
        )
        if visibility == Visibility.PUBLIC:
            documento.publish()
        return documento


class DocumentCrudTests(DocumentTestBase):
    def test_documento_novo_nasce_privado(self):
        self.client.force_authenticate(self.aluno)
        response = self.client.post(
            '/api/documents/mine/',
            {
                'title': 'Meu material',
                'description': 'teste',
                'subject': self.disciplina.id,
                'category': self.categoria.id,
                'file': arquivo(),
                'tags': 'prova,revisão',
            },
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['visibility'], Visibility.PRIVATE)
        self.assertCountEqual(response.data['tags'], ['prova', 'revisão'])

    def test_upload_recusa_extensao_invalida(self):
        self.client.force_authenticate(self.aluno)
        response = self.client.post(
            '/api/documents/mine/',
            {
                'title': 'Executável',
                'file': SimpleUploadedFile('virus.exe', b'MZ', content_type='application/exe'),
            },
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(MAX_UPLOAD_SIZE_BYTES=10, MAX_UPLOAD_SIZE_MB=0)
    def test_upload_recusa_arquivo_grande(self):
        self.client.force_authenticate(self.aluno)
        response = self.client.post(
            '/api/documents/mine/',
            {'title': 'Grande', 'file': arquivo(conteudo=b'x' * 100)},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_meus_documentos_lista_apenas_os_proprios(self):
        self.criar_documento(owner=self.aluno, title='Do aluno')
        self.criar_documento(owner=self.outro, title='Do outro')
        self.client.force_authenticate(self.aluno)
        response = self.client.get('/api/documents/mine/')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Do aluno')

    def test_sem_login_retorna_401(self):
        documento = self.criar_documento(visibility=Visibility.PUBLIC)
        self.assertEqual(
            self.client.get(f'/api/documents/{documento.id}/').status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(
            self.client.get('/api/documents/public/').status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class DocumentPermissionTests(DocumentTestBase):
    def test_documento_privado_de_outro_retorna_404(self):
        documento = self.criar_documento(owner=self.aluno)
        self.client.force_authenticate(self.outro)
        self.assertEqual(
            self.client.get(f'/api/documents/{documento.id}/').status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_arquivo_privado_de_outro_retorna_404(self):
        documento = self.criar_documento(owner=self.aluno)
        self.client.force_authenticate(self.outro)
        self.assertEqual(
            self.client.get(f'/api/documents/{documento.id}/file/').status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_dono_baixa_o_proprio_arquivo(self):
        documento = self.criar_documento(owner=self.aluno)
        self.client.force_authenticate(self.aluno)
        response = self.client.get(f'/api/documents/{documento.id}/file/?download=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        conteudo = b''.join(response.streaming_content)
        self.assertIn(b'conteudo de teste', conteudo)
        self.assertIn('attachment', response['Content-Disposition'])

    def test_gestor_acessa_documento_privado_de_qualquer_um(self):
        documento = self.criar_documento(owner=self.aluno)
        self.client.force_authenticate(self.gestor)
        self.assertEqual(
            self.client.get(f'/api/documents/{documento.id}/').status_code,
            status.HTTP_200_OK,
        )

    def test_outro_usuario_nao_edita_nem_exclui(self):
        documento = self.criar_documento(owner=self.aluno, visibility=Visibility.PUBLIC)
        self.client.force_authenticate(self.outro)
        resposta_edicao = self.client.patch(
            f'/api/documents/{documento.id}/', {'title': 'Invadido'}, format='multipart'
        )
        self.assertEqual(resposta_edicao.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            self.client.delete(f'/api/documents/{documento.id}/').status_code,
            status.HTTP_403_FORBIDDEN,
        )


class PublicationTests(DocumentTestBase):
    def test_aluno_nao_publica(self):
        documento = self.criar_documento(owner=self.aluno)
        self.client.force_authenticate(self.aluno)
        response = self.client.post(f'/api/documents/{documento.id}/publish/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        documento.refresh_from_db()
        self.assertEqual(documento.visibility, Visibility.PRIVATE)

    def test_professor_publica_e_despublica_o_proprio(self):
        documento = self.criar_documento(owner=self.professor)
        self.client.force_authenticate(self.professor)

        publicar = self.client.post(f'/api/documents/{documento.id}/publish/')
        self.assertEqual(publicar.status_code, status.HTTP_200_OK)
        documento.refresh_from_db()
        self.assertEqual(documento.visibility, Visibility.PUBLIC)
        self.assertIsNotNone(documento.published_at)

        # Publicado aparece no acervo para outro usuário.
        self.client.force_authenticate(self.outro)
        acervo = self.client.get('/api/documents/public/')
        self.assertEqual(acervo.data['count'], 1)

        # Ao despublicar, some do acervo.
        self.client.force_authenticate(self.professor)
        self.client.post(f'/api/documents/{documento.id}/unpublish/')
        self.client.force_authenticate(self.outro)
        acervo = self.client.get('/api/documents/public/')
        self.assertEqual(acervo.data['count'], 0)

    def test_professor_nao_publica_documento_de_outro(self):
        documento = self.criar_documento(owner=self.aluno)
        self.client.force_authenticate(self.professor)
        response = self.client.post(f'/api/documents/{documento.id}/publish/')
        self.assertIn(
            response.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)
        )

    def test_gestor_publica_documento_de_outro(self):
        documento = self.criar_documento(owner=self.aluno)
        self.client.force_authenticate(self.gestor)
        response = self.client.post(f'/api/documents/{documento.id}/publish/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_busca_e_filtros_do_acervo(self):
        self.criar_documento(owner=self.professor, visibility=Visibility.PUBLIC, title='Cálculo I')
        self.criar_documento(owner=self.professor, visibility=Visibility.PUBLIC, title='Redes')
        self.client.force_authenticate(self.aluno)

        busca = self.client.get('/api/documents/public/?search=Cálculo')
        self.assertEqual(busca.data['count'], 1)

        filtro = self.client.get(f'/api/documents/public/?institution={self.instituicao.id}')
        self.assertEqual(filtro.data['count'], 2)

        vazio = self.client.get('/api/documents/public/?category=9999')
        self.assertEqual(vazio.data['count'], 0)


class PaginationTests(DocumentTestBase):
    def test_pagina_padrao_e_tamanho_ajustavel(self):
        for indice in range(15):
            self.criar_documento(
                owner=self.professor, visibility=Visibility.PUBLIC, title=f'Material {indice}'
            )
        self.client.force_authenticate(self.aluno)

        padrao = self.client.get('/api/documents/public/')
        self.assertEqual(padrao.data['count'], 15)
        self.assertEqual(len(padrao.data['results']), 12)

        segunda = self.client.get('/api/documents/public/?page=2')
        self.assertEqual(len(segunda.data['results']), 3)

        # A tela do assistente pede uma página maior para montar o seletor.
        maior = self.client.get('/api/documents/public/?page_size=100')
        self.assertEqual(len(maior.data['results']), 15)

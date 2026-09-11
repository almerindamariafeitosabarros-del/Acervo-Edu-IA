import io
import shutil
import tempfile
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User
from apps.documents.models import Document, Visibility

from .extractors import TextExtractionError, extract_text
from .models import AIQuery
from .services import AIUnavailableError, truncate

TEMP_MEDIA = tempfile.mkdtemp()

CONTEUDO_TXT = b'Conteudo do material de teste sobre bancos de dados relacionais.'


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class AITestBase(APITestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.aluno = User.objects.create_user(
            email='aluno@t.com', password='x', name='Aluno', role=Role.STUDENT
        )
        self.outro = User.objects.create_user(
            email='outro@t.com', password='x', name='Outro', role=Role.STUDENT
        )
        self.documento = Document.objects.create(
            title='Material',
            owner=self.aluno,
            file=SimpleUploadedFile('material.txt', CONTEUDO_TXT, content_type='text/plain'),
            original_filename='material.txt',
            file_size=len(CONTEUDO_TXT),
        )


class ExtractorTests(AITestBase):
    def test_extrai_texto_de_txt(self):
        texto = extract_text(io.BytesIO(CONTEUDO_TXT), 'material.txt')
        self.assertIn('bancos de dados', texto)

    def test_arquivo_sem_texto_levanta_erro(self):
        with self.assertRaises(TextExtractionError):
            extract_text(io.BytesIO(b'   '), 'vazio.txt')

    def test_formato_nao_suportado(self):
        with self.assertRaises(TextExtractionError):
            extract_text(io.BytesIO(b'conteudo'), 'apresentacao.pptx')

    def test_truncagem_respeita_limite(self):
        texto, truncado = truncate('a' * 100, max_chars=10)
        self.assertEqual(len(texto), 10)
        self.assertTrue(truncado)

        texto, truncado = truncate('abc', max_chars=10)
        self.assertFalse(truncado)


class AskTests(AITestBase):
    @patch('apps.ai.views.ask_ollama', return_value=('Resposta da IA.', 1200, 'qwen2.5:7b'))
    def test_pergunta_sobre_documento_proprio(self, mock_ask):
        self.client.force_authenticate(self.aluno)
        response = self.client.post(
            '/api/ai/ask/',
            {'document_id': self.documento.id, 'prompt': 'Resuma este material'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['answer'], 'Resposta da IA.')
        self.assertEqual(AIQuery.objects.filter(user=self.aluno).count(), 1)
        # O texto do documento chegou ao serviço.
        self.assertIn('bancos de dados', mock_ask.call_args[0][0])

    @patch('apps.ai.views.ask_ollama')
    def test_documento_privado_de_outro_retorna_404(self, mock_ask):
        self.client.force_authenticate(self.outro)
        response = self.client.post(
            '/api/ai/ask/',
            {'document_id': self.documento.id, 'prompt': 'Resuma'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        mock_ask.assert_not_called()

    @patch('apps.ai.views.ask_ollama', return_value=('Resposta.', 10, 'qwen2.5:7b'))
    def test_documento_publico_pode_ser_consultado_por_outro(self, mock_ask):
        self.documento.publish()
        self.client.force_authenticate(self.outro)
        response = self.client.post(
            '/api/ai/ask/',
            {'document_id': self.documento.id, 'prompt': 'Resuma'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('apps.ai.views.ask_ollama', return_value=('Resposta.', 10, 'qwen2.5:7b'))
    def test_arquivo_avulso_nao_entra_no_acervo(self, mock_ask):
        self.client.force_authenticate(self.aluno)
        total_antes = Document.objects.count()
        response = self.client.post(
            '/api/ai/ask/',
            {
                'file': SimpleUploadedFile('avulso.txt', CONTEUDO_TXT, content_type='text/plain'),
                'prompt': 'Do que trata?',
            },
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Document.objects.count(), total_antes)
        self.assertEqual(response.data['uploaded_filename'], 'avulso.txt')

    @patch('apps.ai.views.ask_ollama', side_effect=AIUnavailableError('Assistente indisponível no momento.'))
    def test_ollama_desligado_retorna_503(self, mock_ask):
        self.client.force_authenticate(self.aluno)
        response = self.client.post(
            '/api/ai/ask/',
            {'document_id': self.documento.id, 'prompt': 'Resuma'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn('indisponível', response.data['detail'])
        self.assertEqual(AIQuery.objects.count(), 0)

    @override_settings(AI_MAX_CHARS=20)
    @patch('apps.ai.views.ask_ollama', return_value=('Resposta.', 10, 'qwen2.5:7b'))
    def test_documento_grande_avisa_truncagem(self, mock_ask):
        self.client.force_authenticate(self.aluno)
        response = self.client.post(
            '/api/ai/ask/',
            {'document_id': self.documento.id, 'prompt': 'Resuma'},
            format='json',
        )
        self.assertTrue(response.data['truncated'])
        self.assertTrue(response.data['notice'])
        self.assertEqual(len(mock_ask.call_args[0][0]), 20)

    def test_pergunta_sem_documento_nem_arquivo_falha(self):
        self.client.force_authenticate(self.aluno)
        response = self.client.post('/api/ai/ask/', {'prompt': 'Resuma'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sem_login_retorna_401(self):
        response = self.client.post('/api/ai/ask/', {'prompt': 'Resuma'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class HistoryTests(AITestBase):
    def test_historico_mostra_apenas_do_usuario(self):
        AIQuery.objects.create(user=self.aluno, document=self.documento, prompt='p1', answer='r1')
        AIQuery.objects.create(user=self.outro, document=None, prompt='p2', answer='r2')
        self.client.force_authenticate(self.aluno)
        response = self.client.get('/api/ai/history/')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['prompt'], 'p1')

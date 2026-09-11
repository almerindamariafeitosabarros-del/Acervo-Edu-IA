from django.conf import settings
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.documents.models import Document
from apps.documents.serializers import validate_uploaded_file

from .extractors import TextExtractionError, extract_text
from .models import AIQuery
from .serializers import AIQuerySerializer, AskSerializer
from .services import AIUnavailableError, ask_ollama, truncate

TRUNCATED_NOTICE = (
    'O documento é grande: a resposta considerou apenas o início do conteúdo '
    f'(primeiros {settings.AI_MAX_CHARS} caracteres).'
)


class AskView(APIView):
    """POST /api/ai/ask/ — pergunta sobre um documento escolhido."""

    def post(self, request):
        serializer = AskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        document = None
        uploaded_filename = ''

        if data.get('document_id'):
            document = Document.objects.filter(pk=data['document_id']).first()
            # Documento inexistente ou sem acesso respondem igual: 404.
            if document is None or not document.can_be_viewed_by(request.user):
                return Response(
                    {'detail': 'Documento não encontrado.'}, status=status.HTTP_404_NOT_FOUND
                )
            source_file = document.file
            filename = document.original_filename or document.file.name
        else:
            uploaded = data['file']
            try:
                validate_uploaded_file(uploaded)
            except Exception as exc:  # ValidationError do DRF
                return Response({'file': exc.detail}, status=status.HTTP_400_BAD_REQUEST)
            source_file = uploaded
            filename = uploaded.name
            uploaded_filename = uploaded.name[:255]

        try:
            handle = source_file.open('rb') if document else source_file
            handle.seek(0)
            try:
                text = extract_text(handle, filename)
            finally:
                handle.close()
        except TextExtractionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except FileNotFoundError:
            return Response(
                {'detail': 'Arquivo do documento não encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        text, was_truncated = truncate(text)

        try:
            answer, elapsed_ms, model = ask_ollama(text, data['prompt'])
        except AIUnavailableError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        query = AIQuery.objects.create(
            user=request.user,
            document=document,
            uploaded_filename=uploaded_filename,
            prompt=data['prompt'],
            answer=answer,
            model=model,
            response_time_ms=elapsed_ms,
            truncated=was_truncated,
        )
        payload = AIQuerySerializer(query).data
        payload['notice'] = TRUNCATED_NOTICE if was_truncated else ''
        return Response(payload, status=status.HTTP_201_CREATED)


class HistoryView(ListAPIView):
    """GET /api/ai/history/ — histórico de perguntas do próprio usuário."""

    serializer_class = AIQuerySerializer
    filterset_fields = ['document']
    search_fields = ['prompt', 'answer']

    def get_queryset(self):
        return AIQuery.objects.filter(user=self.request.user).select_related('document')


class AIStatusView(APIView):
    """Informa qual modelo está configurado (usado só para exibição)."""

    def get(self, request):
        return Response(
            {
                'model': settings.OLLAMA_MODEL,
                'max_chars': settings.AI_MAX_CHARS,
                'timeout_seconds': settings.AI_TIMEOUT_SECONDS,
            }
        )

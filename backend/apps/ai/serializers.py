from rest_framework import serializers

from .models import AIQuery


class AIQuerySerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source='document_label', read_only=True)

    class Meta:
        model = AIQuery
        fields = [
            'id', 'document', 'document_title', 'uploaded_filename',
            'prompt', 'answer', 'model', 'response_time_ms', 'truncated', 'created_at',
        ]


class AskSerializer(serializers.Serializer):
    """Pergunta sobre um documento do acervo (document_id) ou um arquivo avulso."""

    document_id = serializers.IntegerField(required=False)
    file = serializers.FileField(required=False)
    prompt = serializers.CharField()

    def validate_prompt(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Escreva sua pergunta.')
        return value

    def validate(self, attrs):
        if not attrs.get('document_id') and not attrs.get('file'):
            raise serializers.ValidationError(
                {'document_id': 'Escolha um documento ou envie um arquivo.'}
            )
        return attrs

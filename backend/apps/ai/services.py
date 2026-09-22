"""Integração com o Ollama rodando na máquina local."""

import time

import requests
from django.conf import settings

SYSTEM_PROMPT = (
    'Responda em português do Brasil usando apenas o conteúdo do documento. '
    'Se a informação não estiver no documento, diga isso.'
)

UNAVAILABLE_MESSAGE = 'Assistente indisponível no momento.'


class AIUnavailableError(Exception):
    """O Ollama não respondeu (desligado, sem o modelo ou tempo esgotado)."""


def truncate(text, max_chars=None):
    """Corta o texto no limite configurado. Devolve (texto, foi_truncado)."""
    limit = max_chars or settings.AI_MAX_CHARS
    if len(text) <= limit:
        return text, False
    return text[:limit], True


def build_prompt(document_text, question):
    return (
        'Conteúdo do documento:\n'
        '"""\n'
        f'{document_text}\n'
        '"""\n\n'
        f'Pergunta do usuário: {question}'
    )


def ask_ollama(document_text, question):
    """Envia o texto e a pergunta ao Ollama. Devolve (resposta, tempo_ms, modelo)."""
    payload = {
        'model': settings.OLLAMA_MODEL,
        'system': SYSTEM_PROMPT,
        'prompt': build_prompt(document_text, question),
        'stream': False,
    }
    started = time.monotonic()
    try:
        response = requests.post(
            f'{settings.OLLAMA_URL}/api/generate',
            json=payload,
            timeout=settings.AI_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise AIUnavailableError(UNAVAILABLE_MESSAGE) from exc

    elapsed_ms = int((time.monotonic() - started) * 1000)
    answer = (data.get('response') or '').strip()
    if not answer:
        raise AIUnavailableError(UNAVAILABLE_MESSAGE)
    return answer, elapsed_ms, settings.OLLAMA_MODEL

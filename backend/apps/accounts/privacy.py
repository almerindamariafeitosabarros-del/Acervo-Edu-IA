"""Direitos do titular dos dados (LGPD, Lei 13.709/2018, art. 18).

Reúne as operações de acesso, portabilidade e eliminação dos dados pessoais.
"""

from django.db import transaction

from apps.ai.models import AIQuery
from apps.documents.models import Document


def export_user_data(user):
    """Devolve, em formato legível por máquina, todos os dados do titular.

    Atende aos incisos II (acesso) e V (portabilidade) do art. 18 da LGPD.
    """
    documentos = (
        Document.objects.filter(owner=user)
        .select_related('category', 'subject', 'subject__course', 'subject__course__institution')
        .prefetch_related('tags')
    )
    consultas = AIQuery.objects.filter(user=user).select_related('document')

    return {
        'gerado_em': None,  # preenchido pela view com a data da exportação
        'titular': {
            'nome': user.name,
            'email': user.email,
            'perfil': user.get_role_display(),
            'instituicao': user.institution.name if user.institution else None,
            'conta_ativa': user.is_active,
            'cadastrado_em': user.date_joined.isoformat(),
            'consentimento': {
                'aceito_em': user.accepted_terms_at.isoformat() if user.accepted_terms_at else None,
                'versao_dos_termos': user.accepted_terms_version or None,
            },
        },
        'documentos': [
            {
                'titulo': documento.title,
                'descricao': documento.description,
                'autor_do_material': documento.material_author,
                'instituicao': (
                    documento.subject.course.institution.name if documento.subject else None
                ),
                'curso': documento.subject.course.name if documento.subject else None,
                'disciplina': documento.subject.name if documento.subject else None,
                'categoria': documento.category.name if documento.category else None,
                'tags': [tag.name for tag in documento.tags.all()],
                'arquivo': documento.original_filename,
                'tamanho_bytes': documento.file_size,
                'visibilidade': documento.get_visibility_display(),
                'publicado_em': (
                    documento.published_at.isoformat() if documento.published_at else None
                ),
                'criado_em': documento.created_at.isoformat(),
            }
            for documento in documentos
        ],
        'consultas_ao_assistente': [
            {
                'documento': consulta.document_label,
                'pergunta': consulta.prompt,
                'resposta': consulta.answer,
                'modelo': consulta.model,
                'tempo_de_resposta_ms': consulta.response_time_ms,
                'data': consulta.created_at.isoformat(),
            }
            for consulta in consultas
        ],
        'observacao': (
            'Os arquivos enviados não cabem neste relatório. Baixe cada documento '
            'pela tela Meus Documentos antes de excluir a conta.'
        ),
    }


@transaction.atomic
def delete_user_account(user):
    """Elimina a conta e todos os dados pessoais do titular (art. 18, VI).

    Remove os arquivos do disco antes de apagar os registros, para não deixar
    conteúdo órfão em MEDIA_ROOT. Devolve um resumo do que foi eliminado.
    """
    documentos = Document.objects.filter(owner=user)
    total_documentos = documentos.count()
    total_consultas = AIQuery.objects.filter(user=user).count()

    for documento in documentos:
        if documento.file:
            documento.file.delete(save=False)

    # Os demais registros saem por cascata (documentos e consultas de IA).
    user.delete()

    return {
        'documentos_excluidos': total_documentos,
        'consultas_excluidas': total_consultas,
    }

"""Popula o banco com dados de exemplo para demonstrar a plataforma."""

import io

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.academics.models import Category, Course, Institution, Subject, Tag
from apps.accounts.models import Role, User
from apps.documents.models import Document, Visibility

SENHA_PADRAO = 'acervo123'

USUARIOS = [
    ('Administrador do Sistema', 'admin@acervo.edu', Role.ADMIN),
    ('Gabriela Gestora', 'gestor@acervo.edu', Role.MANAGER),
    ('Paulo Professor', 'professor@acervo.edu', Role.TEACHER),
    ('Ana Aluna', 'aluno@acervo.edu', Role.STUDENT),
]

CATEGORIAS = [
    ('Apostila', 'Material de estudo completo'),
    ('Slide', 'Apresentação de aula'),
    ('Artigo', 'Artigo científico ou de divulgação'),
    ('Exercícios', 'Listas e provas resolvidas'),
]

ESTRUTURA = {
    'Instituto Federal de Educação': {
        'sigla': 'IFE',
        'cursos': {
            'Análise e Desenvolvimento de Sistemas': [
                'Algoritmos e Programação',
                'Banco de Dados',
                'Engenharia de Software',
            ],
            'Redes de Computadores': ['Redes I', 'Segurança da Informação'],
        },
    },
    'Universidade Estadual': {
        'sigla': 'UE',
        'cursos': {
            'Pedagogia': ['Didática', 'Psicologia da Educação'],
            'Matemática': ['Cálculo I', 'Álgebra Linear'],
        },
    },
}


def texto_exemplo(titulo, disciplina):
    return (
        f'{titulo}\n'
        f'Disciplina: {disciplina}\n\n'
        'Este é um material de exemplo criado pelo comando seed_demo do Acervo Edu IA.\n'
        'Ele existe para demonstrar o cadastro de documentos, o Acervo Público e o '
        'Assistente de IA local.\n\n'
        'Capítulo 1 — Conceitos iniciais\n'
        'Um documento educacional reúne o conteúdo trabalhado em aula: definições, '
        'exemplos resolvidos e exercícios propostos.\n\n'
        'Capítulo 2 — Aplicação prática\n'
        'Na prática, o professor publica o material no acervo e os alunos podem '
        'consultar, baixar e pedir um resumo ao assistente de IA.\n\n'
        'Capítulo 3 — Avaliação\n'
        'A avaliação considera a participação nas atividades e a entrega dos '
        'exercícios propostos ao final de cada capítulo.\n'
    )


class Command(BaseCommand):
    help = 'Cria usuários, catálogo acadêmico e documentos de exemplo.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Remove os documentos de exemplo antes de recriar.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['limpar']:
            Document.objects.filter(owner__email__endswith='@acervo.edu').delete()
            self.stdout.write('Documentos de exemplo removidos.')

        instituicoes = {}
        disciplinas = []
        for nome, dados in ESTRUTURA.items():
            instituicao, _ = Institution.objects.get_or_create(
                name=nome, defaults={'acronym': dados['sigla']}
            )
            instituicoes[nome] = instituicao
            for nome_curso, nomes_disciplinas in dados['cursos'].items():
                curso, _ = Course.objects.get_or_create(institution=instituicao, name=nome_curso)
                for nome_disciplina in nomes_disciplinas:
                    disciplina, _ = Subject.objects.get_or_create(course=curso, name=nome_disciplina)
                    disciplinas.append(disciplina)

        categorias = [
            Category.objects.get_or_create(name=nome, defaults={'description': descricao})[0]
            for nome, descricao in CATEGORIAS
        ]

        tags = [
            Tag.objects.get_or_create(name=nome)[0]
            for nome in ['introdução', 'revisão', 'prova', 'prática', 'teoria']
        ]

        usuarios = {}
        instituicao_padrao = instituicoes['Instituto Federal de Educação']
        for nome, email, perfil in USUARIOS:
            usuario = User.objects.filter(email=email).first()
            if usuario is None:
                usuario = User.objects.create_user(
                    email=email,
                    password=SENHA_PADRAO,
                    name=nome,
                    role=perfil,
                    institution=instituicao_padrao,
                )
                usuario.register_consent()
                campos = ['accepted_terms_at', 'accepted_terms_version']
                if perfil == Role.ADMIN:
                    usuario.is_staff = True
                    usuario.is_superuser = True
                    campos += ['is_staff', 'is_superuser']
                usuario.save(update_fields=campos)
            usuarios[perfil] = usuario

        professor = usuarios[Role.TEACHER]
        aluno = usuarios[Role.STUDENT]

        documentos = [
            ('Apostila de Algoritmos', professor, Visibility.PUBLIC),
            ('Slides de Banco de Dados', professor, Visibility.PUBLIC),
            ('Lista de Exercícios de Cálculo I', professor, Visibility.PUBLIC),
            ('Resumo de Engenharia de Software', professor, Visibility.COMMUNITY),
            ('Minhas anotações de Didática', aluno, Visibility.COMMUNITY),
        ]

        criados = 0
        for indice, (titulo, dono, visibilidade) in enumerate(documentos):
            if Document.objects.filter(title=titulo, owner=dono).exists():
                continue
            disciplina = disciplinas[indice % len(disciplinas)]
            categoria = categorias[indice % len(categorias)]
            conteudo = texto_exemplo(titulo, disciplina.name)
            documento = Document(
                title=titulo,
                description=f'Material de exemplo de {disciplina.name}.',
                material_author=dono.name,
                subject=disciplina,
                category=categoria,
                owner=dono,
                original_filename=f'{titulo.lower().replace(" ", "-")}.txt',
                file_size=len(conteudo.encode('utf-8')),
            )
            documento.file.save(
                documento.original_filename,
                ContentFile(conteudo.encode('utf-8')),
                save=False,
            )
            documento.save()
            documento.tags.set(tags[indice % len(tags)::2])
            if visibilidade == Visibility.PUBLIC:
                documento.publish()
            criados += 1

        self.stdout.write(self.style.SUCCESS(
            f'Dados de exemplo prontos: {len(usuarios)} usuários, '
            f'{len(disciplinas)} disciplinas, {criados} documentos novos.'
        ))
        self.stdout.write('')
        self.stdout.write('Contas de teste (senha: %s):' % SENHA_PADRAO)
        for nome, email, perfil in USUARIOS:
            self.stdout.write(f'  {Role(perfil).label:15} {email}')

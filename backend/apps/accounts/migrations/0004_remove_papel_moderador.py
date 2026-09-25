"""Remove o papel Moderador e as tabelas do Mural Público.

O Mural foi retirado do projeto; com ele saem o perfil que existia apenas para
moderá-lo e as tabelas do app `mural`. Contas que estavam como Moderador viram
Aluno, para não ficarem com um perfil que o sistema não reconhece mais.
"""

from django.db import migrations, models


def moderador_vira_aluno(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    User.objects.filter(role='moderator').update(role='student')


def sem_volta(apps, schema_editor):
    """Não há como saber quais contas eram Moderador; a reversão não restaura."""


# As tabelas saem na ordem inversa das dependências: primeiro as que apontam
# para outras. IF EXISTS mantém a migração segura em bancos novos, onde o
# Mural nunca chegou a existir.
TABELAS_DO_MURAL = [
    'mural_muralreport',
    'mural_muralattachment',
    'mural_muralpost',
]


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_user_role'),
    ]

    operations = [
        migrations.RunPython(moderador_vira_aluno, sem_volta),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[
                    ('student', 'Aluno'),
                    ('teacher', 'Professor'),
                    ('manager', 'Gestor'),
                    ('admin', 'Administrador'),
                ],
                default='student',
                max_length=20,
                verbose_name='perfil',
            ),
        ),
        migrations.RunSQL(
            sql=[f'DROP TABLE IF EXISTS {tabela};' for tabela in TABELAS_DO_MURAL],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # O app `mural` não existe mais, então suas migrações aplicadas viram
        # registro órfão em django_migrations. Removemos para o histórico ficar
        # coerente com o código.
        migrations.RunSQL(
            sql="DELETE FROM django_migrations WHERE app = 'mural';",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

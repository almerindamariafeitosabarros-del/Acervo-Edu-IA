"""
Configuracoes do projeto Acervo Edu IA.

Todos os segredos e parametros de ambiente vem do arquivo .env na raiz do
repositorio (veja .env.example).
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# BASE_DIR = .../backend ; REPO_DIR = raiz do repositorio
BASE_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = BASE_DIR.parent

load_dotenv(REPO_DIR / '.env')


def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


def env_int(name, default):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return int(default)


def env_list(name, default=''):
    raw = os.getenv(name, default) or ''
    return [item.strip() for item in raw.split(',') if item.strip()]


SECRET_KEY = os.getenv('SECRET_KEY', 'insecure-dev-key-troque-no-env')

DEBUG = env_bool('DEBUG', True)

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceiros
    'rest_framework',
    'django_filters',
    'corsheaders',

    # Apps do projeto
    'apps.accounts',
    'apps.academics',
    'apps.documents',
    'apps.ai',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'acervo_edu_ia.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'acervo_edu_ia.wsgi.application'
ASGI_APPLICATION = 'acervo_edu_ia.asgi.application'


# Banco de dados: PostgreSQL (Docker Compose). USE_SQLITE=True facilita rodar
# testes e demonstracoes sem Docker.
if env_bool('USE_SQLITE', False):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'acervo_edu_ia'),
            'USER': os.getenv('POSTGRES_USER', 'acervo'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'acervo'),
            'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
        }
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Fortaleza'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Arquivos enviados nunca sao servidos por URL publica: o acesso passa sempre
# por /api/documents/{id}/file/ (ver apps.documents.views).
MEDIA_ROOT = BASE_DIR / 'media'
# MEDIA_URL existe apenas para o Django; nenhuma rota serve MEDIA_ROOT.
MEDIA_URL = '/media-interno/'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env_int('ACCESS_TOKEN_LIFETIME_MINUTES', 60)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env_int('REFRESH_TOKEN_LIFETIME_DAYS', 7)),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS liberado apenas para a origem do frontend.
CORS_ALLOWED_ORIGINS = env_list('FRONTEND_ORIGIN', 'http://localhost:5173')
CORS_ALLOW_CREDENTIALS = False

CSRF_TRUSTED_ORIGINS = list(CORS_ALLOWED_ORIGINS)


# Regras de upload
MAX_UPLOAD_SIZE_MB = env_int('MAX_UPLOAD_SIZE_MB', 25)
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_UPLOAD_EXTENSIONS = ['pdf', 'docx', 'pptx', 'txt']

# Assistente de IA local (Ollama)
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434').rstrip('/')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')
AI_MAX_CHARS = env_int('AI_MAX_CHARS', 12000)
AI_TIMEOUT_SECONDS = env_int('AI_TIMEOUT_SECONDS', 120)


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

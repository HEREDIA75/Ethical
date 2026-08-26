import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Configurações de Segurança lidas dinamicamente
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-chave-padrao-segura")
DEBUG = os.getenv("DEBUG", "False") == "True"

# Permite acesso ao Railway e conexões locais
ALLOWED_HOSTS = ["*"]

# Aplicações instaladas
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Libs de terceiros
    "corsheaders",
    # Apps do projeto
    "gestao",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Habilita suporte a CORS
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

# Permite requisições de origens externas (necessário para o Vue.js em dev)
CORS_ALLOW_ALL_ORIGINS = True

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Configuração Dinâmica do Banco de Dados MySQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQLDATABASE", os.getenv("MYSQL_DATABASE", "railway")),
        "USER": os.getenv("MYSQLUSER", os.getenv("MYSQL_USER", "root")),
        "PASSWORD": os.getenv("MYSQLPASSWORD", os.getenv("MYSQL_PASSWORD", "")),
        "HOST": os.getenv("MYSQLHOST", os.getenv("MYSQL_HOST", "localhost")),
        "PORT": os.getenv("MYSQLPORT", os.getenv("MYSQL_PORT", "3306")),
    }
}

# Validação de Senhas
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internacionalização ajustada para o Brasil
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# Arquivos Estáticos
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Necessário se usar painel admin ou formulários
CSRF_TRUSTED_ORIGINS = [
    "https://*.railway.app",
    "https://*.up.railway.app",
]

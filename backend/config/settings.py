import os
from pathlib import Path
from datetime import timedelta
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-key-change-it')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# ALLOWED_HOSTS - добавляем 'backend' для Docker сети и поддержку ngrok
_allowed_hosts = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')
if 'backend' not in _allowed_hosts:
    _allowed_hosts.append('backend')

# Добавляем поддержку ngrok доменов (для разработки через Telegram Mini App)
# Проверяем, есть ли ngrok домены в переменной окружения
_ngrok_hosts = config('NGROK_HOSTS', default='').split(',')
if _ngrok_hosts and _ngrok_hosts[0]:
    _allowed_hosts.extend([h.strip() for h in _ngrok_hosts if h.strip()])

# В DEBUG режиме также разрешаем все ngrok домены автоматически
if DEBUG:
    # Разрешаем все хосты в DEBUG режиме (для разработки)
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = _allowed_hosts


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    
    # Local apps
    'apps.users',
    'apps.organizations',
    'apps.products',
    'apps.orders',
    'apps.iiko_integration',
    'apps.website',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware', # Отключаем для Telegram
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DB_NAME = config('DB_NAME', default='iiko_delivery')
DB_USER = config('DB_USER', default='postgres')
DB_PASSWORD = config('DB_PASSWORD', default='postgres')
DB_HOST = config('DB_HOST', default='db')
DB_PORT = config('DB_PORT', default='5432')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'users.User'


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Asia/Almaty'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=90),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# Swagger Configuration
SPECTACULAR_SETTINGS = {
    'TITLE': 'TG Delivery API',
    'DESCRIPTION': 'API для сервиса доставки через Telegram Mini App с интеграцией iiko',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://tg-redis:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://tg-redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Celery Beat Schedule - периодические задачи
CELERY_BEAT_SCHEDULE = {
    'sync-stop-lists': {
        'task': 'apps.products.tasks.sync_all_terminals_stop_lists',
        'schedule': 300.0,  # Каждые 5 минут проверяем терминалы и обновляем стоп-листы
    },
}

# Стоп-лист: глобальное «рабочее» окно (часовой пояс сервера = TIME_ZONE, например Asia/Almaty +5).
# Вне этого окна запросы на обновление стоп-листа не отправляются.
# Формат: 'HH:mm'. Если не задано — проверка не выполняется (поведение по умолчанию).
STOP_LIST_SYNC_WORKING_START = config('STOP_LIST_SYNC_WORKING_START', default='08:00')
STOP_LIST_SYNC_WORKING_END = config('STOP_LIST_SYNC_WORKING_END', default='23:59')

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:5173,http://localhost:3000').split(',')
CORS_ALLOW_CREDENTIALS = True

# Telegram
# TELEGRAM_BOT_TOKEN и TELEGRAM_BOT_USERNAME больше не используются на уровне settings
# Токены ботов теперь хранятся в модели Organization (bot_token, bot_username)
# Это позволяет каждой организации иметь свой собственный бот
TELEGRAM_CONTACT_SECRET = config('TELEGRAM_CONTACT_SECRET', default='')

# iiko API
IIKO_API_BASE_URL = config('IIKO_API_BASE_URL', default='https://api-ru.iiko.services/api/1')

# Security settings for production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_SSL_REDIRECT = False

# Доверенные домены для CSRF (обязательно для работы за прокси)
_csrf_origins = [
    'https://b2b-delivery.mevent.kz',
    'http://localhost:3005',
    'http://127.0.0.1:3005',
]
_csrf_extra = config('CSRF_TRUSTED_ORIGINS', default='').split(',')
CSRF_TRUSTED_ORIGINS = _csrf_origins + [x.strip() for x in _csrf_extra if x.strip()]
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)

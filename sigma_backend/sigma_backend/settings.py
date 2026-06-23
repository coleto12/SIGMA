"""
Configuración principal del proyecto SIGMA
Universidad de Cartagena - Sistema Integrado de Gestión de Matrícula Académica
"""

from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------
# Seguridad
# -------------------------------------------------------------------
SECRET_KEY = config('DJANGO_SECRET_KEY', default='clave-temporal-cambiar-en-produccion')

DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config(
    'DJANGO_ALLOWED_HOSTS',
    default='localhost,127.0.0.1'
).split(',')

# -------------------------------------------------------------------
# CSRF en producción: Django exige que los orígenes HTTPS desde donde
# se envían formularios (como el login del admin) estén declarados
# explícitamente. Sin esto, el admin da "403 Verificación CSRF fallida"
# en Railway (y cualquier host distinto a localhost detrás de HTTPS).
# -------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = config(
    'DJANGO_CSRF_TRUSTED_ORIGINS',
    default='http://localhost:8000,http://127.0.0.1:8000'
).split(',')

# -------------------------------------------------------------------
# Aplicaciones instaladas
# -------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary_storage',
    'cloudinary',

    # Terceros
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',

    # Apps propias de SIGMA (orden según dependencias entre bloques)
    'institucional',
    'usuarios',
    'academico',
    'programacion',
    'matricula',
    'notificaciones',
    'auditoria',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sigma_backend.urls'

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

WSGI_APPLICATION = 'sigma_backend.wsgi.application'

# -------------------------------------------------------------------
# Base de datos: PostgreSQL alojado en Supabase
# Se configura mediante la variable DATABASE_URL (connection string que
# Supabase entrega en Project Settings > Database > Connection string > URI)
# -------------------------------------------------------------------
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True,
    )
}

# -------------------------------------------------------------------
# Validación de contraseñas (para login institucional, si se usa
# autenticación local en lugar de SSO/OAuth puro)
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------------------------------------------
# Internacionalización
# -------------------------------------------------------------------
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# Archivos estáticos y media (documentos adjuntos, matrículas oficiales)
#
# 'static' (CSS/JS del admin de Django) se sirve con WhiteNoise.
# 'media' (archivos SUBIDOS por usuarios: PDFs, documentos adjuntos) se
# guarda en Cloudinary, porque Railway no tiene disco persistente: si
# se guardaran localmente, se perderían en cada redeploy/reinicio.
# -------------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
}

# Si hay credenciales de Cloudinary configuradas, usarlo para 'media'.
# Si no (ej. desarrollo local sin Cloudinary), cae a disco local, para
# no romper el flujo de quien todavía no lo haya configurado.
if CLOUDINARY_STORAGE['CLOUD_NAME']:
    STORAGES = {
        'default': {
            'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }
else:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------------------------------------------------
# Modelo de usuario personalizado (ver usuarios/models.py)
# Debe declararse ANTES de la primera migración.
# -------------------------------------------------------------------
AUTH_USER_MODEL = 'usuarios.Usuario'

# -------------------------------------------------------------------
# Django REST Framework
# -------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# -------------------------------------------------------------------
# CORS (el frontend HTML5/CSS3/JS corre en otro origen/puerto)
# -------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000'
).split(',')

# URL base del frontend, usada para construir enlaces que se envían por
# correo (ej. el enlace de restablecimiento de contraseña). En Vite el
# puerto de desarrollo por defecto es 5173, no 3000.
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:5173')

# -------------------------------------------------------------------
# JWT (djangorestframework-simplejwt)
# Ver RNF-SEG-01/02/03 del ERS: HTTPS + JWT + RBAC.
# -------------------------------------------------------------------
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# -------------------------------------------------------------------
# Correo (Gmail SMTP)
# Usado por notificaciones/services.py para enviar el correo real
# además de la notificación in-app (tabla Notificacion).
#
# EMAIL_HOST_PASSWORD debe ser una "contraseña de aplicación" de Gmail
# (myaccount.google.com/apppasswords), NUNCA la contraseña normal de la
# cuenta. Requiere verificación en dos pasos activa en esa cuenta.
# -------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)
# Timeout corto y explícito: algunos proveedores de hosting (ej. Railway)
# bloquean o filtran el tráfico saliente al puerto SMTP, lo que hace que
# la conexión se quede colgada indefinidamente en vez de fallar rápido.
# Sin este límite, eso puede agotar el WORKER TIMEOUT de Gunicorn y
# matar el proceso completo que estaba atendiendo la petición HTTP
# (ver bug real: aprobar una solicitud tumbaba el worker entero al
# intentar enviar el correo de notificación). Con el timeout, el envío
# de correo simplemente falla rápido y queda contenido por el
# try/except de notificaciones/services.py, sin afectar el resto.
EMAIL_TIMEOUT = 10

# Si no hay credenciales configuradas (.env vacío), se cae a modo consola
# para no romper el desarrollo local sin Gmail configurado.
if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
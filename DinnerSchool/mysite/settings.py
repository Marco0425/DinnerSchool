import os
from pathlib import Path
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY')
RCSECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Hosts permitidos
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',  # Para Render.com
    'dinnerschool.onrender.com',  # Tu dominio específico
]

# Configuración CSRF y seguridad
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://dinnerschool.onrender.com',
]

# Application definition
INSTALLED_APPS = [
    'core.apps.CoreConfig',
    'comedor.apps.ComedorConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',  # Para archivos estáticos
    'cloudinary_storage',  # Cloudinary para imágenes
    'cloudinary',  # Cloudinary
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para archivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
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

WSGI_APPLICATION = 'mysite.wsgi.application'

# Database - PostgreSQL en Render
# Comentar en local
# DATABASES = {
#     'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images) con WhiteNoise
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

# Configuración de Cloudinary
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

# Configurar Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

# Media files con Cloudinary
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de seguridad para producción
# if not DEBUG:
#     SECURE_SSL_REDIRECT = True
#     SESSION_COOKIE_SECURE = True
#     CSRF_COOKIE_SECURE = True
#     SECURE_BROWSER_XSS_FILTER = True
#     SECURE_CONTENT_TYPE_NOSNIFF = True
#     ALLOWED_HOSTS.extend(['.onrender.com'])

# else:
DEBUG = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
    

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'errors.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # Logger root para capturar TODOS los errores
        '': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        # Loggers específicos de tus apps
        'core': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'comedor': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        # Loggers de Django
        'django': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
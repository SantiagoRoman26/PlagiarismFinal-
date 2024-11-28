from pathlib import Path
from django.urls import reverse_lazy 
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# Application definition

BASE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'modelo',
    'plagio',
    'usuario',
    'autorizar',
    'login',
    'documento',
    'gestionDocumentos',
    'conf',
]

THIRD_APPS = [
    'formtools',
]

INSTALLED_APPS = BASE_APPS + LOCAL_APPS + THIRD_APPS

BASE_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

LOCAL_MIDDLEWARE = [

]

THIRD_MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

MIDDLEWARE =  BASE_MIDDLEWARE + LOCAL_MIDDLEWARE + THIRD_MIDDLEWARE

ROOT_URLCONF = 'PlagiarismDetector.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'PlagiarismDetector.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

LOGIN_URL=reverse_lazy('autenticar')
LOGOUT_REDIRECT_URL='homepage'

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

# STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'templates/static/')
# STATIC_URL = 'static/'

STATIC_URL = '/integriscan/static/'
MEDIA_URL = '/integriscan/media/'

# MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'uploads'

X_FRAME_OPTIONS = 'SAMEORIGIN'
XS_SHARING_ALLOWED_METHODS = ['POST','GET','OPTIONS', 'PUT', 'DELETE']

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_HOST = 'smtp.googlemail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'santiagoromanprueba@gmail.com'
EMAIL_HOST_PASSWORD = 'lelpzcumdqgmoygm'
EMAIL_USE_TLS = True  
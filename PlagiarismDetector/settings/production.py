import os
from PlagiarismDetector.logging import *
from PlagiarismDetector.settings.base import *
from dotenv import load_dotenv

load_dotenv(Path.joinpath(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [ '*' ]

CORS_ALLOW_ALL_ORIGINS=True

CSRF_TRUSTED_ORIGINS = [ 'https://plagiarismfinal-production.up.railway.app/*']


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'templates/static/')

MEDIA_ROOT = BASE_DIR / 'uploads'
# STATIC_URL = 'static/'


# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'uploads'

# X_FRAME_OPTIONS = 'SAMEORIGIN'
# XS_SHARING_ALLOWED_METHODS = ['POST','GET','OPTIONS', 'PUT', 'DELETE']

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

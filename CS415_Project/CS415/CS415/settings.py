"""
Django settings for CS415 project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os.path
import sys                           

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%)+3a&lnyn+_7@x$^b!1nx6f!vq=y48o(9at-tswd(l+b$n7h&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#ALLOWED_HOSTS = ['192.168.169.63']
ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'WatchIt',
    "semantic_admin",
    "semantic_forms",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

]


AUTH_USER_MODEL = "WatchIt.User" 
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'WatchIt.middleware.ActivityLoggingMiddleware'
]

ROOT_URLCONF = 'CS415.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [],
        'DIRS': [BASE_DIR / 'templates'],
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

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

WSGI_APPLICATION = 'CS415.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'WatchIt',
        'USER': 'karan',
        'PASSWORD': '123',
        'HOST': 'localhost',
        'PORT': '5432',
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Pacific/Fiji'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


STATICFILES_DIRS =  BASE_DIR, 'static'

MEDIA_ROOT =  os.path.join(BASE_DIR, 'media') 
MEDIA_URL = 'media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STRIPE_PUBLIC_KEY = 'pk_test_51PGTzgDGr86VR9McfOmvWQcbkUF5BF7SFwj7nL2r5WfvCR7jq1z8oi4kcJumvpDkdXbXyDhckyQD1lztDl2vljV300dYWxZbAq'
STRIPE_SECRET_KEY = 'sk_test_51PGTzgDGr86VR9McJQWPN7Gson2pC84pbSRrYTuWnOCVXKmMrAm6e4o6Yl0bOMxkWLGaVnV8QiLUvF4pVtU28Vsi005vdSFcTP'


EMAIL_FROM_USER = 'watchitmoviess@gmail.com'
EMAIL_HOST_PASSWORD = 'vadhshijhnwpvfle '
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'watchitmoviess@gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587

#savi
TWILIO_ACCOUNT_SID = 'ACc5449c6fe2a297c1f2b500ab60386cb8'
TWILIO_AUTH_TOKEN = '5b9912fca3cc447f1e64b9a8cd131984'
TWILIO_PHONE_NUMBER = '+14018122982'

#zak
# TWILIO_ACCOUNT_SID = 'ACe597614a58aa098008a9416a14080b45'
# TWILIO_AUTH_TOKEN = 'ae90879ac5e337117ab0885ed193b31a'
# TWILIO_PHONE_NUMBER = ''

#karan

# TWILIO_ACCOUNT_SID = 'ACbab5a0fb84843f39a1c52f75d4eec69b'
# TWILIO_AUTH_TOKEN = '0eb5dd22f89043e4f7daf7326a4e08ce'
# TWILIO_PHONE_NUMBER = '+13856441298'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'user_activity.log',
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'WatchIt': {
            'handlers': ['file'],  # Only include the 'file' handler
            'level': 'INFO',
            'propagate': False,
        },
        'WatchIt.security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Path to the SSL certificate and key
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SSL_CERTIFICATE = os.path.join(BASE_DIR, 'certs', 'localhost.crt')
SSL_KEY = os.path.join(BASE_DIR, 'certs', 'localhost.key')

#TWILIO_ACCOUNT_SID = 'ACbab5a0fb84843f39a1c52f75d4eec69b'
#TWILIO_AUTH_TOKEN = '0eb5dd22f89043e4f7daf7326a4e08ce'
#TWILIO_PHONE_NUMBER = '+13856441298'


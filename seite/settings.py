"""
Django settings for seite project.

Generated by 'django-admin startproject' using Django 1.9.12.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
DATA_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_env_variable(name):
    '''
    Gets the environment variable or throws ImproperlyConfigured exception
    :rtype: object
    '''
    try:
        return os.environ[name]
    except KeyError:
        raise ImproperlyConfigured('Environment variable “%s” not found.' % name)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_h!7u1tm_6)ncy=8mv24yocp_@b^)l!l_yvo=9*v=afg_l9vr#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'Grundgeruest',
    'Veranstaltungen',
    'Produkte',
    'Bibliothek',
    'Scholien',
    'Workflow',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.admindocs',
    'django_extensions',

    'userena',
    'guardian',
    'easy_thumbnails',
    'django.contrib.sites',
    'django.contrib.humanize',
    'easycart',
    'django_countries',
    'django_cron',
    'google_analytics',
    'webstack_django_sorting',
    'mathfilters',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'seite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'easycart.context_processors.cart',
                'Grundgeruest.views.liste_menue_zurueckgeben',
            ],
        },
    },
]

WSGI_APPLICATION = 'seite.wsgi.application'


AUTH_USER_MODEL = 'Grundgeruest.Nutzer'

# userena-specific settings

AUTH_PROFILE_MODULE = 'Grundgeruest.ScholariumProfile'

AUTHENTICATION_BACKENDS = (
    'userena.backends.UserenaAuthenticationBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ANONYMOUS_USER_ID = -1

USERENA_WITHOUT_USERNAMES = True
USERENA_SIGNIN_REDIRECT_URL = '/nutzer/%(username)s/'
USERENA_REGISTER_PROFILE = False
LOGIN_URL = '/nutzer/anmelden/'
LOGOUT_URL = '/nutzer/abmelden/'

SITE_ID = 2  # für localhost in der ursprünglichen DB

# easycart-specific settings

EASYCART_CART_CLASS = 'Produkte.views.Warenkorb'

# django-countries

COUNTRIES_FIRST = ['AT', 'DE', 'CH', 'LI']
COUNTRIES_FIRST_REPEAT = True
COUNTRIES_FIRST_BREAK = 20*'-'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedSHA1PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
]

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'CET'

USE_I18N = True

USE_L10N = True

USE_TZ = False

DATE_FORMAT = 'l, j. M Y'
DATETIME_FORMAT = DATE_FORMAT + ', H:M'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(DATA_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'seite', 'static'),
]


try:
    MEDIA_ROOT = '/home/scholarium/scholarium_daten/'
    os.chdir(MEDIA_ROOT)
except FileNotFoundError:
    MEDIA_ROOT = os.path.join(DATA_DIR, 'media')

MEDIA_URL = '/media/'

# EMail-Versand

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'iljasseite@gmail.com'
EMAIL_HOST_PASSWORD = 'ad8F9hnv2Jjsk4Rg5ns'
DEFAULT_TO_EMAILS = ['mb@scholarium.at', 'ilja1988@gmail.com']

# Paypal
PAYPAL_MODE = 'sandbox'   # sandbox or live
PAYPAL_CLIENT_ID = 'AasKeJoihSdkebF5q7QCuubWoIpnlZiV5vfklRN6onwfU9AJYOwXJ5HvDO-PFghOdi26gGzzpc38qb7B'
# get_env_variable('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = 'EI3An34Ea1-D5oKS59QwAI0mGu8ELZRT3m9YxPKfRCdoGlqlYL3Oqc8jlelBMpebtxXsKBjO4GCZmnOz'
# get_env_variable('PAYPAL_CLIENT_SECRET')

HOSTNAME = 'https://scholarium.at'

# Cron
CRON_CLASSES = [
    # 'seite.cron.cron_t2sql',
    'seite.cron.cron_publish',
    'seite.cron.cron_zotero'
]

# Release period in days
RELEASE_PERIOD = 6

GOOGLE_ANALYTICS = {
    'google_analytics_id': 'UA-117190689-1',
}

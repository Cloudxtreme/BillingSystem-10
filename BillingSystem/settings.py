"""
Django settings for BillingSystem project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import datetime
today = datetime.datetime.now()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Access configparser to load variable values from config file
from django.utils.six.moves import configparser
CONFIG = configparser.SafeConfigParser(allow_no_value=True)
CONFIG.read('config.cfg')
CONFIG = CONFIG._sections


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k!_*3=#=9jhy7ni_y-^t%w309loek+m+x%y#-e4u8mw&4_)=ur'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_countries',
    'localflavor',
    'widget_tweaks',
    'simple_history',
    'deepdiff',

    'infoGatherer',
    'claims',
    'accounts',
    'dashboard',
    'accounting',
    'displayContent',
    'daterange_filter',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'audit_log.middleware.UserLoggingMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',

)

ROOT_URLCONF = 'BillingSystem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'infoGatherer/templates/'),
            os.path.join(BASE_DIR, 'templates/'),
        ],
        # 'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

WSGI_APPLICATION = 'BillingSystem.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass 

DATE_FORMAT = "m/d/Y"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'xenonhealth',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': 'Xenonhealth',
    }
}

if DEBUG:
    EMAIL_HOST = 'smtp.office365.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'ekasit.jarussinvichai@xenonhealth.com'
    EMAIL_HOST_PASSWORD = 'H@ppy001'
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static/')]

AUTH_USER_MODEL = 'accounts.User'

today_path = today.strftime("%Y/%m/%d")
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/documents/'+today_path)
MEDIA_URL = '/media/'

LOGIN_URL = '/accounts/sign_in/'

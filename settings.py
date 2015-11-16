import sys
from os.path import isdir
import os

ALLOWED_HOSTS = [u'quast.bioinf.spbau.ru', u'new-quast.bioinf.spbau.ru']

SOURCE_DIRPATH              = os.path.abspath(os.path.dirname(__file__))
HOME_DIRPATH                = os.path.join(SOURCE_DIRPATH, '..')
VIRTUALENV_PATH             = os.path.join(HOME_DIRPATH, 'virtualenv')

DATA_DIRPATH                = os.path.join(HOME_DIRPATH, 'data')
INPUT_ROOT_DIRPATH          = os.path.join(DATA_DIRPATH, 'input')
RESULTS_ROOT_DIRPATH        = os.path.join(DATA_DIRPATH, 'results')
REGULAR_REPORT_DIRNAME      = 'full_output'
HTML_REPORT_FNAME           = 'report.html'
HTML_REPORT_AUX_DIRNAME     = 'report_html_aux'
DATA_SETS_ROOT_DIRPATH      = os.path.join(DATA_DIRPATH, 'data_sets')
celerydb_fpath              = os.path.join(DATA_DIRPATH, 'celery.sqlite')
quastdb_fpath               = os.path.join(DATA_DIRPATH, 'quast.sqlite')

QUAST_DIRPATH               = os.path.join(SOURCE_DIRPATH, 'quast')
QUAST_PY_FPATH              = os.path.join(QUAST_DIRPATH, 'quast.py')
ERROR_LOG_FNAME             = 'error.log'
GLOSSARY_PATH               = os.path.join(QUAST_DIRPATH, 'libs/html_saver/glossary.json')
MANUAL_FPATH                = os.path.join(QUAST_DIRPATH, 'manual.html')
CHANGES_FPATH               = os.path.join(QUAST_DIRPATH, 'CHANGES')
LICENSE_FPATH               = os.path.join(QUAST_DIRPATH, 'LICENSE')
BIB_FPATH                   = os.path.join(QUAST_DIRPATH, 'quast_ref.bib')


APP_DIRPATH                 = os.path.join(SOURCE_DIRPATH, 'quast_app')
FILES_DIRPATH               = os.path.join(APP_DIRPATH, 'files')
FILES_DOWNLOADS_DIRPATH     = os.path.join(FILES_DIRPATH, 'downloads')
EXAMPLE_DIRPATH             = os.path.join(FILES_DIRPATH, 'example')
IDBA_DIRPATH                = os.path.join(FILES_DIRPATH, 'idba')
PAPER_DIRPATH               = os.path.join(FILES_DIRPATH, 'paper')

REPORT_LINK_BASE            = '/reports/'

database = 'sqlite'

if os.environ.get('DEVELOPMENT', None):
    DEBUG = True
    ADDRESS = 'http://127.0.0.1:8000/'
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

else:
    DEBUG = False
    ADDRESS = 'http://quast.bioinf.spbau.ru/'
    database = 'mysql'
    EMAIL_HOST = 'localhost'

<<<<<<< Updated upstream
    database = 'mysql'
#EMAIL_HOST = 'localhost'
#EMAIL_HOST = '127.0.0.1'
#EMAIL_HOST_USER = ''
#EMAIL_HOST_PASSWORD = ''
#EMAIL_PORT = 1025
#TEMPLATE_DEBUG = DEBUG
=======

TEMPLATE_DEBUG = DEBUG
>>>>>>> Stashed changes


REPORTS_SHOW_LIMIT = 8

DEBUG_PASSWORD = '1234'

SUPPORT_EMAIL = 'quast.support@bioinf.spbau.ru'

ADMINS = (
    ('Vlad Saveliev', 'vladsaveliev@me.com'),
)
MANAGERS = ADMINS

SEND_BROKEN_LINK_EMAILS = False


TEMPLATE_ARGS_BY_DEFAULT = {
    'debug': DEBUG,
    'support_email': SUPPORT_EMAIL,
    'address_base': ADDRESS,
}


# BROKER_URL = 'redis://localhost/0'
# BROKER_URL = 'amqp'
# Celery with sqlite
BROKER_URL = 'sqla+sqlite:///' + celerydb_fpath
# http://docs.celeryproject.org/en/latest/configuration.html#conf-database-result-backend
CELERY_RESULT_DBURI = 'sqlite:///' + celerydb_fpath
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_SEND_EVENTS = True

if database == 'mysql':
    db_engine = 'django.db.backends.mysql'
    db_name = 'quast'
else:
    db_engine = 'django.db.backends.sqlite3'
    db_name = quastdb_fpath

DATABASES = {
    'default': {
        'ENGINE': db_engine,                                                 # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': db_name,                                                     # Or path to database file if using sqlite3.
        'USER': 'root',                                                     # Not used with sqlite3.
        'PASSWORD': '',                                             # Not used with sqlite3.
        #'HOST': '',                                                         # Set to empty string for localhost. Not used with sqlite3.
        #'PORT': '',                                                         # Set to empty string for default. Not used with sqlite3.
        #'SUPPORT_TRANSACTIONS': False,
    }
}

DATABASE_OPTIONS = {
    "timeout": 20,
}

USE_TZ = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Moscow'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/files/files.lawrence.com/files/"
MEDIA_ROOT = 'media/'

# URL that handles the files served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://files.lawrence.com/files/", "http://example.com/files/"
MEDIA_URL = '/media/'

# Absolute path to the directory files files should be collected to.
# Don't put anything in this directory yourself; store your files files
# in apps' "files/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/files/files.lawrence.com/files/"
STATIC_ROOT = 'static/'

# URL prefix for files files.
# Example: "http://files.lawrence.com/files/"
STATIC_URL = '/static/'
# IMPORTANT!!!! Note slash before 'static'.
# Without it static/admin/ would become admin/static/admin

# Additional locations of files files
STATICFILES_DIRS = [
    # Put strings here, like "/home/html/files" or "C:/www/django/files".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SOURCE_DIRPATH, 'static_webserver'),
    os.path.join(QUAST_DIRPATH, 'libs/html_saver/static'),
]
ds_static = os.path.join(DATA_DIRPATH, 'static')
if isdir(ds_static):
    STATICFILES_DIRS.append(ds_static)

# List of finder classes that know how to find files files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    )

# Make this unique, and don't share it with anybody.
SECRET_KEY = '3ikccwwfa*6q7yw7^4-j_y*3&amp;6+o!j5zte!h2#%&amp;&amp;js6@hi12d'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    #    'django.core.context_processors.debug',
    #    'django.core.context_processors.i18n',
    #    'django.core.context_processors.files',
    #    'django.core.context_processors.files',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Djasngo's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (os.path.join(SOURCE_DIRPATH, 'templates'),)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
#    'object_tools',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'djcelery',
#    'django-celery',
    'quast_app',
    'ajaxuploader',
    # 'south',
#    'south_admin',
#    'django_socketio',
    )

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s.%(funcName)s line %(lineno)s: %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'handlers': {
        'console_debug': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'mail_warning': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
            'formatter': 'verbose',
        },
        'mail_info': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
            'formatter': 'verbose',
        },
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(HOME_DIRPATH, "debug.log"),
            'maxBytes': 50000,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'file_warning': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(HOME_DIRPATH, "warning.log"),
            'maxBytes': 50000,
            'backupCount': 100,
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_warning', 'file_warning'],
            'level': 'WARNING',
            'propagate': False,
            'formatter': 'verbose',
        },
        'django.db.backends': {
            'propagate': True,
            'formatter': 'verbose',
        },
        'quast': {
            'handlers': ['mail_warning', 'file_debug', 'file_warning', 'console_debug'],
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
        'quast_mailer': {
            'handlers': ['mail_info', 'file_debug', 'file_warning', 'console_debug'],
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
    },
}



## setting up session
# http://mongoengine-odm.readthedocs.org/en/latest/django.html#sessions
# SESSION_ENGINE = 'mongoengine.django.sessions'
#
# from mongoengine import connect
# connect('sessiondb')


## Celery with mongo
## http://packages.python.org/celery/getting-started/brokers/mongodb.html
#BROKER_URL = 'mongodb://localhost:27017/celery_db'
#
## http://packages.python.org/celery/configuration.html#conf-mongodb-result-backend
#CELERY_RESULT_BACKEND = "mongodb"
#CELERY_MONGODB_BACKEND_SETTINGS = {
#    "host": "localhost",
#    "port": 27017,
#    "database": "celery_db",
#    "taskmeta_collection": "run_quast_taskmeta_collection",
#}

import djcelery
djcelery.setup_loader()

# from celery.schedules import crontab
# CELERYBEAT_SCHEDULE = {
#     # Executes every Monday morning at 7:30 A.M
#     'every-monday-morning': {
#         'task': 'tasks.delete_quast_sessions',
#         'schedule': crontab(hour=7, minute=30, day_of_week=1),
#         },
#     }

#Redis and celery

#SESSION_ENGINE = 'redis_sessions.session'
#
#BROKER_HOST = 'localhost' #"192.168.1.33"
#BROKER_BACKEND = 'redis://localhost:6379/0'
#
#REDIS_PORT = 6379
#REDIS_HOST = 'localhost' #"192.168.1.33"
#
#REDIS_DB = 0
#REDIS_CONNECT_RETRY = True
#
#CELERY_SEND_EVENTS = True
#CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
#CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"
#if DEBUG:
#    CELERY_ALWAYS_EAGER = True


#Redis and celery redundant

#CELERY_REDIS_HOST = "localhost"
#CELERY_REDIS_PORT = 6379

#CELERY_ENABLE_UTC = True
#CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True
#CELERY_TASK_RESULT_EXPIRES = 60*60
#CELERY_SEND_TASK_ERROR_EMAILS = True
#CELERY_SEND_EVENTS = True
#CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"



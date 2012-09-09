
# Vlad's MacBook
development = True
home_dirpath = '/Users/vladsaveliev/Dropbox/bio/quast'

# Morality
#development = False
#home_dirpath = '/var/www/quast'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

import sys
import os

if development:
    sys.path.append(os.path.join(home_dirpath, 'quast_website'))

quast_dirpath           = os.path.join(home_dirpath, 'quast_tool')
quast_py_fpath          = os.path.join(quast_dirpath, 'quast.py')
reports_scripts_dirpath = os.path.join(quast_dirpath, 'libs/html_saver/report-scripts')
glossary_path           = os.path.join(quast_dirpath, 'libs/html_saver/glossary.json')

env_dirpath             = os.path.join(home_dirpath, 'quast_virtualenv')
templates_dirpath       = os.path.join(home_dirpath, 'quast_website/templates')
static_dirpath          = os.path.join(home_dirpath, 'static')
input_root_dirpath      = os.path.join(home_dirpath, 'input')
results_root_dirpath    = os.path.join(home_dirpath, 'results')
datasets_root_dirpath   = os.path.join(home_dirpath, 'datasets')
quastdb_fpath           = os.path.join(home_dirpath, 'quast.sqlite')
celerydb_fpath          = os.path.join(home_dirpath, 'celery.sqlite')



# Django settings for quast_website project.

ADMINS = (
    ('Vlad Saveliev', 'vladsaveliev@me.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        #'ENGINE': 'django_mongodb_engine',                                  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.sqlite3',                             # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': quastdb_fpath,                                              # Or path to database file if using sqlite3.
        #'USER': '',                                                         # Not used with sqlite3.
        #'PASSWORD': '',                                                     # Not used with sqlite3.
        #'HOST': '',                                                         # Set to empty string for localhost. Not used with sqlite3.
        #'PORT': '',                                                         # Set to empty string for default. Not used with sqlite3.
        #'SUPPORT_TRANSACTIONS': False,
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

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
MEDIA_ROOT = '/files/'

# URL that handles the files served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://files.lawrence.com/files/", "http://example.com/files/"
MEDIA_URL = '/files/'

# Absolute path to the directory files files should be collected to.
# Don't put anything in this directory yourself; store your files files
# in apps' "files/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/files/files.lawrence.com/files/"
STATIC_ROOT = '/collected_static/'

# URL prefix for files files.
# Example: "http://files.lawrence.com/files/"
STATIC_URL = '/static/'

# Additional locations of files files
STATICFILES_DIRS = (
# Put strings here, like "/home/html/files" or "C:/www/django/files".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
)
if development:
    STATICFILES_DIRS += (static_dirpath,)

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
WSGI_APPLICATION = 'quast_website.wsgi.application'

TEMPLATE_DIRS = (templates_dirpath,)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'quast_app',
    'ajaxuploader',
    'djcelery',
    )

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        }
}

#BROKER_URL = 'redis://localhost/0'
#BROKER_URL = 'amqp://guest:guest@localhost:5672//'
# Celery with sqlite
BROKER_URL = 'sqla+sqlite:///' + celerydb_fpath
# http://docs.celeryproject.org/en/latest/configuration.html#conf-database-result-backend
CELERY_RESULT_DBURI = 'sqlite:///' + celerydb_fpath


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








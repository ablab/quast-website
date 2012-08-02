# Django settings for quast_website project.
import os


ENV_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '../quast_virtualenv'))


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

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
MEDIA_ROOT = '/files/'

# URL that handles the files served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://files.lawrence.com/files/", "http://example.com/files/"
MEDIA_URL = '/files/'

# Absolute path to the directory files files should be collected to.
# Don't put anything in this directory yourself; store your files files
# in apps' "files/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/files/files.lawrence.com/files/"
STATIC_ROOT = 'collected_static'

# URL prefix for files files.
# Example: "http://files.lawrence.com/files/"
STATIC_URL = '/static/'

# Additional locations of files files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/files" or "C:/www/django/files".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/Users/vladsaveliev/Dropbox/bio/quast-website/static/',
)

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

#TEMPLATE_CONTEXT_PROCESSORS = (
#    'django.core.context_processors.debug',
#    'django.core.context_processors.i18n',
#    'django.core.context_processors.files',
#    'django.core.context_processors.files',
#    'django.contrib.auth.context_processors.auth',
#    'django.contrib.messages.context_processors.messages',
#)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

SESSION_ENGINE = 'django.contrib.sessions.backends.file'

ROOT_URLCONF = 'quast_website.urls'

# Python dotted path to the WSGI application used by Djasngo's runserver.
WSGI_APPLICATION = 'quast_website.wsgi.application'

TEMPLATE_DIRS = ('templates',)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
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


# celery setup
BROKER_URL = 'redis://localhost:6379/0'

CELERY_RESULT_BACKEND = 'redis://'
CELERY_REDIS_HOST = "localhost"
CELERY_REDIS_PORT = 6379

#CELERY_ENABLE_UTC = True
#CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True
#CELERY_TASK_RESULT_EXPIRES = 60*60
#CELERY_SEND_TASK_ERROR_EMAILS = True
#CELERY_SEND_EVENTS = True
#CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

import djcelery
djcelery.setup_loader()

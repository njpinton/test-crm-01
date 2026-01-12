"""
Development settings for CRM project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# For local development, use SQLite by default
# To use Cloud SQL Proxy, set DATABASE_URL in .env
DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default='sqlite:///db.sqlite3'
    )
}


# Email backend - console output for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Static files - use default settings from base.py
# No Cloud Storage in development


# Debug toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

INTERNAL_IPS = [
    '127.0.0.1',
]


# Disable HTTPS redirect for local development
SECURE_SSL_REDIRECT = False


# Logging configuration for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

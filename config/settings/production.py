"""
Production settings for CRM project (GCP Cloud Run).
"""

from .base import *
import os
from datetime import timedelta
from django.core.exceptions import ImproperlyConfigured

# CRITICAL: Enforce SECRET_KEY is set in production
if SECRET_KEY == 'dev-only-insecure-key-do-not-use-in-production':
    _secret = env('DJANGO_SECRET_KEY', default=None)
    if not _secret:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY environment variable must be set in production. "
            "Generate one with: python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
        )
    SECRET_KEY = _secret

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Get allowed hosts from environment variable
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*.run.app'])


# Database - Cloud SQL PostgreSQL
# https://cloud.google.com/python/django/run#cloud-sql-for-postgresql

# The connection name is formatted as: PROJECT_ID:REGION:INSTANCE_NAME
CLOUDRUN_SERVICE_URL = env('CLOUDRUN_SERVICE_URL', default=None)

# Connection pooling - reuse connections to avoid handshake overhead
CONN_MAX_AGE = env.int('CONN_MAX_AGE', default=60)

if os.getenv('GAE_APPLICATION', None) or os.getenv('K_SERVICE', None):
    # Running on Cloud Run or App Engine
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DATABASE_NAME'),
            'USER': env('DATABASE_USER'),
            'PASSWORD': env('DATABASE_PASSWORD'),
            'HOST': '/cloudsql/' + env('CLOUD_SQL_CONNECTION_NAME'),
            'CONN_MAX_AGE': CONN_MAX_AGE,
        }
    }
else:
    # Fallback to DATABASE_URL for other deployments
    DATABASES = {
        'default': env.db('DATABASE_URL')
    }
    DATABASES['default']['CONN_MAX_AGE'] = CONN_MAX_AGE


# Cloud Storage for static and media files
# https://django-storages.readthedocs.io/en/latest/backends/gcloud.html

GS_BUCKET_NAME = env('GS_BUCKET_NAME')
GS_PROJECT_ID = env('GS_PROJECT_ID', default=None)
GS_DEFAULT_ACL = 'publicRead'
GS_FILE_OVERWRITE = False
GS_EXPIRATION = timedelta(hours=1)  # Signed URL expiration (1 hour for better UX)

# Static files bucket
GS_STATIC_BUCKET_NAME = env('GS_STATIC_BUCKET_NAME', default=GS_BUCKET_NAME)
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
STATIC_URL = f'https://storage.googleapis.com/{GS_STATIC_BUCKET_NAME}/static/'

# Media files bucket
GS_MEDIA_BUCKET_NAME = env('GS_MEDIA_BUCKET_NAME', default=GS_BUCKET_NAME)
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
MEDIA_URL = f'https://storage.googleapis.com/{GS_MEDIA_BUCKET_NAME}/media/'


# Email backend - Gmail API for production
EMAIL_BACKEND = 'gmailapi_backend.mail.GmailBackend'
GMAIL_API_CLIENT_ID = env('GMAIL_CLIENT_ID')
GMAIL_API_CLIENT_SECRET = env('GMAIL_CLIENT_SECRET')
GMAIL_API_REFRESH_TOKEN = env('GMAIL_REFRESH_TOKEN')


# Security Settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True


# CORS settings (if needed for API access)
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])


# Logging configuration for production (Cloud Logging)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '%(levelname)s %(asctime)s %(name)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
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
            'level': 'INFO',
            'propagate': False,
        },
    },
}


# Cache configuration (optional - can use Cloud Memorystore if needed)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


# Sentry error tracking (optional)
SENTRY_DSN = env('SENTRY_DSN', default=None)
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=True
    )

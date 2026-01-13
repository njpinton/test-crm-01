"""
Vercel deployment settings for CRM project.
"""

from .base import *
import os
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
DEBUG = env.bool('DEBUG', default=False)

# Vercel domains
VERCEL_URL = env('VERCEL_URL', default=None)
VERCEL_PROJECT_PRODUCTION_URL = env('VERCEL_PROJECT_PRODUCTION_URL', default=None)

# Build allowed hosts dynamically
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
if VERCEL_URL:
    ALLOWED_HOSTS.append(VERCEL_URL)
if VERCEL_PROJECT_PRODUCTION_URL:
    ALLOWED_HOSTS.append(VERCEL_PROJECT_PRODUCTION_URL)
# Allow all Vercel preview deployments
ALLOWED_HOSTS.extend(['.vercel.app', 'localhost', '127.0.0.1'])

# CSRF trusted origins for Vercel
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
if VERCEL_URL:
    CSRF_TRUSTED_ORIGINS.append(f'https://{VERCEL_URL}')
if VERCEL_PROJECT_PRODUCTION_URL:
    CSRF_TRUSTED_ORIGINS.append(f'https://{VERCEL_PROJECT_PRODUCTION_URL}')
# Allow all Vercel preview deployments
CSRF_TRUSTED_ORIGINS.append('https://*.vercel.app')


# Database - Vercel Postgres, Neon, Supabase, or any PostgreSQL
# Uses DATABASE_URL environment variable
DATABASE_URL = env('DATABASE_URL', default=None)
POSTGRES_URL = env('POSTGRES_URL', default=None)  # Vercel Postgres format

if POSTGRES_URL:
    # Vercel Postgres
    DATABASES = {
        'default': env.db_url('POSTGRES_URL')
    }
elif DATABASE_URL:
    DATABASES = {
        'default': env.db('DATABASE_URL')
    }
else:
    # Fallback to SQLite for simple deployments (not recommended for production)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/db.sqlite3',
        }
    }

# Connection pooling settings
if 'default' in DATABASES and DATABASES['default'].get('ENGINE') != 'django.db.backends.sqlite3':
    DATABASES['default']['CONN_MAX_AGE'] = env.int('CONN_MAX_AGE', default=60)
    DATABASES['default']['CONN_HEALTH_CHECKS'] = True


# Static files configuration for Vercel
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Use simple storage for Vercel (no manifest)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Disable WhiteNoise's missing directory check
WHITENOISE_USE_FINDERS = True


# Media files - use external storage (GCP, S3, etc.) or Vercel Blob
GS_BUCKET_NAME = env('GS_BUCKET_NAME', default=None)
if GS_BUCKET_NAME:
    # Use Google Cloud Storage
    from datetime import timedelta
    GS_PROJECT_ID = env('GS_PROJECT_ID', default=None)
    GS_DEFAULT_ACL = 'publicRead'
    GS_FILE_OVERWRITE = False
    GS_EXPIRATION = timedelta(hours=1)
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/media/'
else:
    # Local media (will not persist on Vercel serverless)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = '/tmp/media'


# Email backend
GMAIL_CLIENT_ID = env('GMAIL_CLIENT_ID', default=None)
if GMAIL_CLIENT_ID:
    EMAIL_BACKEND = 'gmailapi_backend.mail.GmailBackend'
    GMAIL_API_CLIENT_ID = GMAIL_CLIENT_ID
    GMAIL_API_CLIENT_SECRET = env('GMAIL_CLIENT_SECRET')
    GMAIL_API_REFRESH_TOKEN = env('GMAIL_REFRESH_TOKEN')
else:
    # Fallback to console backend
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Security Settings
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True


# Logging configuration
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
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
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
    },
}


# Cache - use local memory (serverless-friendly)
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

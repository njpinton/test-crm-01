"""
Vercel serverless function handler for Django.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.vercel')

from django.core.wsgi import get_wsgi_application

# Vercel Python runtime expects 'app' to be a WSGI application
app = get_wsgi_application()

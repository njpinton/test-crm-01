"""
Vercel serverless function handler for Django.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

# Vercel expects a handler function
def handler(request, context=None):
    """
    Vercel serverless function handler.
    This wraps the Django WSGI application.
    """
    return application

# For Vercel Python runtime
app = application

"""
Vercel serverless function handler for Django.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.vercel')

# Run migrations on cold start
def run_migrations():
    """Run pending migrations on first request (cold start)."""
    try:
        import django
        django.setup()
        from django.core.management import call_command
        call_command('migrate', '--noinput', verbosity=1)
        print("Migrations completed successfully")
    except Exception as e:
        import traceback
        print(f"Migration error: {e}")
        traceback.print_exc()

# Run migrations before initializing the app
run_migrations()

from django.core.wsgi import get_wsgi_application

# Vercel Python runtime expects 'app' to be a WSGI application
app = get_wsgi_application()

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.views import View
from django.core.management import call_command
from io import StringIO


class RunMigrationsView(View):
    """Run pending migrations. For use after deployment."""

    def get(self, request):
        output = StringIO()
        results = []

        # First, try to show current migration status
        try:
            call_command('showmigrations', '--list', stdout=output, stderr=output)
            results.append(f"Current migration status:\n{output.getvalue()}")
            output.truncate(0)
            output.seek(0)
        except Exception as e:
            results.append(f"Could not get migration status: {e}")

        # Check if we need to fake certain migrations
        fake_migrations = request.GET.get('fake')
        if fake_migrations:
            try:
                app, migration = fake_migrations.rsplit('.', 1)
                call_command('migrate', app, migration, '--fake', '--noinput', stdout=output, stderr=output)
                results.append(f"Faked migration {fake_migrations}:\n{output.getvalue()}")
                output.truncate(0)
                output.seek(0)
            except Exception as e:
                results.append(f"Failed to fake migration: {e}")

        # Try to run migrations
        try:
            call_command('migrate', '--noinput', stdout=output, stderr=output)
            results.append(f"Migration output:\n{output.getvalue()}")
        except Exception as e:
            results.append(f"Migration error: {str(e)}\n\nOutput:\n{output.getvalue()}")

        return HttpResponse(f"<pre>{'<hr>'.join(results)}</pre>")


class HomeView(LoginRequiredMixin, TemplateView):
    """
    Dashboard home view for authenticated users.
    """
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any dashboard-specific context here
        # e.g., recent deals, activity summary, etc.
        return context

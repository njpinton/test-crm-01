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
        try:
            call_command('migrate', '--noinput', stdout=output, stderr=output)
            result = output.getvalue()
            return HttpResponse(f"<pre>Migration output:\n\n{result}</pre>")
        except Exception as e:
            return HttpResponse(f"<pre>Migration error:\n\n{str(e)}\n\nOutput:\n{output.getvalue()}</pre>")


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

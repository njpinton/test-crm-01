from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


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

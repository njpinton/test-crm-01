from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count, Sum
from django.http import HttpResponse
from django.template.loader import render_to_string

from .models import Client
from .forms import ClientForm


class ClientListView(LoginRequiredMixin, ListView):
    """List all clients with search and filtering."""
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 25

    def get_queryset(self):
        queryset = Client.objects.annotate(
            deal_count=Count('deals'),
            total_value=Sum('deals__estimated_value')
        )

        # Search
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(company_name__icontains=search) |
                Q(contact_name__icontains=search) |
                Q(contact_email__icontains=search)
            )

        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Sorting
        sort = self.request.GET.get('sort', 'company_name')
        if sort.lstrip('-') in ['company_name', 'created_at', 'deal_count', 'status']:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Client.Status.choices
        context['current_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class ClientDetailView(LoginRequiredMixin, DetailView):
    """View client details with associated deals."""
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deals'] = self.object.deals.select_related('owner').order_by('-created_at')[:10]
        context['deal_stats'] = self.object.deals.aggregate(
            total_count=Count('id'),
            total_value=Sum('estimated_value'),
            won_count=Count('id', filter=Q(stage='CLOSED_WON')),
            won_value=Sum('actual_value', filter=Q(stage='CLOSED_WON'))
        )
        return context


class ClientCreateView(LoginRequiredMixin, CreateView):
    """Create a new client."""
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('clients:detail', kwargs={'pk': self.object.pk})


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    """Edit an existing client."""
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'

    def get_success_url(self):
        return reverse_lazy('clients:detail', kwargs={'pk': self.object.pk})


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a client (with confirmation)."""
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deal_count'] = self.object.deals.count()
        return context


class ClientSearchView(LoginRequiredMixin, ListView):
    """HTMX endpoint for client search (used in deal forms)."""
    model = Client
    template_name = 'clients/partials/client_search_results.html'
    context_object_name = 'clients'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if len(query) < 2:
            return Client.objects.none()

        return Client.objects.filter(
            Q(company_name__icontains=query) |
            Q(contact_name__icontains=query)
        )[:10]

    def render_to_response(self, context, **response_kwargs):
        if self.request.htmx:
            html = render_to_string(self.template_name, context, request=self.request)
            return HttpResponse(html)
        return super().render_to_response(context, **response_kwargs)

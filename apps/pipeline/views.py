import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    TemplateView, ListView, DetailView,
    CreateView, UpdateView, DeleteView, View
)
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from .models import Deal, DealFile, DealActivity
from .forms import DealForm, DealCloseForm, DealFileUploadForm
from apps.clients.models import Client


class KanbanBoardView(LoginRequiredMixin, TemplateView):
    """Main Kanban board view showing all pipeline stages."""
    template_name = 'pipeline/kanban.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get deals grouped by stage
        stages_data = []
        for stage in Deal.get_stage_order():
            deals = Deal.objects.filter(stage=stage.value).select_related(
                'client', 'owner'
            ).order_by('position', '-created_at')

            stage_total = deals.aggregate(
                total=Sum('estimated_value'),
                count=Count('id')
            )

            stages_data.append({
                'stage': stage,
                'deals': deals,
                'count': stage_total['count'] or 0,
                'total_value': stage_total['total'] or 0,
            })

        context['stages'] = stages_data
        context['total_pipeline_value'] = Deal.objects.filter(
            stage__in=Deal.ACTIVE_STAGES
        ).aggregate(total=Sum('estimated_value'))['total'] or 0

        # Breadcrumbs
        context['breadcrumbs'] = [
            {'label': 'Pipeline', 'url': None},
        ]

        return context


class DealListView(LoginRequiredMixin, ListView):
    """List view with filtering and sorting."""
    model = Deal
    template_name = 'pipeline/deal_list.html'
    context_object_name = 'deals'
    paginate_by = 25

    def get_queryset(self):
        queryset = Deal.objects.select_related('client', 'owner', 'estimator')

        # Apply filters from query params
        stage = self.request.GET.get('stage')
        owner = self.request.GET.get('owner')
        client = self.request.GET.get('client')
        search = self.request.GET.get('q')

        if stage:
            queryset = queryset.filter(stage=stage)
        if owner:
            queryset = queryset.filter(owner_id=owner)
        if client:
            queryset = queryset.filter(client_id=client)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(client__company_name__icontains=search) |
                Q(description__icontains=search)
            )

        # Apply sorting
        sort = self.request.GET.get('sort', '-created_at')
        return queryset.order_by(sort)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stage_choices'] = Deal.Stage.choices
        context['current_stage'] = self.request.GET.get('stage', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class DealDetailView(LoginRequiredMixin, DetailView):
    """Deal detail view with files and activity."""
    model = Deal
    template_name = 'pipeline/deal_detail.html'
    context_object_name = 'deal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['files'] = self.object.files.filter(is_current=True)
        context['activities'] = self.object.activities.all()[:20]
        context['close_form'] = DealCloseForm(initial={'stage': self.object.stage})

        # Breadcrumbs
        context['breadcrumbs'] = [
            {'label': 'Pipeline', 'url': reverse_lazy('pipeline:kanban')},
            {'label': self.object.title, 'url': None},
        ]

        return context


class DealCreateView(LoginRequiredMixin, CreateView):
    """Create new deal."""
    model = Deal
    form_class = DealForm
    template_name = 'pipeline/deal_form.html'

    def get_initial(self):
        initial = super().get_initial()
        # Pre-select client if provided in URL
        client_id = self.request.GET.get('client')
        if client_id:
            initial['client'] = client_id
        # Default owner to current user
        initial['owner'] = self.request.user
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        if not form.instance.owner:
            form.instance.owner = self.request.user
        response = super().form_valid(form)

        # Log activity
        DealActivity.objects.create(
            deal=self.object,
            activity_type=DealActivity.ActivityType.CREATED,
            description=f"Deal created",
            user=self.request.user
        )

        return response

    def get_success_url(self):
        return reverse_lazy('pipeline:deal_detail', kwargs={'pk': self.object.pk})


class DealUpdateView(LoginRequiredMixin, UpdateView):
    """Edit existing deal."""
    model = Deal
    form_class = DealForm
    template_name = 'pipeline/deal_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)

        DealActivity.objects.create(
            deal=self.object,
            activity_type=DealActivity.ActivityType.EDITED,
            description="Deal updated",
            user=self.request.user
        )

        return response

    def get_success_url(self):
        return reverse_lazy('pipeline:deal_detail', kwargs={'pk': self.object.pk})


class DealDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a deal."""
    model = Deal
    template_name = 'pipeline/deal_confirm_delete.html'
    success_url = reverse_lazy('pipeline:kanban')


@method_decorator(require_POST, name='dispatch')
class MoveDealView(LoginRequiredMixin, View):
    """HTMX endpoint for drag-and-drop stage changes."""

    def post(self, request):
        deal_id = request.POST.get('deal_id')
        new_stage = request.POST.get('stage')
        source_stage = request.POST.get('source_stage')
        position = request.POST.get('position', 0)

        deal = get_object_or_404(Deal, pk=deal_id)
        old_stage = deal.stage

        # Check if moving to closed stage - may need sub-reason
        if new_stage in [Deal.Stage.CLOSED_LOST.value, Deal.Stage.DECLINED_TO_BID.value]:
            # Return close modal HTML with source_stage for later counter updates
            context = {
                'deal': deal,
                'new_stage': new_stage,
                'source_stage': source_stage,
                'form': DealCloseForm(initial={'stage': new_stage})
            }
            return render(request, 'pipeline/partials/close_modal.html', context)

        deal.stage = new_stage
        deal.position = int(position)

        # For Closed Won, auto-set actual value to estimated if not set
        if new_stage == Deal.Stage.CLOSED_WON.value and not deal.actual_value:
            deal.actual_value = deal.estimated_value

        deal.save()

        # Log activity
        DealActivity.objects.create(
            deal=deal,
            activity_type=DealActivity.ActivityType.STAGE_CHANGED,
            description=f"Stage changed from {Deal.Stage(old_stage).label} to {Deal.Stage(new_stage).label}",
            old_value=old_stage,
            new_value=new_stage,
            user=request.user
        )

        # Calculate updated counts for source and target stages
        source_count = Deal.objects.filter(stage=source_stage).count() if source_stage else 0
        target_count = Deal.objects.filter(stage=new_stage).count()

        # Calculate updated stage values
        source_value = Deal.objects.filter(stage=source_stage).aggregate(
            total=Sum('estimated_value'))['total'] or 0 if source_stage else 0
        target_value = Deal.objects.filter(stage=new_stage).aggregate(
            total=Sum('estimated_value'))['total'] or 0

        # Calculate total pipeline value (active stages only)
        total_pipeline = Deal.objects.filter(
            stage__in=Deal.ACTIVE_STAGES
        ).aggregate(total=Sum('estimated_value'))['total'] or 0

        context = {
            'deal': deal,
            'source_stage': source_stage,
            'source_count': source_count,
            'source_value': source_value,
            'target_stage': new_stage,
            'target_count': target_count,
            'target_value': target_value,
            'total_pipeline': total_pipeline,
        }

        # Return updated card HTML with OOB swaps for counters
        return render(request, 'pipeline/partials/deal_card_with_oob.html', context)


@method_decorator(require_POST, name='dispatch')
class CloseDealView(LoginRequiredMixin, View):
    """Handle closing a deal with reason."""

    def post(self, request, pk):
        deal = get_object_or_404(Deal, pk=pk)
        form = DealCloseForm(request.POST)

        if form.is_valid():
            old_stage = deal.stage
            new_stage = form.cleaned_data['stage']

            deal.stage = new_stage

            if new_stage == 'CLOSED_LOST':
                deal.closed_lost_reason = form.cleaned_data['closed_lost_reason']
            elif new_stage == 'DECLINED_TO_BID':
                deal.declined_reason = form.cleaned_data['declined_reason']
            elif new_stage == 'CLOSED_WON':
                if form.cleaned_data.get('actual_value'):
                    deal.actual_value = form.cleaned_data['actual_value']
                elif not deal.actual_value:
                    deal.actual_value = deal.estimated_value

            if form.cleaned_data.get('close_notes'):
                deal.close_notes = form.cleaned_data['close_notes']

            deal.save()

            # Log activity
            DealActivity.objects.create(
                deal=deal,
                activity_type=DealActivity.ActivityType.STAGE_CHANGED,
                description=f"Deal closed: {Deal.Stage(new_stage).label}",
                old_value=old_stage,
                new_value=new_stage,
                user=request.user
            )

            if request.htmx:
                # Return empty response with HX-Trigger to refresh board
                response = HttpResponse()
                response['HX-Trigger'] = json.dumps({'dealClosed': str(deal.pk)})
                return response

            return JsonResponse({'success': True})

        # Return form with errors
        context = {'deal': deal, 'form': form, 'new_stage': request.POST.get('stage')}
        return render(request, 'pipeline/partials/close_modal.html', context)


class DealFileListView(LoginRequiredMixin, ListView):
    """List files for a deal."""
    model = DealFile
    template_name = 'pipeline/partials/file_list.html'
    context_object_name = 'files'

    def get_queryset(self):
        deal_pk = self.kwargs['deal_pk']
        return DealFile.objects.filter(deal_id=deal_pk, is_current=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deal'] = get_object_or_404(Deal, pk=self.kwargs['deal_pk'])
        context['upload_form'] = DealFileUploadForm()
        return context


class DealFileUploadView(LoginRequiredMixin, CreateView):
    """Handle file uploads for deals."""
    model = DealFile
    form_class = DealFileUploadForm

    def form_valid(self, form):
        deal = get_object_or_404(Deal, pk=self.kwargs['deal_pk'])
        form.instance.deal = deal
        form.instance.uploaded_by = self.request.user

        # Get file info
        file = form.cleaned_data['file']
        form.instance.original_filename = file.name
        form.instance.file_size = file.size
        form.instance.mime_type = file.content_type or 'application/octet-stream'

        # Handle versioning - check if file with same name exists
        existing = DealFile.objects.filter(
            deal=deal,
            original_filename=file.name,
            is_current=True
        ).first()

        if existing:
            existing.is_current = False
            existing.save()
            form.instance.previous_version = existing
            form.instance.version = existing.version + 1

        response = super().form_valid(form)

        DealActivity.objects.create(
            deal=deal,
            activity_type=DealActivity.ActivityType.FILE_ADDED,
            description=f"File uploaded: {self.object.original_filename}",
            user=self.request.user
        )

        if self.request.htmx:
            return render(self.request, 'pipeline/partials/file_list.html', {
                'files': deal.files.filter(is_current=True),
                'deal': deal,
                'upload_form': DealFileUploadForm()
            })

        return response

    def get_success_url(self):
        return reverse_lazy('pipeline:deal_detail', kwargs={'pk': self.kwargs['deal_pk']})


class DealFileDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a file from a deal."""
    model = DealFile

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        deal = self.object.deal

        DealActivity.objects.create(
            deal=deal,
            activity_type=DealActivity.ActivityType.FILE_REMOVED,
            description=f"File removed: {self.object.original_filename}",
            user=request.user
        )

        self.object.delete()

        if request.htmx:
            return render(request, 'pipeline/partials/file_list.html', {
                'files': deal.files.filter(is_current=True),
                'deal': deal,
                'upload_form': DealFileUploadForm()
            })

        return JsonResponse({'success': True})


class DealSearchView(LoginRequiredMixin, ListView):
    """HTMX endpoint for live search."""
    model = Deal
    template_name = 'pipeline/partials/search_results.html'
    context_object_name = 'deals'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if len(query) < 2:
            return Deal.objects.none()

        return Deal.objects.filter(
            Q(title__icontains=query) |
            Q(client__company_name__icontains=query)
        ).select_related('client', 'owner')[:10]

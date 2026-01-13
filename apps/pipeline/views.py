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

from .models import Deal, DealFile, DealActivity, DealSchedule, DealComment
from .forms import (
    DealForm, DealCloseForm, DealFileUploadForm,
    DealScheduleForm, DealScheduleCompleteForm, DealCommentForm
)
from apps.clients.models import Client


class KanbanBoardView(LoginRequiredMixin, TemplateView):
    """Main Kanban board view showing all pipeline stages."""
    template_name = 'pipeline/kanban.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch ALL deals in a single query, grouped by stage
        all_deals = list(Deal.objects.select_related(
            'client', 'owner'
        ).order_by('position', '-created_at'))

        # Group deals by stage in Python (much faster than N queries)
        deals_by_stage = {}
        for deal in all_deals:
            if deal.stage not in deals_by_stage:
                deals_by_stage[deal.stage] = []
            deals_by_stage[deal.stage].append(deal)

        # Build stages data
        stages_data = []
        total_pipeline_value = 0

        for stage in Deal.get_stage_order():
            stage_deals = deals_by_stage.get(stage.value, [])
            stage_total = sum(d.estimated_value or 0 for d in stage_deals)
            stage_count = len(stage_deals)

            # Track active pipeline value
            if stage.value in Deal.ACTIVE_STAGES:
                total_pipeline_value += stage_total

            stages_data.append({
                'stage': stage,
                'deals': stage_deals,
                'count': stage_count,
                'total_value': stage_total,
            })

        context['stages'] = stages_data
        context['total_pipeline_value'] = total_pipeline_value

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

        # Schedules - upcoming and past
        context['schedules'] = self.object.schedules.all()
        context['upcoming_schedules'] = self.object.schedules.filter(
            scheduled_date__gte=timezone.now().date()
        ).exclude(status__in=['COMPLETED', 'CANCELLED'])[:5]
        context['schedule_form'] = DealScheduleForm()

        # Comments
        context['comments'] = self.object.comments.filter(parent__isnull=True).select_related('author')
        context['comment_form'] = DealCommentForm()

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


# ============================================================
# Schedule Views
# ============================================================

class DealScheduleListView(LoginRequiredMixin, ListView):
    """List all schedules for a deal."""
    model = DealSchedule
    template_name = 'pipeline/partials/schedule_list.html'
    context_object_name = 'schedules'

    def get_queryset(self):
        deal_pk = self.kwargs['deal_pk']
        return DealSchedule.objects.filter(deal_id=deal_pk).select_related('assigned_to')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deal'] = get_object_or_404(Deal, pk=self.kwargs['deal_pk'])
        context['schedule_form'] = DealScheduleForm()
        return context


class DealScheduleCreateView(LoginRequiredMixin, CreateView):
    """Create a new scheduled event for a deal."""
    model = DealSchedule
    form_class = DealScheduleForm
    template_name = 'pipeline/partials/schedule_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deal'] = get_object_or_404(Deal, pk=self.kwargs['deal_pk'])
        context['is_edit'] = False
        return context

    def form_valid(self, form):
        deal = get_object_or_404(Deal, pk=self.kwargs['deal_pk'])
        form.instance.deal = deal
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        DealActivity.objects.create(
            deal=deal,
            activity_type=DealActivity.ActivityType.EDITED,
            description=f"Schedule added: {self.object.title} on {self.object.scheduled_date}",
            user=self.request.user
        )

        if self.request.htmx:
            schedules = deal.schedules.all()
            return render(self.request, 'pipeline/partials/schedule_list.html', {
                'schedules': schedules,
                'deal': deal,
                'schedule_form': DealScheduleForm()
            })

        return response

    def get_success_url(self):
        return reverse_lazy('pipeline:deal_detail', kwargs={'pk': self.kwargs['deal_pk']})


class DealScheduleUpdateView(LoginRequiredMixin, UpdateView):
    """Edit an existing scheduled event."""
    model = DealSchedule
    form_class = DealScheduleForm
    template_name = 'pipeline/partials/schedule_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deal'] = self.object.deal
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        DealActivity.objects.create(
            deal=self.object.deal,
            activity_type=DealActivity.ActivityType.EDITED,
            description=f"Schedule updated: {self.object.title}",
            user=self.request.user
        )

        if self.request.htmx:
            deal = self.object.deal
            schedules = deal.schedules.all()
            return render(self.request, 'pipeline/partials/schedule_list.html', {
                'schedules': schedules,
                'deal': deal,
                'schedule_form': DealScheduleForm()
            })

        return response

    def get_success_url(self):
        return reverse_lazy('pipeline:deal_detail', kwargs={'pk': self.object.deal.pk})


class DealScheduleDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a scheduled event."""
    model = DealSchedule

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        deal = self.object.deal
        title = self.object.title

        DealActivity.objects.create(
            deal=deal,
            activity_type=DealActivity.ActivityType.EDITED,
            description=f"Schedule removed: {title}",
            user=request.user
        )

        self.object.delete()

        if request.htmx:
            schedules = deal.schedules.all()
            return render(request, 'pipeline/partials/schedule_list.html', {
                'schedules': schedules,
                'deal': deal,
                'schedule_form': DealScheduleForm()
            })

        return JsonResponse({'success': True})


@method_decorator(require_POST, name='dispatch')
class DealScheduleCompleteView(LoginRequiredMixin, View):
    """Mark a scheduled event as complete."""

    def post(self, request, pk):
        schedule = get_object_or_404(DealSchedule, pk=pk)
        form = DealScheduleCompleteForm(request.POST)

        if form.is_valid():
            schedule.status = DealSchedule.Status.COMPLETED
            schedule.completed_at = timezone.now()
            schedule.completion_notes = form.cleaned_data.get('completion_notes', '')
            schedule.save()

            DealActivity.objects.create(
                deal=schedule.deal,
                activity_type=DealActivity.ActivityType.EDITED,
                description=f"Schedule completed: {schedule.title}",
                user=request.user
            )

            if request.htmx:
                deal = schedule.deal
                schedules = deal.schedules.all()
                return render(request, 'pipeline/partials/schedule_list.html', {
                    'schedules': schedules,
                    'deal': deal,
                    'schedule_form': DealScheduleForm()
                })

        return JsonResponse({'success': True})


@method_decorator(require_POST, name='dispatch')
class DealScheduleStatusUpdateView(LoginRequiredMixin, View):
    """Update schedule status (e.g., mark as in progress, cancelled)."""

    def post(self, request, pk):
        schedule = get_object_or_404(DealSchedule, pk=pk)
        new_status = request.POST.get('status')

        if new_status in [s.value for s in DealSchedule.Status]:
            old_status = schedule.status
            schedule.status = new_status

            if new_status == DealSchedule.Status.COMPLETED.value:
                schedule.completed_at = timezone.now()

            schedule.save()

            DealActivity.objects.create(
                deal=schedule.deal,
                activity_type=DealActivity.ActivityType.EDITED,
                description=f"Schedule status changed: {schedule.title} ({old_status} → {new_status})",
                user=request.user
            )

            if request.htmx:
                deal = schedule.deal
                schedules = deal.schedules.all()
                return render(request, 'pipeline/partials/schedule_list.html', {
                    'schedules': schedules,
                    'deal': deal,
                    'schedule_form': DealScheduleForm()
                })

        return JsonResponse({'success': True})


# ============================================================
# Comment Views
# ============================================================

class DealCommentCreateView(LoginRequiredMixin, CreateView):
    """Add a comment to a deal."""
    model = DealComment
    form_class = DealCommentForm
    template_name = 'pipeline/partials/comment_form.html'

    def form_valid(self, form):
        deal = get_object_or_404(Deal, pk=self.kwargs['deal_pk'])
        form.instance.deal = deal
        form.instance.author = self.request.user

        # Handle reply to another comment
        parent_id = self.request.POST.get('parent_id')
        if parent_id:
            form.instance.parent = get_object_or_404(DealComment, pk=parent_id)

        response = super().form_valid(form)

        DealActivity.objects.create(
            deal=deal,
            activity_type=DealActivity.ActivityType.COMMENT,
            description=f"Comment added by {self.request.user.get_full_name() or self.request.user.email}",
            user=self.request.user
        )

        if self.request.htmx:
            comments = deal.comments.filter(parent__isnull=True).select_related('author')
            return render(self.request, 'pipeline/partials/comments_section.html', {
                'comments': comments,
                'deal': deal,
                'comment_form': DealCommentForm()
            })

        return response

    def get_success_url(self):
        return reverse_lazy('pipeline:deal_detail', kwargs={'pk': self.kwargs['deal_pk']})


class DealCommentDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a comment (only author can delete)."""
    model = DealComment

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        deal = self.object.deal

        # Only allow author or admin to delete
        if self.object.author != request.user and not request.user.is_staff:
            return HttpResponse(status=403)

        DealActivity.objects.create(
            deal=deal,
            activity_type=DealActivity.ActivityType.COMMENT,
            description=f"Comment deleted by {request.user.get_full_name() or request.user.email}",
            user=request.user
        )

        self.object.delete()

        if request.htmx:
            comments = deal.comments.filter(parent__isnull=True).select_related('author')
            return render(request, 'pipeline/partials/comments_section.html', {
                'comments': comments,
                'deal': deal,
                'comment_form': DealCommentForm()
            })

        return JsonResponse({'success': True})

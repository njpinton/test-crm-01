import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Deal(models.Model):
    """
    Deal model representing opportunities in the sales pipeline.
    Tracks deals through 9 stages from initial request to close.
    """

    class Stage(models.TextChoices):
        NEW_REQUEST = 'NEW_REQUEST', 'New Request'
        ENGAGED = 'ENGAGED', 'Engaged'
        ESTIMATE_IN_PROGRESS = 'ESTIMATE_IN_PROGRESS', 'Estimate In Progress'
        ESTIMATE_SENT = 'ESTIMATE_SENT', 'Estimate Sent'
        FOLLOW_UP = 'FOLLOW_UP', 'Follow Up'
        NEGOTIATION = 'NEGOTIATION', 'Negotiation'
        CLOSED_WON = 'CLOSED_WON', 'Closed Won'
        CLOSED_LOST = 'CLOSED_LOST', 'Closed Lost'
        DECLINED_TO_BID = 'DECLINED_TO_BID', 'Declined to Bid'

    # Stages that are considered "active" (in pipeline)
    ACTIVE_STAGES = [
        'NEW_REQUEST', 'ENGAGED', 'ESTIMATE_IN_PROGRESS',
        'ESTIMATE_SENT', 'FOLLOW_UP', 'NEGOTIATION'
    ]

    # Stages that are considered "closed"
    CLOSED_STAGES = ['CLOSED_WON', 'CLOSED_LOST', 'DECLINED_TO_BID']

    class ClosedLostReason(models.TextChoices):
        PRICE = 'PRICE', 'Price Too High'
        TIMELINE = 'TIMELINE', 'Timeline Issues'
        COMPETITOR = 'COMPETITOR', 'Lost to Competitor'
        UNRESPONSIVE = 'UNRESPONSIVE', 'Client Unresponsive'
        OTHER = 'OTHER', 'Other'

    class DeclinedReason(models.TextChoices):
        TOO_SMALL = 'TOO_SMALL', 'Project Too Small'
        NOT_OUR_SCOPE = 'NOT_OUR_SCOPE', 'Not Our Scope of Work'
        TIMING = 'TIMING', 'Timing Not Right'
        CAPACITY = 'CAPACITY', 'No Capacity'
        OTHER = 'OTHER', 'Other'

    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Deal information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='deals'
    )

    # Pipeline stage
    stage = models.CharField(
        max_length=30,
        choices=Stage.choices,
        default=Stage.NEW_REQUEST,
        db_index=True
    )
    stage_changed_at = models.DateTimeField(default=timezone.now)

    # Sub-reasons for closed/declined stages
    closed_lost_reason = models.CharField(
        max_length=20,
        choices=ClosedLostReason.choices,
        blank=True
    )
    declined_reason = models.CharField(
        max_length=20,
        choices=DeclinedReason.choices,
        blank=True
    )
    close_notes = models.TextField(
        blank=True,
        help_text='Additional notes about why the deal was closed/declined'
    )

    # Financial fields
    estimated_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    actual_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Final value for closed won deals'
    )
    probability = models.IntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Probability of winning (0-100%)'
    )

    # Important dates
    expected_close_date = models.DateField(null=True, blank=True)
    actual_close_date = models.DateField(null=True, blank=True)

    # Assignment
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='owned_deals',
        help_text='Primary owner of this deal'
    )
    estimator = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='estimated_deals',
        help_text='Assigned estimator'
    )
    site_officer = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='site_officer_deals',
        help_text='Field technician who visits the site'
    )
    project_manager = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='project_manager_deals',
        help_text='Person overseeing the deal/project'
    )

    # Display order within stage (for Kanban board)
    position = models.PositiveIntegerField(default=0)

    # Metadata
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_deals'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deals'
        verbose_name = 'Deal'
        verbose_name_plural = 'Deals'
        ordering = ['position', '-created_at']
        indexes = [
            models.Index(fields=['stage', 'position']),
            models.Index(fields=['owner', 'stage']),
            models.Index(fields=['client', 'stage']),
            models.Index(fields=['expected_close_date']),
            models.Index(fields=['created_at']),
            models.Index(fields=['stage_changed_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.client.company_name}"

    def save(self, *args, **kwargs):
        # Track stage changes
        if self.pk:
            try:
                old = Deal.objects.get(pk=self.pk)
                if old.stage != self.stage:
                    self.stage_changed_at = timezone.now()
                    # Auto-set close date for closed stages
                    if self.stage in self.CLOSED_STAGES and not self.actual_close_date:
                        self.actual_close_date = timezone.now().date()
            except Deal.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    @property
    def weighted_value(self):
        """Calculate weighted pipeline value based on probability."""
        if self.estimated_value:
            return self.estimated_value * Decimal(self.probability) / 100
        return Decimal('0.00')

    @property
    def is_active(self):
        """Check if deal is in an active pipeline stage."""
        return self.stage in self.ACTIVE_STAGES

    @property
    def is_closed(self):
        """Check if deal is in a closed stage."""
        return self.stage in self.CLOSED_STAGES

    @property
    def is_won(self):
        """Check if deal is closed won."""
        return self.stage == self.Stage.CLOSED_WON

    @property
    def days_in_stage(self):
        """Calculate days since last stage change."""
        delta = timezone.now() - self.stage_changed_at
        return delta.days

    @property
    def age_in_days(self):
        """Calculate deal age in days."""
        delta = timezone.now() - self.created_at
        return delta.days

    @classmethod
    def get_stage_order(cls):
        """Return ordered list of stages for Kanban display."""
        return [
            cls.Stage.NEW_REQUEST,
            cls.Stage.ENGAGED,
            cls.Stage.ESTIMATE_IN_PROGRESS,
            cls.Stage.ESTIMATE_SENT,
            cls.Stage.FOLLOW_UP,
            cls.Stage.NEGOTIATION,
            cls.Stage.CLOSED_WON,
            cls.Stage.CLOSED_LOST,
            cls.Stage.DECLINED_TO_BID,
        ]

    @classmethod
    def get_default_probability(cls, stage):
        """Get default probability for a stage."""
        probabilities = {
            cls.Stage.NEW_REQUEST: 10,
            cls.Stage.ENGAGED: 20,
            cls.Stage.ESTIMATE_IN_PROGRESS: 30,
            cls.Stage.ESTIMATE_SENT: 50,
            cls.Stage.FOLLOW_UP: 60,
            cls.Stage.NEGOTIATION: 75,
            cls.Stage.CLOSED_WON: 100,
            cls.Stage.CLOSED_LOST: 0,
            cls.Stage.DECLINED_TO_BID: 0,
        }
        return probabilities.get(stage, 50)


def deal_file_upload_path(instance, filename):
    """Generate upload path for deal files: deals/<deal_id>/files/<filename>"""
    return f"deals/{instance.deal_id}/files/{filename}"


class DealFile(models.Model):
    """
    File attachments for deals with versioning support.
    Supports PDF, images, and spreadsheet files.
    """

    class FileType(models.TextChoices):
        ESTIMATE = 'ESTIMATE', 'Estimate'
        CONTRACT = 'CONTRACT', 'Contract'
        PROPOSAL = 'PROPOSAL', 'Proposal'
        DRAWING = 'DRAWING', 'Drawing/Plans'
        PHOTO = 'PHOTO', 'Photo'
        CORRESPONDENCE = 'CORRESPONDENCE', 'Correspondence'
        OTHER = 'OTHER', 'Other'

    # Allowed file extensions
    ALLOWED_EXTENSIONS = [
        'pdf', 'doc', 'docx',
        'xls', 'xlsx', 'csv',
        'jpg', 'jpeg', 'png', 'gif', 'webp',
        'txt', 'rtf',
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='files'
    )

    file = models.FileField(upload_to=deal_file_upload_path)
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text='File size in bytes')
    mime_type = models.CharField(max_length=100)

    file_type = models.CharField(
        max_length=20,
        choices=FileType.choices,
        default=FileType.OTHER
    )

    description = models.CharField(max_length=500, blank=True)

    # Versioning
    version = models.PositiveIntegerField(default=1)
    is_current = models.BooleanField(default=True)
    previous_version = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='newer_versions'
    )

    # Metadata
    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_deal_files'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'deal_files'
        verbose_name = 'Deal File'
        verbose_name_plural = 'Deal Files'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['deal', 'file_type']),
            models.Index(fields=['deal', 'is_current']),
            models.Index(fields=['uploaded_at']),
        ]

    def __str__(self):
        return f"{self.original_filename} (v{self.version})"

    def save(self, *args, **kwargs):
        # Store original filename and size on first save
        if not self.pk and self.file:
            self.original_filename = self.file.name.split('/')[-1]
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    @property
    def extension(self):
        """Return file extension."""
        if '.' in self.original_filename:
            return self.original_filename.split('.')[-1].lower()
        return ''

    @property
    def is_image(self):
        """Check if file is an image."""
        return self.extension in ['jpg', 'jpeg', 'png', 'gif', 'webp']

    @property
    def is_pdf(self):
        """Check if file is a PDF."""
        return self.extension == 'pdf'

    @property
    def formatted_size(self):
        """Return human-readable file size."""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"


class DealActivity(models.Model):
    """
    Activity log for deals to track history and changes.
    """

    class ActivityType(models.TextChoices):
        CREATED = 'CREATED', 'Deal Created'
        STAGE_CHANGED = 'STAGE_CHANGED', 'Stage Changed'
        EDITED = 'EDITED', 'Deal Edited'
        FILE_ADDED = 'FILE_ADDED', 'File Added'
        FILE_REMOVED = 'FILE_REMOVED', 'File Removed'
        COMMENT = 'COMMENT', 'Comment Added'
        ASSIGNED = 'ASSIGNED', 'Assignment Changed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='activities'
    )

    activity_type = models.CharField(
        max_length=20,
        choices=ActivityType.choices
    )

    description = models.TextField()

    # Store old and new values for change tracking
    old_value = models.CharField(max_length=255, blank=True)
    new_value = models.CharField(max_length=255, blank=True)

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='deal_activities'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'deal_activities'
        verbose_name = 'Deal Activity'
        verbose_name_plural = 'Deal Activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['deal', 'created_at']),
            models.Index(fields=['activity_type']),
        ]

    def __str__(self):
        return f"{self.deal.title} - {self.get_activity_type_display()}"


class DealSchedule(models.Model):
    """
    Scheduled events for deals - site visits, service appointments, inspections, etc.
    Supports recurring events and detailed scheduling information.
    """

    class EventType(models.TextChoices):
        SITE_VISIT = 'SITE_VISIT', 'Site Visit'
        INSPECTION = 'INSPECTION', 'Inspection'
        INSTALLATION = 'INSTALLATION', 'Installation'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance'
        REPAIR = 'REPAIR', 'Repair'
        FOLLOW_UP = 'FOLLOW_UP', 'Follow-up'
        OTHER = 'OTHER', 'Other'

    class Status(models.TextChoices):
        NEW_REQUEST = 'NEW_REQUEST', 'New Request'
        SITE_OFFICER_ASSIGNED = 'SITE_OFFICER_ASSIGNED', 'Site Officer Assigned'
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    # Statuses that are in the active pipeline
    ACTIVE_STATUSES = ['NEW_REQUEST', 'SITE_OFFICER_ASSIGNED', 'SCHEDULED', 'IN_PROGRESS']
    # Statuses that are considered closed/done
    CLOSED_STATUSES = ['COMPLETED', 'CANCELLED']

    class RecurrencePattern(models.TextChoices):
        WEEKLY = 'WEEKLY', 'Weekly'
        BIWEEKLY = 'BIWEEKLY', 'Every 2 Weeks'
        MONTHLY = 'MONTHLY', 'Monthly'
        QUARTERLY = 'QUARTERLY', 'Quarterly'
        SEMIANNUAL = 'SEMIANNUAL', 'Every 6 Months'
        ANNUAL = 'ANNUAL', 'Annual'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='schedules')

    # Event details
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    custom_event_type = models.CharField(
        max_length=100,
        blank=True,
        help_text='Custom event type when "Other" is selected'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Scheduling
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField(null=True, blank=True)
    duration_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=1.0,
        help_text='Duration in hours'
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.NEW_REQUEST,
        db_index=True
    )

    # Display order within status (for Schedule Kanban board)
    position = models.PositiveIntegerField(default=0)

    # Assignment
    assigned_to = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_schedules',
        help_text='Person assigned to this event'
    )

    # Location details
    location_notes = models.TextField(
        blank=True,
        help_text='Specific location within the property'
    )
    access_instructions = models.TextField(
        blank=True,
        help_text='Gate codes, parking info, contact on arrival, etc.'
    )

    # Equipment/preparation
    equipment_needed = models.TextField(
        blank=True,
        help_text='Tools, parts, or equipment required for this visit'
    )

    # Recurring support
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(
        max_length=20,
        choices=RecurrencePattern.choices,
        blank=True
    )
    recurrence_end_date = models.DateField(null=True, blank=True)
    parent_schedule = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recurrence_instances',
        help_text='Parent recurring schedule'
    )

    # Completion
    completed_at = models.DateTimeField(null=True, blank=True)
    completion_notes = models.TextField(
        blank=True,
        help_text='Notes from completing this event'
    )

    # Audit
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_schedules'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deal_schedules'
        verbose_name = 'Deal Schedule'
        verbose_name_plural = 'Deal Schedules'
        ordering = ['scheduled_date', 'scheduled_time']
        indexes = [
            models.Index(fields=['deal', 'scheduled_date']),
            models.Index(fields=['assigned_to', 'scheduled_date']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.scheduled_date}"

    def save(self, *args, **kwargs):
        # Auto-set completed_at when marked as completed
        if self.status == self.Status.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def display_event_type(self):
        """Return the event type for display, using custom if OTHER."""
        if self.event_type == self.EventType.OTHER and self.custom_event_type:
            return self.custom_event_type
        return self.get_event_type_display()

    @property
    def is_past_due(self):
        """Check if scheduled date has passed and not completed."""
        if self.status in [self.Status.COMPLETED, self.Status.CANCELLED]:
            return False
        return self.scheduled_date < timezone.now().date()

    @property
    def is_today(self):
        """Check if scheduled for today."""
        return self.scheduled_date == timezone.now().date()

    @property
    def is_active(self):
        """Check if schedule is in an active status."""
        return self.status in self.ACTIVE_STATUSES

    @classmethod
    def get_status_order(cls):
        """Return ordered list of statuses for Kanban display."""
        return [
            cls.Status.NEW_REQUEST,
            cls.Status.SITE_OFFICER_ASSIGNED,
            cls.Status.SCHEDULED,
            cls.Status.IN_PROGRESS,
            cls.Status.COMPLETED,
        ]

    @classmethod
    def get_active_statuses(cls):
        """Return list of active statuses for filtering."""
        return cls.ACTIVE_STATUSES


class DealComment(models.Model):
    """
    Comments on deals - separate from activity log for better UX and threading support.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='comments')

    content = models.TextField()

    # Threading support for replies
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    # Audit
    author = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='deal_comments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)

    class Meta:
        db_table = 'deal_comments'
        verbose_name = 'Deal Comment'
        verbose_name_plural = 'Deal Comments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['deal', '-created_at']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f"Comment by {self.author} on {self.deal.title}"

    def save(self, *args, **kwargs):
        # Mark as edited if content changed on update
        if self.pk:
            self.is_edited = True
        super().save(*args, **kwargs)

    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment."""
        return self.parent is not None

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Deal, DealFile, DealActivity, DealSchedule, DealComment


class DealFileInline(admin.TabularInline):
    model = DealFile
    extra = 0
    readonly_fields = ['uploaded_at', 'uploaded_by', 'file_size', 'version', 'formatted_size']
    fields = [
        'file', 'file_type', 'description', 'is_current',
        'version', 'uploaded_by', 'uploaded_at', 'formatted_size'
    ]

    def formatted_size(self, obj):
        return obj.formatted_size
    formatted_size.short_description = 'Size'


class DealActivityInline(admin.TabularInline):
    model = DealActivity
    extra = 0
    readonly_fields = [
        'activity_type', 'description', 'old_value',
        'new_value', 'user', 'created_at'
    ]
    can_delete = False
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return False


class DealScheduleInline(admin.TabularInline):
    model = DealSchedule
    extra = 0
    readonly_fields = ['created_at', 'created_by', 'completed_at']
    fields = [
        'title', 'event_type', 'scheduled_date', 'scheduled_time',
        'duration_hours', 'status', 'assigned_to', 'created_at'
    ]


class DealCommentInline(admin.TabularInline):
    model = DealComment
    extra = 0
    readonly_fields = ['author', 'created_at', 'is_edited']
    fields = ['content', 'author', 'created_at', 'is_edited']


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'client_link', 'stage', 'owner',
        'estimated_value_display', 'probability',
        'expected_close_date', 'days_in_stage_display', 'created_at'
    ]
    list_filter = ['stage', 'owner', 'estimator', 'site_officer', 'project_manager', 'created_at', 'expected_close_date']
    search_fields = ['title', 'description', 'client__company_name']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25

    readonly_fields = [
        'id', 'created_at', 'updated_at', 'stage_changed_at',
        'weighted_value_display', 'days_in_stage_display', 'age_in_days_display'
    ]

    fieldsets = (
        (None, {
            'fields': ('id', 'title', 'description', 'client')
        }),
        ('Pipeline Stage', {
            'fields': (
                'stage', 'stage_changed_at',
                'closed_lost_reason', 'declined_reason', 'close_notes'
            )
        }),
        ('Financials', {
            'fields': (
                'estimated_value', 'actual_value',
                'probability', 'weighted_value_display'
            )
        }),
        ('Dates', {
            'fields': (
                'expected_close_date', 'actual_close_date',
                'days_in_stage_display', 'age_in_days_display'
            )
        }),
        ('Assignment', {
            'fields': ('owner', 'project_manager', 'site_officer', 'estimator', 'created_by')
        }),
        ('Metadata', {
            'fields': ('position', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [DealScheduleInline, DealCommentInline, DealFileInline, DealActivityInline]

    def client_link(self, obj):
        url = reverse('admin:clients_client_change', args=[obj.client.pk])
        return format_html('<a href="{}">{}</a>', url, obj.client.company_name)
    client_link.short_description = 'Client'
    client_link.admin_order_field = 'client__company_name'

    def estimated_value_display(self, obj):
        if obj.estimated_value:
            return f"${obj.estimated_value:,.2f}"
        return "-"
    estimated_value_display.short_description = 'Est. Value'
    estimated_value_display.admin_order_field = 'estimated_value'

    def weighted_value_display(self, obj):
        return f"${obj.weighted_value:,.2f}"
    weighted_value_display.short_description = 'Weighted Value'

    def days_in_stage_display(self, obj):
        days = obj.days_in_stage
        if days > 14:
            return format_html('<span style="color: red; font-weight: bold;">{} days</span>', days)
        elif days > 7:
            return format_html('<span style="color: orange;">{} days</span>', days)
        return f"{days} days"
    days_in_stage_display.short_description = 'Days in Stage'

    def age_in_days_display(self, obj):
        return f"{obj.age_in_days} days"
    age_in_days_display.short_description = 'Deal Age'


@admin.register(DealFile)
class DealFileAdmin(admin.ModelAdmin):
    list_display = [
        'original_filename', 'deal_link', 'file_type',
        'version', 'is_current', 'formatted_size',
        'uploaded_by', 'uploaded_at'
    ]
    list_filter = ['file_type', 'is_current', 'uploaded_at']
    search_fields = ['original_filename', 'deal__title', 'deal__client__company_name']
    ordering = ['-uploaded_at']
    date_hierarchy = 'uploaded_at'

    readonly_fields = ['id', 'file_size', 'mime_type', 'uploaded_at', 'version', 'formatted_size']

    def deal_link(self, obj):
        url = reverse('admin:pipeline_deal_change', args=[obj.deal.pk])
        return format_html('<a href="{}">{}</a>', url, obj.deal.title)
    deal_link.short_description = 'Deal'

    def formatted_size(self, obj):
        return obj.formatted_size
    formatted_size.short_description = 'Size'


@admin.register(DealActivity)
class DealActivityAdmin(admin.ModelAdmin):
    list_display = [
        'deal_link', 'activity_type', 'description_short',
        'user', 'created_at'
    ]
    list_filter = ['activity_type', 'created_at']
    search_fields = ['deal__title', 'description', 'deal__client__company_name']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    readonly_fields = [
        'id', 'deal', 'activity_type', 'description',
        'old_value', 'new_value', 'user', 'created_at'
    ]

    def deal_link(self, obj):
        url = reverse('admin:pipeline_deal_change', args=[obj.deal.pk])
        return format_html('<a href="{}">{}</a>', url, obj.deal.title)
    deal_link.short_description = 'Deal'

    def description_short(self, obj):
        if len(obj.description) > 50:
            return f"{obj.description[:50]}..."
        return obj.description
    description_short.short_description = 'Description'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(DealSchedule)
class DealScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'deal_link', 'event_type', 'scheduled_date',
        'scheduled_time', 'status', 'assigned_to', 'created_at'
    ]
    list_filter = ['status', 'event_type', 'scheduled_date', 'assigned_to', 'is_recurring']
    search_fields = ['title', 'description', 'deal__title', 'deal__client__company_name']
    ordering = ['-scheduled_date', '-scheduled_time']
    date_hierarchy = 'scheduled_date'
    list_per_page = 25

    readonly_fields = ['id', 'created_at', 'updated_at', 'completed_at', 'created_by']

    fieldsets = (
        (None, {
            'fields': ('id', 'deal', 'title', 'description')
        }),
        ('Event Details', {
            'fields': (
                'event_type', 'custom_event_type',
                'scheduled_date', 'scheduled_time', 'duration_hours',
                'status', 'assigned_to'
            )
        }),
        ('Location & Equipment', {
            'fields': ('location_notes', 'access_instructions', 'equipment_needed'),
            'classes': ('collapse',)
        }),
        ('Recurring', {
            'fields': ('is_recurring', 'recurrence_pattern', 'recurrence_end_date', 'parent_schedule'),
            'classes': ('collapse',)
        }),
        ('Completion', {
            'fields': ('completed_at', 'completion_notes'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def deal_link(self, obj):
        url = reverse('admin:pipeline_deal_change', args=[obj.deal.pk])
        return format_html('<a href="{}">{}</a>', url, obj.deal.title)
    deal_link.short_description = 'Deal'
    deal_link.admin_order_field = 'deal__title'


@admin.register(DealComment)
class DealCommentAdmin(admin.ModelAdmin):
    list_display = [
        'content_short', 'deal_link', 'author', 'is_reply_display',
        'created_at', 'is_edited'
    ]
    list_filter = ['created_at', 'is_edited', 'author']
    search_fields = ['content', 'deal__title', 'deal__client__company_name', 'author__email']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25

    readonly_fields = ['id', 'created_at', 'updated_at', 'is_edited']

    fieldsets = (
        (None, {
            'fields': ('id', 'deal', 'content')
        }),
        ('Threading', {
            'fields': ('parent',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('author', 'created_at', 'updated_at', 'is_edited'),
        }),
    )

    def deal_link(self, obj):
        url = reverse('admin:pipeline_deal_change', args=[obj.deal.pk])
        return format_html('<a href="{}">{}</a>', url, obj.deal.title)
    deal_link.short_description = 'Deal'
    deal_link.admin_order_field = 'deal__title'

    def content_short(self, obj):
        if len(obj.content) > 60:
            return f"{obj.content[:60]}..."
        return obj.content
    content_short.short_description = 'Comment'

    def is_reply_display(self, obj):
        return obj.is_reply
    is_reply_display.short_description = 'Is Reply'
    is_reply_display.boolean = True

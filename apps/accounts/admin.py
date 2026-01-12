from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TimeLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for custom User model.
    """

    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['email', 'first_name', 'last_name', 'username']
    ordering = ['-created_at']

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Role & Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'is_staff', 'is_active'),
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']


@admin.register(TimeLog)
class TimeLogAdmin(admin.ModelAdmin):
    """
    Admin interface for TimeLog model.
    """

    list_display = ['user', 'date', 'session_type', 'check_in_time', 'check_out_time', 'duration_display', 'is_checked_in']
    list_filter = ['date', 'session_type', 'user']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering = ['-date', '-check_in_time']
    date_hierarchy = 'date'

    fieldsets = (
        (None, {'fields': ('user', 'date', 'session_type')}),
        ('Time Tracking', {'fields': ('check_in_time', 'check_out_time')}),
        ('Notes', {'fields': ('notes',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ['created_at', 'updated_at']

    def duration_display(self, obj):
        """Display work duration in human-readable format."""
        duration = obj.duration
        if duration:
            hours, remainder = divmod(duration.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours}h {minutes}m"
        return "-"
    duration_display.short_description = "Duration"

    def is_checked_in(self, obj):
        """Display check-in status with icons."""
        return obj.is_checked_in
    is_checked_in.boolean = True
    is_checked_in.short_description = "Currently Checked In"

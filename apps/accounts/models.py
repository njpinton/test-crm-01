import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model for CRM staff.
    Extends Django's AbstractUser to add role-based permissions.
    Uses email for authentication instead of username.
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        BD_STAFF = 'BD_STAFF', 'Business Development Staff'
        ESTIMATOR = 'ESTIMATOR', 'Estimator'

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.BD_STAFF
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Use email for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # No additional required fields for createsuperuser

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def save(self, *args, **kwargs):
        # Auto-generate username from UUID if not provided
        if not self.username:
            self.username = str(uuid.uuid4())[:30]
        super().save(*args, **kwargs)

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_estimator(self):
        return self.role == self.Role.ESTIMATOR

    @property
    def is_bd_staff(self):
        return self.role == self.Role.BD_STAFF


class TimeLog(models.Model):
    """
    Track staff check-in/check-out sessions for attendance monitoring.
    Supports multiple sessions per day (e.g., clock out for lunch, clock back in).
    """

    class SessionType(models.TextChoices):
        REGULAR = 'REGULAR', 'Regular Work'
        BREAK = 'BREAK', 'Break'
        OVERTIME = 'OVERTIME', 'Overtime'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='time_logs'
    )
    date = models.DateField(default=timezone.now)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    session_type = models.CharField(
        max_length=20,
        choices=SessionType.choices,
        default=SessionType.REGULAR
    )
    notes = models.TextField(blank=True, help_text='Optional notes about this session')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'time_logs'
        verbose_name = 'Time Log'
        verbose_name_plural = 'Time Logs'
        ordering = ['-date', '-check_in_time']
        # Allow multiple sessions per day - use indexes for query performance
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date', 'check_in_time']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.date}"

    @property
    def duration(self):
        """Calculate session duration if both check-in and check-out exist."""
        if self.check_in_time and self.check_out_time:
            return self.check_out_time - self.check_in_time
        return None

    @property
    def is_checked_in(self):
        """Check if this session is currently active (has check-in but no check-out)."""
        return self.check_in_time is not None and self.check_out_time is None

    @classmethod
    def get_total_hours_for_date(cls, user, date):
        """Calculate total work hours for a user on a specific date."""
        logs = cls.objects.filter(user=user, date=date, check_out_time__isnull=False)
        total = timezone.timedelta()
        for log in logs:
            if log.duration:
                total += log.duration
        return total

    @classmethod
    def get_active_session(cls, user):
        """Get the currently active (checked-in) session for a user."""
        return cls.objects.filter(
            user=user,
            check_in_time__isnull=False,
            check_out_time__isnull=True
        ).first()

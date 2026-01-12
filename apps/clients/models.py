import uuid
from django.db import models


class Client(models.Model):
    """
    Client/Company model for CRM.
    Represents companies or individuals that deals are associated with.
    """

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        PROSPECT = 'PROSPECT', 'Prospect'

    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Company information
    company_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    # Primary contact
    contact_name = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    contact_title = models.CharField(max_length=100, blank=True)

    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='USA')

    # Status and notes
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROSPECT
    )
    notes = models.TextField(blank=True, help_text='Internal notes about this client')

    # Metadata
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_clients'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clients'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['company_name']
        indexes = [
            models.Index(fields=['company_name']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.company_name

    @property
    def display_name(self):
        """Return company name with primary contact if available."""
        if self.contact_name:
            return f"{self.company_name} ({self.contact_name})"
        return self.company_name

    @property
    def full_address(self):
        """Return formatted full address."""
        parts = []
        if self.address_line1:
            parts.append(self.address_line1)
        if self.address_line2:
            parts.append(self.address_line2)
        city_state_zip = ', '.join(filter(None, [self.city, self.state]))
        if self.postal_code:
            city_state_zip = f"{city_state_zip} {self.postal_code}".strip()
        if city_state_zip:
            parts.append(city_state_zip)
        if self.country and self.country != 'USA':
            parts.append(self.country)
        return '\n'.join(parts)

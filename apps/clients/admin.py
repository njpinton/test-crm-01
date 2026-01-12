from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        'company_name', 'contact_name', 'contact_email',
        'status', 'deal_count', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'industry']
    search_fields = ['company_name', 'contact_name', 'contact_email']
    ordering = ['company_name']
    date_hierarchy = 'created_at'

    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('id', 'company_name', 'industry', 'website', 'status')
        }),
        ('Primary Contact', {
            'fields': ('contact_name', 'contact_title', 'contact_email', 'contact_phone')
        }),
        ('Address', {
            'fields': (
                'address_line1', 'address_line2', 'city',
                'state', 'postal_code', 'country'
            ),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def deal_count(self, obj):
        return obj.deals.count()
    deal_count.short_description = 'Deals'

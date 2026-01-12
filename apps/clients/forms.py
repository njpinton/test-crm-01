from django import forms
from .models import Client


class ClientForm(forms.ModelForm):
    """Form for creating and editing clients."""

    class Meta:
        model = Client
        fields = [
            'company_name', 'industry', 'website', 'status',
            'contact_name', 'contact_title', 'contact_email', 'contact_phone',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'notes'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Company Name'
            }),
            'industry': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'e.g. Construction, Manufacturing'
            }),
            'website': forms.URLInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'https://example.com'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'contact_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Full Name'
            }),
            'contact_title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'e.g. Project Manager'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'email@example.com'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': '(555) 123-4567'
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Street Address'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Suite, Unit, etc.'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'State'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'ZIP Code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3,
                'placeholder': 'Internal notes about this client...'
            }),
        }

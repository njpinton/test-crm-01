from django import forms
from django.contrib.auth import get_user_model
from .models import Deal, DealFile

User = get_user_model()


class DealForm(forms.ModelForm):
    """Form for creating and editing deals."""

    class Meta:
        model = Deal
        fields = [
            'title', 'description', 'client', 'stage',
            'estimated_value', 'probability', 'expected_close_date',
            'owner', 'estimator',
            'closed_lost_reason', 'declined_reason', 'close_notes', 'actual_value'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Deal Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3,
                'placeholder': 'Description of the deal...'
            }),
            'client': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'stage': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'estimated_value': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'actual_value': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'probability': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'min': 0,
                'max': 100
            }),
            'expected_close_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'date'
            }),
            'owner': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'estimator': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'closed_lost_reason': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'declined_reason': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'close_notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 2,
                'placeholder': 'Notes about why the deal was closed/declined...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter owner/estimator to active users
        self.fields['owner'].queryset = User.objects.filter(is_active=True)
        self.fields['estimator'].queryset = User.objects.filter(is_active=True)
        self.fields['estimator'].required = False


class DealCloseForm(forms.Form):
    """Form for closing a deal with reason."""
    stage = forms.ChoiceField(choices=[
        ('CLOSED_WON', 'Closed Won'),
        ('CLOSED_LOST', 'Closed Lost'),
        ('DECLINED_TO_BID', 'Declined to Bid'),
    ])

    closed_lost_reason = forms.ChoiceField(
        choices=[('', '-- Select Reason --')] + list(Deal.ClosedLostReason.choices),
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500'
        })
    )

    declined_reason = forms.ChoiceField(
        choices=[('', '-- Select Reason --')] + list(Deal.DeclinedReason.choices),
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500'
        })
    )

    actual_value = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': '0.00',
            'step': '0.01'
        })
    )

    close_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
            'rows': 2,
            'placeholder': 'Additional notes...'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        stage = cleaned_data.get('stage')

        if stage == 'CLOSED_LOST' and not cleaned_data.get('closed_lost_reason'):
            self.add_error('closed_lost_reason', 'Please select a reason for losing the deal.')

        if stage == 'DECLINED_TO_BID' and not cleaned_data.get('declined_reason'):
            self.add_error('declined_reason', 'Please select a reason for declining to bid.')

        return cleaned_data


class DealFileUploadForm(forms.ModelForm):
    """Form for uploading files to a deal."""

    class Meta:
        model = DealFile
        fields = ['file', 'file_type', 'description']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
            }),
            'file_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Brief description (optional)'
            }),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file extension
            ext = file.name.split('.')[-1].lower()
            if ext not in DealFile.ALLOWED_EXTENSIONS:
                raise forms.ValidationError(
                    f'File type .{ext} is not allowed. Allowed types: {", ".join(DealFile.ALLOWED_EXTENSIONS)}'
                )
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be less than 10MB.')
        return file

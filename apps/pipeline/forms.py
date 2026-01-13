from django import forms
from django.contrib.auth import get_user_model
from .models import Deal, DealFile, DealSchedule, DealComment

User = get_user_model()


class DealForm(forms.ModelForm):
    """Form for creating and editing deals."""

    class Meta:
        model = Deal
        fields = [
            'title', 'description', 'client', 'stage',
            'estimated_value', 'probability', 'expected_close_date',
            'owner', 'estimator', 'site_officer', 'project_manager',
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
            'site_officer': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'project_manager': forms.Select(attrs={
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
        # Filter all user fields to active users
        active_users = User.objects.filter(is_active=True)
        self.fields['owner'].queryset = active_users
        self.fields['estimator'].queryset = active_users
        self.fields['estimator'].required = False
        self.fields['site_officer'].queryset = active_users
        self.fields['site_officer'].required = False
        self.fields['project_manager'].queryset = active_users
        self.fields['project_manager'].required = False


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


class DealScheduleForm(forms.ModelForm):
    """Form for creating and editing scheduled events for a deal."""

    class Meta:
        model = DealSchedule
        fields = [
            'event_type', 'custom_event_type', 'title', 'description',
            'scheduled_date', 'scheduled_time', 'duration_hours',
            'assigned_to', 'location_notes', 'access_instructions',
            'equipment_needed', 'is_recurring', 'recurrence_pattern',
            'recurrence_end_date'
        ]
        widgets = {
            'event_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'x-model': 'eventType'
            }),
            'custom_event_type': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter custom event type',
                'x-show': "eventType === 'OTHER'"
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Event Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 2,
                'placeholder': 'Event description...'
            }),
            'scheduled_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'date'
            }),
            'scheduled_time': forms.TimeInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'time'
            }),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'step': '0.5',
                'min': '0.5',
                'placeholder': '1.0'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'location_notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 2,
                'placeholder': 'Specific location within the property...'
            }),
            'access_instructions': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 2,
                'placeholder': 'Gate codes, parking, contact on arrival...'
            }),
            'equipment_needed': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 2,
                'placeholder': 'Tools, parts, or equipment needed...'
            }),
            'is_recurring': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded',
                'x-model': 'isRecurring'
            }),
            'recurrence_pattern': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'x-show': 'isRecurring'
            }),
            'recurrence_end_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'date',
                'x-show': 'isRecurring'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        self.fields['assigned_to'].required = False
        self.fields['custom_event_type'].required = False
        self.fields['scheduled_time'].required = False
        self.fields['description'].required = False
        self.fields['location_notes'].required = False
        self.fields['access_instructions'].required = False
        self.fields['equipment_needed'].required = False
        self.fields['recurrence_pattern'].required = False
        self.fields['recurrence_end_date'].required = False

    def clean(self):
        cleaned_data = super().clean()
        event_type = cleaned_data.get('event_type')
        custom_event_type = cleaned_data.get('custom_event_type')
        is_recurring = cleaned_data.get('is_recurring')
        recurrence_pattern = cleaned_data.get('recurrence_pattern')

        if event_type == 'OTHER' and not custom_event_type:
            self.add_error('custom_event_type', 'Please specify the custom event type.')

        if is_recurring and not recurrence_pattern:
            self.add_error('recurrence_pattern', 'Please select a recurrence pattern.')

        return cleaned_data


class DealScheduleCompleteForm(forms.Form):
    """Form for marking a schedule as complete."""
    completion_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
            'rows': 3,
            'placeholder': 'Notes about the completed visit...'
        })
    )


class DealCommentForm(forms.ModelForm):
    """Form for adding comments to a deal."""

    class Meta:
        model = DealComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3,
                'placeholder': 'Add a comment...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = True

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Competitor, MonitoringConfig


class CompetitorForm(forms.ModelForm):
    class Meta:
        model = Competitor
        fields = ['name', 'website', 'description', 'industry', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('website', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'industry',
            'description',
            'is_active',
            Submit('submit', 'Add Competitor', css_class='btn btn-primary')
        )


class MonitoringConfigForm(forms.ModelForm):
    class Meta:
        model = MonitoringConfig
        fields = ['check_interval_hours', 'is_enabled', 'keywords']
        widgets = {
            'check_interval_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'is_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'keywords': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Comma-separated keywords'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'check_interval_hours',
            'is_enabled',
            'keywords',
            Submit('submit', 'Save Configuration', css_class='btn btn-primary')
        )


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter your email'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'First name (optional)'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Last name (optional)'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Choose a username'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder': 'Create a password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control form-control-lg', 'placeholder': 'Confirm your password'})



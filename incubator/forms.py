from typing import Any
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Profile

user=get_user_model()
class CustomLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, label='Remember Me')
    def __init__(self, request: Any = ..., *args: Any, **kwargs: Any) -> None:
        super().__init__(self, *args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.fields['username'].label="Username or email"
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Username or Email',
            'class': 'form-control'
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Password',
            'class': 'form-control'
        })

    def clean_username(self):
        username_or_email = self.cleaned_data['username']
        if '@' in username_or_email:
            if not user.objects.filter(email=username_or_email).exists():
                raise ValidationError("No user with this email address exists.")
        else:
            if not user.objects.filter(username=username_or_email).exists():
                raise ValidationError("No user with this username exists.")
        return username_or_email
    
class CustomSignupForm(UserCreationForm):
    role = forms.ChoiceField(choices=user.ROLE_CHOICES)
    class Meta:
        model = user
        fields = ('username', 'first_name', 'last_name', 'role','email', 'password1', 'password2')
        help_texts = {
            'username': None,
            'first_name': None,
            'last_name': None,
        }

    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['password1'].help_text = ''  
        self.fields['password2'].help_text = ''  
        self.helper.form_method = 'post'
    
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match")

        return cleaned_data
    


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'profile_picture',  # Moved to the top for better UI flow
            'bio',
            'skills',
            'education',
            'experience',
            'phone_number',
            'location',
            'linkedin',
            'twitter',
            'github',
            'status',
        ]

    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write a short bio'}),
        required=False
    )
    profile_picture = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control-file'}),
        required=False
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        required=False
    )
    location = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
        required=False
    )
    linkedin = forms.URLField(
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'LinkedIn Profile URL'}),
        required=False
    )
    twitter = forms.URLField(
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Twitter Profile URL'}),
        required=False
    )
    github = forms.URLField(
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'GitHub Profile URL'}),
        required=False
    )
    status = forms.ChoiceField(
        choices=[('Available', 'Available'), ('Not Available', 'Not Available')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    skills = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your skills'}),
        required=False
    )
    education = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your education'}),
        required=False
    )
    experience = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your experience'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_action = ''
        self.helper.add_input(Submit('submit', 'Update Profile', css_class='btn btn-primary'))

   
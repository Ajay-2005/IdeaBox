from typing import Any
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

user=get_user_model()
class CustomLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, label='Remember Me')
    def __init__(self, request: Any = ..., *args: Any, **kwargs: Any) -> None:
        super().__init__(self, *args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.add_input(Submit(
            'login', 'Sign In', css_class='btn btn-success', style="width: 100%; font-size: 1.2rem;"))


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
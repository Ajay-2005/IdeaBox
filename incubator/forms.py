from typing import Any
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class CustomLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, label='Remember Me')
    def __init__(self, request: Any = ..., *args: Any, **kwargs: Any) -> None:
        super().__init__(self, *args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.add_input(Submit(
            'login', 'Sign In', css_class='btn btn-success', style="width: 100%; font-size: 1.2rem;"))


class CustomSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        help_texts = {
            'username': None,
            'first_name':None,
            'last_name':None,
            'password1': None,
            'password2': None
        }

   
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit(
            'submit', 'Register', css_class='btn btn-success', style="width:100%;font-size:1.2rem;margin-top:5px;"))

   
    def save(self, commit=True):
        user = super(CustomSignupForm, self).save(commit=False)
        user.email = self.cleaned_data['email']  
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user
    

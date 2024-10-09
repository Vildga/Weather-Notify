from django import forms
from .models import Subscription
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


class CitySearchForm(forms.Form):
    search_query = forms.CharField(label='Search for a city', max_length=100)


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['city', 'period', 'method']


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        help_texts = {
            'username': None,
            'password1': '',
            'password2': '',
        }


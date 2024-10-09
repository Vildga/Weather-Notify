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
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'A user with the username {username} already exists.')
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        try:
            validate_password(password1)
        except ValidationError as e:
            raise forms.ValidationError('\n'.join(e.messages))

        return password1

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f'A user with the email {email} already exists.')
        return email


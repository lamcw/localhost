from django import forms
from django.contrib.auth.forms import UserCreationForm

from placeholder.authentication.models import User


class DatePicker(forms.DateInput):
    input_type = 'date'


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            'dob',
            'gender',
        )
        widgets = {
            'dob': DatePicker(),
            'gender': forms.RadioSelect(),
        }

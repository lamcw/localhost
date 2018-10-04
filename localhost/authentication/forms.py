from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class DatePicker(forms.DateInput):
    input_type = 'date'


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
            'dob',
            'gender',
        )
        widgets = {
            'dob': DatePicker(),
            'gender': forms.RadioSelect(),
        }

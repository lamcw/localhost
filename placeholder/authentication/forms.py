from django import forms
from django.contrib.auth.forms import UserCreationForm

from placeholder.authentication.models import User


class DatePicker(forms.DateInput):
    input_type = 'date'


class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self:
            field.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            'bio',
            'dob',
            'gender',
        )
        widgets = {
            'dob': DatePicker(),
        }

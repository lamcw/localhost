from datetime import datetime, time, timedelta

from django import forms
from django.contrib.auth import get_user_model
from django.forms.models import ModelForm, inlineformset_factory
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from localhost.core.models import Property, PropertyItem, PropertyItemReview
from localhost.core.utils import parse_address

User = get_user_model()


class DatePicker(forms.DateInput):
    input_type = 'date'


class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = (
            'bio',
            'dob',
            'gender',
        )
        widgets = {
            'bio': forms.Textarea(attrs={
                'cols': 100,
                'rows': 3
            }),
            'dob': DatePicker(),
            'gender': forms.RadioSelect(),
        }


class PropertyItemForm(ModelForm):
    img = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        label='Photos',
        required=False)

    class Meta:
        model = PropertyItem
        fields = '__all__'
        exclude = ('highest_bidder', )


class PropertyForm(ModelForm):
    # TIME_CHOICE in this format [(time object, time in string)]
    TIME_CHOICE = [((datetime.combine(timezone.now(), time()) +
                     timedelta(minutes=i * 30)).time(),
                    (datetime.combine(timezone.now(), time()) +
                     timedelta(minutes=i * 30)).strftime('%H:%M'))
                   for i in range(48)]
    earliest_checkin_time = forms.ChoiceField(
        choices=TIME_CHOICE, help_text=_('Earliest check-in time.'))
    latest_checkin_time = forms.ChoiceField(
        choices=TIME_CHOICE, help_text=_('Latest check-in time.'))
    img = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        label='Photos',
        required=False)

    class Meta:
        model = Property
        exclude = ('host', )

    def clean(self):
        """
        Clean latest_checkin_time and earliest_checkin_time.

        Ensure that earliest_checkin_time < latest_checkin_time.
        """
        cleaned_data = super().clean()
        earliest_checkin_time = cleaned_data.get('earliest_checkin_time')
        latest_checkin_time = cleaned_data.get('latest_checkin_time')
        if (earliest_checkin_time and latest_checkin_time
                and earliest_checkin_time > latest_checkin_time):
            raise forms.ValidationError(
                _('Invalid check-in time: %(earliest)s > %(latest)s'),
                code='invalid-time',
                params={
                    'earliest': earliest_checkin_time,
                    'latest': latest_checkin_time
                })

    def save(self, commit=True):
        new_property = super().save(commit=False)
        new_property.latitude, new_property.longitude = parse_address(
            self.cleaned_data.get('address'))
        if commit:
            new_property.save()
        return new_property


class WalletForm(forms.Form):
    recharge_amount = forms.IntegerField(
        min_value=1, max_value=9223372036854775807)

    class Meta:
        labels = {
            'recharge_amount': 'Add money to wallet',
        }


class PropertyItemReviewForm(ModelForm):
    class Meta:
        model = PropertyItemReview
        fields = (
            'rating',
            'description',
        )
        labels = {
            'description': 'Leave a review...',
        }
        widgets = {
            'rating': forms.HiddenInput(),
        }


PropertyItemFormSet = inlineformset_factory(
    Property, PropertyItem, form=PropertyItemForm, extra=1)

from django import forms
from django.contrib.auth import get_user_model
from django.forms.models import ModelForm, inlineformset_factory
from django.utils.translation import gettext_lazy as _

from localhost.core.models import Property, PropertyItem
from localhost.core.utils import parse_address

User = get_user_model()


class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ('bio', )
        widgets = {
            'bio': forms.Textarea(attrs={
                'cols': 100,
                'rows': 3
            }),
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


PropertyItemFormSet = inlineformset_factory(
    Property, PropertyItem, form=PropertyItemForm, extra=1)

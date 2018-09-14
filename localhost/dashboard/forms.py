import googlemaps
from django import forms
from django.conf import settings
from django.forms.models import ModelForm, inlineformset_factory
from django.utils.translation import gettext_lazy as _

from localhost.core.models import Property, PropertyItem, PropertyItemReview


class PropertyItemReviewForm(ModelForm):
    class Meta:
        model = PropertyItemReview
        exclude = ('booking', )


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
        gmaps = googlemaps.Client(key=settings.GMAPS_KEY)
        address = self.cleaned_data.get('address')
        geocode = gmaps.geocode(address)
        new_property.latitude = geocode[0]['geometry']['location']['lat']
        new_property.longitude = geocode[0]['geometry']['location']['lng']
        if commit:
            new_property.save()
        return new_property


PropertyItemFormSet = inlineformset_factory(
    Property, PropertyItem, form=PropertyItemForm, extra=1)

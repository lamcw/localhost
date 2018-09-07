import googlemaps
from django.conf import settings
from django.forms.models import (BaseInlineFormSet, ModelForm,
                                 inlineformset_factory)

from localhost.core.models import (Property, PropertyImage, PropertyItem,
                                   PropertyItemImage)


class PropertyItemForm(ModelForm):
    class Meta:
        model = PropertyItem
        fields = '__all__'
        exclude = ('highest_bidder', )


class PropertyForm(PropertyItemForm):
    class Meta:
        model = Property
        exclude = (
            'host',
            'latitude',
            'longitude',
        )

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


PropertyItemImageFormSet = inlineformset_factory(
    PropertyItem,
    PropertyItemImage,
    fields=('img', ),
    labels={'img': 'photo'},
    extra=1)

PropertyImageFormSet = inlineformset_factory(
    Property,
    PropertyImage,
    fields=('img', ),
    labels={'img': 'photo'},
    extra=1)


class BasePropertyItemFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        """
        Add extra Image formset for each room.
        """
        super().add_fields(form, index)

        form.image_formset = PropertyItemImageFormSet(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix=
            f"image-{form.prefix}-{PropertyItemImageFormSet.get_default_prefix()}"
        )

    def is_valid(self):
        """
        Validate image formsets.
        """
        result = super().is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'image_formset'):
                    result = result and form.image_formset.is_valid()
        return result

    def save(self, commit=True):
        """
        Save image formsets.
        """
        result = super().save(commit=commit)

        for form in self.forms:
            if hasattr(form, 'image_formset'):
                if not self._should_delete_form(form):
                    form.image_formset.save(commit=commit)
        return result


PropertyItemFormSet = inlineformset_factory(
    Property,
    PropertyItem,
    form=PropertyItemForm,
    formset=BasePropertyItemFormSet,
    extra=1)

import googlemaps
from django.conf import settings
from django import forms
from django.forms.models import (BaseInlineFormSet, ModelForm,
                                 inlineformset_factory)

from localhost.core.models import (Bed, Property, PropertyItem,
                                     PropertyItemImage, Room)


class PropertyItemForm(ModelForm):
    class Meta:
        model = PropertyItem
        fields = '__all__'
        exclude = ('highest_bidder', 'open_for_auction')


class PropertyForm(PropertyItemForm):
    class Meta(PropertyItemForm.Meta):
        model = Property
        exclude = PropertyItemForm.Meta.exclude + (
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


class RoomForm(PropertyItemForm):
    class Meta(PropertyItemForm.Meta):
        model = Room
        exclude = PropertyItemForm.Meta.exclude + ('property_ptr', )


class BedForm(PropertyItemForm):
    class Meta(PropertyItemForm.Meta):
        model = Bed
        exclude = PropertyItemForm.Meta.exclude + ('room_ptr', )


PropertyItemImageFormSet = inlineformset_factory(
    PropertyItem,
    PropertyItemImage,
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


class BaseRoomFormSet(BasePropertyItemFormSet):
    def add_fields(self, form, index):
        """
        Add extra Bed formset for each room.
        """
        super().add_fields(form, index)

        form.nested = BedFormSet(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix=f"bed-{form.prefix}-{BedFormSet.get_default_prefix()}")

    def is_valid(self):
        """
        Validate nested formsets.
        """
        result = super().is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()
        return result

    def save(self, commit=True):
        """
        Save nested formsets.
        """
        result = super().save(commit=commit)

        for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)
        return result


BedFormSet = inlineformset_factory(
    Room,
    Bed,
    formset=BasePropertyItemFormSet,
    form=BedForm,
    fk_name='room_ptr',
    extra=1)

RoomFormSet = inlineformset_factory(
    Property,
    Room,
    formset=BaseRoomFormSet,
    form=RoomForm,
    fk_name='property_ptr',
    extra=1)

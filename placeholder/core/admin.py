from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.postgres.forms import RangeWidget
from placeholder.core.models import (Amenity, Bed, Booking, Property,
                                     PropertyItem, Room)
from polymorphic.admin import (PolymorphicChildModelAdmin,
                               PolymorphicParentModelAdmin)


class PropertyItemChildAdmin(PolymorphicChildModelAdmin):
    base_model = PropertyItem


@admin.register(Property)
class PropertyAdmin(PropertyItemChildAdmin):
    base_model = Property


@admin.register(Room)
class RoomAdmin(PropertyItemChildAdmin):
    base_model = Room


@admin.register(Bed)
class BedAdmin(PropertyItemChildAdmin):
    base_model = Bed


@admin.register(PropertyItem)
class PropertyItemAdmin(PolymorphicParentModelAdmin):
    base_model = PropertyItem
    child_models = (Property, Room, Bed)


class BookingAdminForm(forms.ModelForm):
    class Meta:
        model = Booking
        widgets = {'period': RangeWidget(AdminDateWidget())}
        fields = '__all__'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    form = BookingAdminForm


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    pass

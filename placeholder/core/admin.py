from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.postgres.forms import RangeWidget
from polymorphic.admin import (PolymorphicChildModelAdmin,
                               PolymorphicParentModelAdmin)

from placeholder.core.models import (Amenity, Bed, Booking, Property,
                                     PropertyItem, Room, PropertyItemImage)


class BedInline(admin.StackedInline):
    model = Bed
    fk_name = 'room_ptr'
    readonly_fields = ['room_ptr']
    extra = 1


class RoomInline(admin.StackedInline):
    model = Room
    fk_name = 'property_ptr'
    readonly_fields = ['property_ptr']
    show_change_link = True
    extra = 1


class ImageInline(admin.StackedInline):
    model = PropertyItemImage
    extra = 1


class PropertyItemChildAdmin(PolymorphicChildModelAdmin):
    base_model = PropertyItem
    inlines = [ImageInline]


@admin.register(Property)
class PropertyAdmin(PropertyItemChildAdmin):
    base_model = Property
    show_in_index = True
    inlines = PropertyItemChildAdmin.inlines + [RoomInline]


@admin.register(Room)
class RoomAdmin(PropertyItemChildAdmin):
    base_model = Room
    inlines = PropertyItemChildAdmin.inlines + [BedInline]


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

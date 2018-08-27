from django.contrib import admin
from polymorphic.admin import (PolymorphicChildModelAdmin,
                               PolymorphicParentModelAdmin)

from placeholder.core.models import Bed, Property, PropertyItem, Room


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

from django.contrib import admin

from localhost.core.models import (Amenity, BiddingSession, Booking, Property,
                                   PropertyImage, PropertyItem,
                                   PropertyItemImage)


class PropertyItemImageInline(admin.StackedInline):
    model = PropertyItemImage


class PropertyImageInline(admin.StackedInline):
    model = PropertyImage
    extra = 1


class PropertyItemInline(admin.StackedInline):
    model = PropertyItem
    extra = 1
    readonly_fields = [
        'highest_bidder',
    ]
    # TODO nested inline with image


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    inlines = [PropertyItemInline, PropertyImageInline]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    pass


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    pass


@admin.register(BiddingSession)
class BiddingSessionAdmin(admin.ModelAdmin):
    pass

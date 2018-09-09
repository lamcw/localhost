from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel
from polymorphic.showfields import ShowFieldType


class Amenity(models.Model):
    item = models.CharField(max_length=15, unique=True)

    class Meta:
        verbose_name_plural = 'amenities'

    def __str__(self):
        return f"{self.item}"


class BiddingSession(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"""{self.start_time.strftime('%I:%M %p')} -
            {self.end_time.strftime('%I:%M %p')}"""


class Property(models.Model):
    host = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(
        _('title'), max_length=100, help_text=_('Character limit: 100'))
    description = models.TextField(
        _('description'), max_length=600, help_text=_('Character limit: 600'))
    address = models.CharField(
        _('address'), max_length=200, help_text=_('Address of this property.'))
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    earliest_checkin_time = models.TimeField(
        _('earliest check-in time'),
        help_text=_('Earliest time a guest can check-in.'))
    latest_checkin_time = models.TimeField(
        _('latest check-in time'),
        help_text=_('Latest time a guest can check-in.'))
    session = models.ManyToManyField(
        BiddingSession,
        verbose_name=_('bidding session'),
        blank=True,
        help_text=_('Choose a session to enable bidding during those times.'))

    class Meta:
        verbose_name_plural = 'properties'

    def __str__(self):
        return f"Property: {self.title} owned by {self.host}"


class PropertyItem(models.Model):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='property_item')
    title = models.CharField(
        _('title'), max_length=100, help_text=_('Character limit: 100'))
    description = models.TextField(
        _('description'), max_length=600, help_text=_('Character limit: 600'))
    min_price = models.PositiveIntegerField(
        _('min price'), help_text=_('Starting price of the auction.'))
    buyout_price = models.PositiveIntegerField(
        _('buyout price'), help_text=_('Buyout price during auction.'))
    highest_bidder = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    amenities = models.ManyToManyField(
        Amenity, blank=True, help_text=_('Amenities in this place.'))
    capacity = models.PositiveIntegerField()
    bindable = models.BooleanField(
        default=True, help_text=_('Enable binding bids.'))

    def __str__(self):
        return f"{self.title}"


def property_item_img_path(instance, filename):
    """
    File will be uploaded to
    MEDIA_ROOT/user_<id>/property_item_<property_item_id>/<filename>
    """
    return f"user_{instance.property_item.property.host.id}/property_item_{instance.property_item.id}/{filename}"


def property_img_path(instance, filename):
    """
    File will be uploaded to
    MEDIA_ROOT/user_<id>/property_<property_item_id>/<filename>
    """
    return f"user_{instance.property.host.id}/property_{instance.property.id}/{filename}"


class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='images')
    img = models.ImageField(upload_to=property_img_path)


class PropertyItemImage(models.Model):
    property_item = models.ForeignKey(
        PropertyItem, on_delete=models.CASCADE, related_name='images')
    img = models.ImageField(upload_to=property_item_img_path)


class Booking(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    property_item = models.ForeignKey(PropertyItem, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(_('price'))

    def __str__(self):
        return f"{self.user} booked {self.property_item}"


class Review(ShowFieldType, PolymorphicModel):
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(6)])
    description = models.TextField(_('description'))

    class Meta:
        abstract = True


class PropertyItemReview(Review):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)


class UserReview(Review):
    reviewer = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

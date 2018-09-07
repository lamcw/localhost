from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import DateRangeField
from django.core.validators import MinValueValidator
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


class PropertyItem(ShowFieldType, PolymorphicModel):
    title = models.CharField(_('title'), max_length=40)
    description = models.TextField(_('description'), max_length=200)
    price = models.DecimalField(
        _('price'),
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.0'))])
    buyout_price = models.DecimalField(
        _('buyout price'),
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.0'))],
        help_text=_('buyout price during auction.'))
    highest_bidder = models.OneToOneField(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    open_for_auction = models.BooleanField(default=False)
    amenities = models.ManyToManyField(Amenity, blank=True)
    capacity = models.PositiveIntegerField(blank=True)

    def __str__(self):
        return f"{self.title}"


class Property(PropertyItem):
    host = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    address = models.CharField(
        _('address'), max_length=150, help_text=_('address of this property.'))
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)

    class Meta:
        verbose_name_plural = 'properties'

    def __str__(self):
        return f"Property: {self.title} owned by {self.host}"


class Room(PropertyItem):
    property_ptr = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='room')

    def __str__(self):
        return f"Room in {self.property_ptr}"


class Bed(PropertyItem):
    room_ptr = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='bed')

    def __str__(self):
        return f"Bed in {self.room_ptr}"


def user_directory_path(instance, filename):
    """
    File will be uploaded to
    MEDIA_ROOT/user_<id>/property_item_<property_item_id>/<filename>
    """
    return f"user_{instance.user.id}/property_item_{instance.property_item.id}/{filename}"


class PropertyItemImage(models.Model):
    property_item = models.ForeignKey(PropertyItem, on_delete=models.CASCADE)
    img = models.ImageField(upload_to=user_directory_path)


class Booking(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    property_item = models.ForeignKey(PropertyItem, on_delete=models.CASCADE)
    price = models.DecimalField(
        _('price'),
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.0'))])
    period = DateRangeField(_('period'), help_text=_('booking period.'))
    CART = 'C'
    PAID = 'P'
    STATUS_CHOCIE = (
        (CART, 'Cart'),
        (PAID, 'Paid'),
    )
    status = models.CharField(
        max_length=1, choices=STATUS_CHOCIE, default=CART)

    def __str__(self):
        return f"{self.user} booked {self.property_item}"


class Review(PolymorphicModel):
    rating = models.IntegerField(choices=[(i, i) for i in range(6)])
    description = models.TextField(_('description'))

    class Meta:
        abstract = True


class PropertyItemReview(Review):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)


class UserReview(Review):
    reviewer = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

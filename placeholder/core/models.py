from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel


class PropertyItem(PolymorphicModel):
    price = models.DecimalField(_('price'), max_digits=8, decimal_places=2)
    buyout_price = models.DecimalField(
        _('buyout price'),
        max_digits=8,
        decimal_places=2,
        help_text=_('buyout price during auction')
    )
    title = models.CharField(_('title'), max_length=40)
    description = models.TextField(_('description'), max_length=200)
    highest_bidder = models.OneToOneField(
        get_user_model(),
        null=True,
        on_delete=models.SET_NULL
    )
    open_for_auction = models.BooleanField(default=False)


class Property(PropertyItem):
    host = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        related_name='%(class)s'
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)

    def __str__(self):
        return f"Listing: {self.title} by {self.host}"


class Room(PropertyItem):
    property_ptr = models.ForeignKey(Property, on_delete=models.CASCADE)


class Bed(PropertyItem):
    room_ptr = models.ForeignKey(Room, on_delete=models.CASCADE)


class Amenity(models.Model):
    property_item = models.ManyToManyField(Room)
    item = models.CharField(max_length=15)

    def __str__(self):
        return f"Amenity: {self.items}"


class PropertyItemImage(models.Model):
    property_item = models.ForeignKey(PropertyItem, on_delete=models.CASCADE)
    img = models.ImageField()


class Booking(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    property_item = models.ForeignKey(PropertyItem, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    checkin_date = models.DateField()
    checkout_date = models.DateField()
    CART = 'C'
    PAID = 'P'
    STATUS_CHOCIE = (
        (CART, 'Cart'),
        (PAID, 'Paid'),
    )
    status = models.CharField(
        max_length=1, choices=STATUS_CHOCIE, default=CART)


class Review(models.Model):
    rating = models.IntegerField(choices=[(i, i) for i in range(6)])
    description = models.TextField(_('description'))

    class Meta:
        abstract = True


class PropertyItemReview(Review):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)


class UserReview(Review):
    reviewer = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

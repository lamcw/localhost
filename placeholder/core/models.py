from django.db import models

from placeholder.authentication.models import User


class Listing(models.Model):
    host = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=70)
    description = models.TextField(max_length=200)
    # latitude = TODO
    # longitude = TODO

    def __str__(self):
        return f"Listing: {self.title} by {self.host}"


class TTB(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    BED = 'B'
    ROOM = 'R'
    PROPERTY = 'P'
    TYPE_CHOICES = (
        (BED, 'Bed'),
        (ROOM, 'Room'),
        (PROPERTY, 'Entire Property'),
    )
    ttb_type = models.CharField(
        max_length=1, choices=TYPE_CHOICES, default=ROOM)
    price = models.DecimalField()
    buyout_price = models.DecimalField()
    rating = models.IntegerField(choices=[(i, i) for i in range(6)])
    title = models.CharField(max_length=40)
    description = models.TextField(max_length=200)
    highest_bidder = models.OneToOneField(User)


class Amenity(models.Model):
    ttb = models.ManyToManyField(TTB)
    item = models.CharField(max_length=15)

    def __str__(self):
        return f"Amenity: {self.items}"


class Image(models.Model):
    img = models.ImageField()

    class Meta:
        abstract = True


class TTBImage(Image):
    ttb = models.OneToOneField(TTB)


class ListingImage(Image):
    listing = models.OneToOneField(Listing)


class Booking(models.Model):
    user = models.OneToOneField(User)
    ttb = models.ForeignKey(TTB, on_delete=models.PROTECT)
    price = models.DecimalField()
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

from django.contrib.auth import get_user_model
from django.db import models


class Property(models.Model):
    host = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    title = models.CharField(max_length=70)
    description = models.TextField(max_length=200)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)

    def __str__(self):
        return f"Listing: {self.title} by {self.host}"


class PropertyItem(models.Model):
    listing = models.ForeignKey(Property, on_delete=models.CASCADE)
    BED = 'B'
    ROOM = 'R'
    PROPERTY = 'P'
    TYPE_CHOICES = (
        (BED, 'Bed'),
        (ROOM, 'Room'),
        (PROPERTY, 'Entire Property'),
    )
    item_type = models.CharField(
        max_length=1, choices=TYPE_CHOICES, default=ROOM)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    buyout_price = models.DecimalField(max_digits=8, decimal_places=2)
    rating = models.IntegerField(choices=[(i, i) for i in range(6)])
    title = models.CharField(max_length=40)
    description = models.TextField(max_length=200)
    highest_bidder = models.ForeignKey(
        get_user_model(), null=True, on_delete=models.SET_NULL)
    open_for_auction = models.BooleanField(default=False)


class Amenity(models.Model):
    property_item = models.ManyToManyField(PropertyItem)
    item = models.CharField(max_length=15)

    def __str__(self):
        return f"Amenity: {self.items}"


class Image(models.Model):
    img = models.ImageField()

    class Meta:
        abstract = True


class PropertyItemImage(Image):
    property_item = models.ForeignKey(PropertyItem, on_delete=models.CASCADE)


class ListingImage(Image):
    listing = models.ForeignKey(Property, on_delete=models.CASCADE)


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
    description = models.TextField()

    class Meta:
        abstract = True


class PropertyItemReview(Review):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)


class UserReview(Review):
    reviewer = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

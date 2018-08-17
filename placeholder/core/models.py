from django.db import models


class Listing(models.Model):
    host = models.ForeignKey('User')
    title = models.CharField(max_length=70)
    description = models.TextField(max_length=200)
    # latitude = TODO
    # longitude = TODO


class TTB(models.Model):
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE)
    BED = 'B'
    ROOM = 'R'
    PROPERTY = 'P'
    TYPE_CHOICES = (
        (BED, 'Bed'),
        (ROOM, 'Room'),
        (PROPERTY, 'Entire Property'),
    )
    ttb_type = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES,
        default=ROOM
    )
    price = models.DecimalField()
    buyout_price = models.DecimalField()
    rating = models.IntegerField(choices=[(i, i) for i in range(6)])
    title = models.CharField(max_length=20)
    description = models.TextField(max_length=200)
    highest_bidder = models.OneToOneField(User)


class TTBImage(models.Model):
    pass

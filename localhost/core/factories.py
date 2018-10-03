import datetime

import factory
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model

from localhost.core import models
from localhost.authentication.factories import UserFactory

User = get_user_model()


class PropertyItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.PropertyItem

    title = 'a'
    description = 'b'
    min_price = 50
    buyout_price = 70
    capacity = 5


class PropertyFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Property

    host = factory.SubFactory(UserFactory)
    property_item = factory.RelatedFactory(PropertyItemFactory, 'property')
    title = 'a'
    description = 'b'
    address = 'c'
    latitude = factory.Faker(
        'geo_coordinate',
        center=settings.DEFAULT_SEARCH_COORD[0],
        radius=0.001)
    longitude = factory.Faker(
        'geo_coordinate',
        center=settings.DEFAULT_SEARCH_COORD[1],
        radius=0.001)
    earliest_checkin_time = factory.Faker(
        'date_time_this_year', tzinfo=timezone.get_current_timezone())
    latest_checkin_time = factory.LazyAttribute(
        lambda o: o.earliest_checkin_time + datetime.timedelta(hours=5))


class BookingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Booking

    user = factory.Iterator(User.objects.all())
    property_item = factory.Iterator(models.PropertyItem.objects.all())
    price = 70
    earliest_checkin_time = factory.Faker(
        'date_time_between_dates',
        datetime_start=timezone.make_aware(datetime.datetime(2018, 9, 1)),
        datetime_end=timezone.make_aware(datetime.datetime(2018, 10, 10)),
        tzinfo=timezone.get_current_timezone())
    latest_checkin_time = factory.LazyAttribute(
        lambda o: o.earliest_checkin_time + datetime.timedelta(hours=6))


class PropertyItemReviewFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.PropertyItemReview

    booking = factory.Iterator(models.Booking.objects.all())
    rating = factory.Iterator([x for x in range(6)])
    description = factory.Faker(
        'paragraph', nb_sentences=3, variable_nb_sentences=True)

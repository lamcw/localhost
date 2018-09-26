import datetime

import factory
from django.utils import timezone
from django.conf import settings

from localhost.core import models
from localhost.authentication.factories import UserFactory


class PropertyItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.PropertyItem

    title = factory.Faker('sentence', nb_words=6)
    description = factory.Faker('text', max_nb_chars=600)
    min_price = 50
    buyout_price = 70
    capacity = 5


class PropertyImageFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.PropertyImage

    img = factory.django.ImageField()


class PropertyFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Property

    host = factory.SubFactory(UserFactory)
    property_item = factory.RelatedFactory(PropertyItemFactory, 'property')
    title = factory.Faker('sentence', nb_words=6)
    description = factory.Faker('text', max_nb_chars=600)
    address = factory.Faker('address')
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
    images = factory.RelatedFactory(PropertyImageFactory, 'property')

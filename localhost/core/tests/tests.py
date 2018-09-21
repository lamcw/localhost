import factory
import datetime
from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from localhost.core import models


class PropertyItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.PropertyItem

    title = factory.Faker('sentence')
    description = factory.Faker('text')
    min_price = factory.Faker()


class PropertyFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Property

    title = factory.Faker('sentence')
    description = factory.Faker('text')
    address = factory.Faker('address')
    latitude, longitude = settings.DEFAULT_SEARCH_COORD
    earliest_checkin_time = factory.Faker(
        'date_time', tz_info=timezone.get_current_timezone())
    latest_checkin_time = factory.LazyAttribute(
        lambda t: t + datetime.timedelta(hours=5))

    property_item = factory.RelatedFactory(
        PropertyItemFactory,
        'property',
        action=models.PropertyItem.ACTION_CREATE)

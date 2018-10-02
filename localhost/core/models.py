import json
import logging

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import IntegrityError, models
from django.db.models.signals import m2m_changed, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from polymorphic.models import PolymorphicModel
from polymorphic.showfields import ShowFieldType

logger = logging.getLogger(__name__)


class Amenity(models.Model):
    item = models.CharField(max_length=15, unique=True)
    icon = models.CharField(
        max_length=30,
        validators=[
            RegexValidator(
                regex=r'^fa-[\w]*',
                message=_('Icon class must starts with \"fa-\"'))
        ],
        help_text=_('Font Awesome glyph class.'))

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


class Sin(models.Func):
    function = 'SIN'


class Cos(models.Func):
    function = 'COS'


class Acos(models.Func):
    function = 'ACOS'


class Radians(models.Func):
    function = 'RADIANS'


class DistanceManager(models.Manager):
    """
    Custom manager that adds functions related to geographical distance.
    """

    def within(self, latitude, longitude):
        """
        Returns the distance between two locations given latitude and
        longitude. The distance is calculated using Haversine Formula. See
        https://en.wikipedia.org/wiki/Haversine_formula
        The model that this manager handles must have a latitude and longitutde
        field.

        Usage:
        >>> class Foo(models.Model):
        >>>     latitude = models.DecimalField()
        >>>     longitude = models.DecimalField()
        >>>     objects = DistanceManager()

        >>> Foo.objects.within(lat, lng)
        <QuerySet [<Foo: ...>]>

        Args:
            latitude: latitude of the given location
            longitude: longitude of the given location
        Returns:
            queryset with annotated distance between the given location and
            objects
        """
        radlat = Radians(latitude)  # given latitude
        radlong = Radians(longitude)  # given longitude
        radflat = Radians(models.F('latitude'))
        radflong = Radians(models.F('longitude'))

        # 6371 is for km. Use 3959 for miles
        expr = 6371 * Acos(
            Cos(radlat) * Cos(radflat) * Cos(radflong - radlong) +
            Sin(radlat) * Sin(radflat))

        return self.get_queryset().annotate(distance=expr)


class Property(models.Model):
    host = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(
        _('title'), max_length=100, help_text=_('Character limit: 100'))
    description = models.TextField(
        _('description'), max_length=600, help_text=_('Character limit: 600'))
    address = models.CharField(
        _('address'), max_length=200, help_text=_('Address of this property.'))
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, editable=False)
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, editable=False)
    earliest_checkin_time = models.TimeField(
        _('earliest check-in time'),
        help_text=_('Earliest time a guest can check-in.'))
    latest_checkin_time = models.TimeField(
        _('latest check-in time'),
        help_text=_('Latest time a guest can check-in.'))

    objects = DistanceManager()

    class Meta:
        verbose_name_plural = 'properties'

    def get_absolute_url(self):
        return reverse('core:property-detail', args=[str(self.id)])

    def __str__(self):
        return f"Property: {self.title} owned by {self.host} ({self.longitude}, {self.latitude})"


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
    session = models.ManyToManyField(
        BiddingSession,
        verbose_name=_('bidding session'),
        blank=True,
        help_text=_('Choose a session to enable bidding during those times.'))
    amenities = models.ManyToManyField(
        Amenity, blank=True, help_text=_('Amenities in this place.'))
    capacity = models.PositiveIntegerField()
    bindable = models.BooleanField(
        default=True, help_text=_('Enable binding bids.'))
    available = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('core:property-item-detail', args=[str(self.id)])

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


class Bid(models.Model):
    property_item = models.ForeignKey(
        PropertyItem, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    class Meta:
        get_latest_by = 'amount'


class Booking(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    property_item = models.ForeignKey(PropertyItem, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(_('price'))
    earliest_checkin_time = models.DateTimeField(_('earliest check-in time'))
    latest_checkin_time = models.DateTimeField(_('latest check-in time'))

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
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='received_reviews')


@receiver(m2m_changed, sender=PropertyItem.session.through)
def property_item_m2m_changed(instance, action, pk_set, **kwargs):
    sessions = BiddingSession.objects.filter(id__in=pk_set)
    if action == 'post_add':
        for session in sessions:
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=session.end_time.minute, hour=session.end_time.hour)
            PeriodicTask.objects.get_or_create(
                crontab=schedule,
                task='localhost.core.tasks.cleanup_bids',
                name=f'PropertyItem<{instance.id}> cleanup bids {session.end_time}',
                args=json.dumps([instance.id]))
    elif action == 'post_remove':
        names = [
            f'PropertyItem<{instance.id}> cleanup bids {session.end_time}'
            for session in sessions
        ]
        PeriodicTask.objects.filter(name__in=names).delete()


@receiver(pre_save, sender=PropertyItem)
def property_item_pre_save(sender, instance, **kwargs):
    schedule, _ = CrontabSchedule.objects.get_or_create(hour=12)
    try:
        PeriodicTask.objects.get_or_create(
            crontab=schedule,
            task='localhost.core.tasks.enable_bids',
            name=f'Daily bids enable {instance.id}',
            args=json.dumps([instance.id]))
    except IntegrityError as e:
        logger.exception('Task already exists. Task creation ignored.', e)

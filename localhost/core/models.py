import json
import logging

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import IntegrityError, models
from django.db.models import F, Q
from django.db.models.signals import m2m_changed, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import (CrontabSchedule, PeriodicTask,
                                       PeriodicTasks)

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

    @classmethod
    def current_session_of(cls, property_item):
        now = timezone.localtime().time()
        qs1 = cls.objects.filter(
            Q(start_time__lte=F('end_time')),
            Q(start_time__lte=now),
            end_time__gte=now,
            propertyitem=property_item)
        qs2 = cls.objects.filter(
            Q(start_time__gt=F('end_time')),
            Q(start_time__lte=now)
            | Q(end_time__gte=now),
            propertyitem=property_item)
        return qs1.union(qs2).first()

    def __str__(self):
        return f"""{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"""


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
            latitude: Latitude of the given location
            longitude: Longitude of the given location

        Returns:
            A queryset with annotated distance between the given location and
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
        return reverse('core:property-detail', args=[str(self.property.id)])

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


class PropertyItemReview(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(6)])
    description = models.TextField(_('description'))


class Notification(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    OUTBID = 'O'
    WON_BID = 'W'
    MESSAGE_CHOICES = (
           (OUTBID, 'You have been outbid!'),
           (WON_BID, 'You have won your auction!')
    )
    message = models.CharField(
            _('message'),
            max_length=1,
            choices=MESSAGE_CHOICES,
    )
    property_item = models.ForeignKey(PropertyItem, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)


@receiver(m2m_changed, sender=PropertyItem.session.through)
def property_item_m2m_changed(instance, action, pk_set, **kwargs):
    """
    Add/remove cleanup task when session has been added to/removed from the
    property item.
    """
    sessions = BiddingSession.objects.filter(id__in=pk_set)
    if action == 'post_add':
        for i, session in enumerate(sessions):
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=session.end_time.minute,
                hour=session.end_time.hour)
            PeriodicTask.objects.get_or_create(
                crontab=schedule,
                task='localhost.core.tasks.cleanup_bids',
                name=f'PropertyItem-{instance.id} bids cleanup {i}',
                args=json.dumps([instance.id]))
    elif action == 'post_remove':
        names = [
            f'PropertyItem-{instance.id} bids cleanup {i}'
            for session in sessions
        ]
        PeriodicTask.objects.filter(name__in=names).delete()


@receiver(pre_save, sender=PropertyItem)
def property_item_pre_save(instance, **kwargs):
    """
    Enable bids every day at 12nn.
    """
    schedule, _ = CrontabSchedule.objects.get_or_create(hour=12, minute=0)
    try:
        PeriodicTask.objects.get_or_create(
            crontab=schedule,
            task='localhost.core.tasks.enable_bids',
            name=f'Daily bids enable {instance.id}',
            args=json.dumps([instance.id]))
    except IntegrityError as e:
        logger.info('Task already exists. Task creation ignored.', e)


@receiver(pre_save, sender=BiddingSession)
def session_pre_save(sender, instance, **kwargs):
    """
    Updates tasks when session time is changed.
    """
    try:
        old_session = sender.objects.get(pk=instance.pk)
        old_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=old_session.end_time.minute,
            hour=old_session.end_time.hour)
        new_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=instance.end_time.minute,
            hour=instance.end_time.hour)
        PeriodicTask.objects \
            .filter(
                crontab=old_schedule,
                task='localhost.core.tasks.cleanup_bids') \
            .update(crontab=new_schedule)
        for task in PeriodicTask.objects.filter(
                crontab=new_schedule,
                task='localhost.core.tasks.cleanup_bids'):
            PeriodicTasks.changed(task)
        old_schedule.delete()
    except sender.DoesNotExist:
        logger.info(f'{instance} not in db. Skipping pre-save actions.')

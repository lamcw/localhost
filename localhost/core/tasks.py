import json
import logging

from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from celery import shared_task
from localhost.core.models import Bid, BiddingSession, Booking, PropertyItem

logger = logging.getLogger(__name__)


@shared_task
def cleanup_bids(pk):
    """
    Clear bids in database.

    If there is a successful bid for a property item, a booking is created for
    it automatically. All the bids are removed and bidding is closed for that
    property item.

    Args:
        pk: primary key of the property item
    """
    property_item = PropertyItem.objects.get(pk=pk)
    logger.info(f'cleaning up bids for property item: {property_item.title}')
    try:
        max_bid = property_item.bids.latest()
        Booking.objects.create(
            user=max_bid.bidder,
            property_item=property_item,
            price=max_bid.amount,
            earliest_checkin_time=property_item.earliest_checkin_time,
            latest_checkin_time=property_item.latest_checkin_time)
        property_item.available = False
        property_item.save()
        property_item.bids.all().delete()
    except Bid.DoesNotExist:
        logger.info('No bids in this session')


@shared_task
def enable_bids(pk):
    """
    Enable bids for a property item at 12:00nn.

    Args:
        pk: primary key of the property item
    """
    property_item = PropertyItem.objects.get(pk=pk)
    property_item.available = True
    property_item.save()
    logger.info(f'Bidding enabled for {property_item.title}')


@receiver(m2m_changed, sender=PropertyItem.session.through)
def property_item_m2m_changed(sender, instance, action, pk_set, **kwargs):
    sessions = BiddingSession.objects.filter(id__in=pk_set)
    if action == 'post_add':
        for session in sessions:
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=session.end_time.minute, hour=session.end_time.hour)
            PeriodicTask.objects.create(
                crontab=schedule,
                task='localhost.core.tasks.cleanup_bids',
                name=
                f'PropertyItem<{instance.id}> cleanup bids {session.end_time}',
                args=json.dumps([instance.id]))
    elif action == 'post_remove':
        names = [
            f'PropertyItem<{instance.id}> cleanup bids {session.end_time}'
            for session in sessions
        ]
        PeriodicTask.objects.filter(name__in=names).delete()


@receiver(post_save, sender=PropertyItem)
def property_item_post_save(sender, instance, **kwargs):
    schedule, _ = CrontabSchedule.objects.get_or_create(hour=12)
    PeriodicTask.ojects.create(
        crontab=schedule,
        task='localhost.core.tasks.enable_bids',
        name=f'Daily bids enable {instance.id}',
        args=json.dumps([instance.id]))

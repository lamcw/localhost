"""
All scheduled tasks in core.
"""
import logging
from datetime import datetime

from celery import shared_task
from django.utils import timezone
from localhost.core.models import Bid, Booking, PropertyItem

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
    logger.info(f'Cleaning up bids for property item: {property_item.title}')
    try:
        max_bid = property_item.bids.latest()
        now = timezone.now()
        earliest = timezone.make_aware(
            datetime.combine(now,
                             property_item.property.earliest_checkin_time))
        latest = timezone.make_aware(
            datetime.combine(now, property_item.property.latest_checkin_time))
        Booking.objects.create(
            user=max_bid.bidder,
            property_item=property_item,
            price=max_bid.amount,
            earliest_checkin_time=earliest,
            latest_checkin_time=latest)
        property_item.available = False
        property_item.save()
        property_item.bids.all().delete()
    except Bid.DoesNotExist:
        logger.exception('No bids in this session')


@shared_task
def enable_bids(pk):
    """
    Enable bids for a property item at 12:00nn.

    Args:
        pk: primary key of the property item
    """
    property_item = PropertyItem.objects.get(pk=pk)
    property_item.available = True
    logger.info(f'Bidding enabled for {property_item.title}')

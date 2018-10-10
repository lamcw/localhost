"""
All scheduled tasks in core.
"""
import logging
from datetime import datetime

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
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
        pk: Primary key of the property item
    """
    property_item = PropertyItem.objects \
        .prefetch_related('bids', 'property').get(pk=pk)
    logger.info(f'Cleaning up bids for property item: {property_item.title}')
    try:
        max_bid = property_item.bids.latest()
        today = timezone.now().date()
        earliest = timezone.make_aware(
            datetime.combine(today,
                             property_item.property.earliest_checkin_time))
        latest = timezone.make_aware(
            datetime.combine(today,
                             property_item.property.latest_checkin_time))
        Booking.objects.create(
            user=max_bid.bidder,
            property_item=property_item,
            price=max_bid.amount,
            earliest_checkin_time=earliest,
            latest_checkin_time=latest)
        channel_layer = get_channel_layer()
        logger.info(f'Bid won for {max_bid.bidder.full_name}')
        async_to_sync(channel_layer.group_send)(
            f'notification_{max_bid.bidder_id}', {
                'type': 'notification',
                'data': {
                    'id': '1337',
                    'message': 'You won a bid!.'
                }
            })
        property_item.bids.all().delete()
        property_item.available = False
        property_item.save()
    except Bid.DoesNotExist:
        logger.info('No bids in this session')


@shared_task
def enable_bids(pk):
    """
    Enable bids for a property item at 12:00nn.

    Args:
        pk: Primary key of the property item
    """
    property_item = PropertyItem.objects.get(pk=pk)
    property_item.available = True
    logger.info(f'Bidding enabled for {property_item.title}')

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def cleanup_bids(pk):
    from localhost.core.models import PropertyItem, Booking, Bid
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
    except Bid.DoesNotExist:
        logger.info('No bids in this session')
    finally:
        property_item.bids.all().delete()

"""
This module provides the MultiplexJsonWebsocketConsumer and Consumer classes.
These classes are used to provide multiplexed socket commmunication between
the server and a variety of clients who can listen to different and many
groups.
"""
import logging
from decimal import Decimal

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone

from localhost.core.models import Bid, BiddingSession, PropertyItem
from localhost.messaging.models import Message

logger = logging.getLogger(__name__)


class MultiplexJsonWebsocketConsumer(JsonWebsocketConsumer):
    """
    Variant of JsonWebsocketConsumer that is extended to support group
    multiplexing; allowing consumers to participate in multiple groups
    with a single socker connection.
    """

    def disconnect(self, code):
        for group in self.groups:
            self.unsubscribe(group)
        self.groups = []

    def subscribe(self, group):
        """
        Subscribes the consumer to a group.
        """
        self.groups.append(group)
        async_to_sync(self.channel_layer.group_add)(group, self.channel_name)

    def unsubscribe(self, group):
        """
        Unsubscribes the consumer from a group.
        """
        self.groups.remove(group)
        async_to_sync(self.channel_layer.group_discard)(group,
                                                        self.channel_name)

    def is_subscribed(self, group):
        """
        Checks if the consumer is subscribed to a group.
        """
        return group in self.groups


class Consumer(MultiplexJsonWebsocketConsumer):
    """
    Generalised variant of MultiplexJsonWebsocketConsumer for use by all
    socket connections.

    JSON data makes use of the client side cooperative multiplex
    socket library that expects all JSON data to be of the form:
    {
        'type': 'identifier',
        'data': {
            ...
        }
    }
    For incoming JSON data, the 'type' will contain the request.
    """

    def connect(self):
        if self.scope['user'].is_authenticated:
            self.accept()
        else:
            self.close()

    def receive_json(self, content, **kwargs):
        try:
            req = content['type']
            if req == 'subscribe':
                group = content['data']['group']
                self.request_subscribe(group)
            elif req == 'unsubscribe':
                group = content['data']['group']
                self.request_unsubscribe(group)
            elif req == 'bid':
                property_item_id = content['data']['property_item_id']
                amount = Decimal(content['data']['amount'])
                self.request_bid(property_item_id, amount)
            elif req == 'message':
                logger.debug(content['data'])
                recipient_id = content['data']['recipient_id']
                message = content['data']['message']
                self.request_inbox(recipient_id, message)
        except KeyError:
            logger.exception('Invalid JSON format')

    def request_subscribe(self, group):
        """
        Handles a request to subscribe to a group
        """

        sub_message = group.split('_')
        logger.debug(sub_message)
        logger.debug(group)
        logger.debug(self.scope['user'].id)
        if (sub_message[0] is 'inbox'
                and sub_message[1] is not self.scope['user'].id):
            logger.info("failed")
            self.close()
        elif not self.is_subscribed(group):
            self.subscribe(group)

    def request_unsubscribe(self, group):
        """
        Handles a request to unsubscribe to a group
        """
        if self.is_subscribed(group):
            self.unsubscribe(group)

    def request_bid(self, property_item_id, amount):
        """
        Handles a bid request
        """
        time_now = timezone.localtime().time()
        property_item = PropertyItem.objects.get(id=property_item_id)

        try:
            # The minimum next bid is either
            # * The starting price when there are no bids
            # * The next dollar amount if there is a bid
            latest_bid = property_item.bids.latest('amount')
            min_next_bid = latest_bid.amount + 1
        except Bid.DoesNotExist:
            min_next_bid = property_item.min_price

        current_session = BiddingSession.objects.filter(
            propertyitem=property_item,
            end_time__gt=time_now,
            start_time__lte=time_now)

        if not current_session.exists():
            self.send_json({
                'type': 'alert',
                'data': {
                    'description': 'Bidding session expired'
                }
            })
        elif amount > self.scope['user'].credits:
            self.send_json({
                'type': 'alert',
                'data': {
                    'description':
                    'Not enough credits! Go to Dashboard to add credits.'
                }
            })

        elif amount < min_next_bid:
            self.send_json({
                'type': 'alert',
                'data': {
                    'description': 'Your bid is too low.'
                }
            })

        else:
            async_to_sync(self.channel_layer.group_send)(
                f'property_item_{property_item_id}', {
                    'type': 'propagate',
                    'identifier_type': 'bid',
                    'data': {
                        'property_item_id': property_item_id,
                        'amount': str(amount),
                        'user_id': self.scope['user'].id
                    }
                })

            if not property_item.bids.exists():
                self.scope['user'].credits -= amount
                self.scope['user'].save()
            elif latest_bid.bidder == self.scope['user']:
                self.scope['user'].credits -= amount - latest_bid.amount
                self.scope['user'].save()
            else:
                latest_bid.bidder.credits += latest_bid.amount
                latest_bid.bidder.save()
                self.scope['user'].credits -= amount
                self.scope['user'].save()

            Bid.objects.create(
                property_item=property_item,
                bidder=self.scope['user'],
                amount=amount)

    def request_inbox(self, recipient_id, message):
        """
        Handles a inbox request
        """
        sender_id = self.scope['user'].id
        time_now = timezone.localtime()
        message_object = Message.objects.create(
            sender=self.scope['user'],
            recipient=get_user_model().objects.get(id=recipient_id),
            time=time_now,
            msg=message)
        recipient = get_user_model().objects.get(id=recipient_id)
        async_to_sync(self.channel_layer.group_send)(
            f'inbox_{recipient_id}', {
                'type': 'propagate',
                'identifier_type': 'message',
                'data': {
                    'message': message_object.msg,
                    'time': str(time_now),
                    'sender': {
                        'id': self.scope['user'].id,
                        'name': self.scope['user'].first_name
                    },
                    'recipient': {
                        'id': recipient_id,
                        'name': recipient.first_name
                    }
                }
            })

        async_to_sync(self.channel_layer.group_send)(
            f'inbox_{sender_id}', {
                'type': 'propagate',
                'identifier_type': 'message',
                'data': {
                    'message': message_object.msg,
                    'time': time_now.strftime("%b %d, %-H:%M %P"),
                    'sender': {
                        'id': self.scope['user'].id,
                        'name': self.scope['user'].first_name
                    },
                    'recipient': {
                        'id': recipient_id,
                        'name': recipient.first_name
                    }
                }
            })

    def propagate(self, event):
        """
        Propagates a message to the client
        """
        self.send_json({
            'type': event['identifier_type'],
            'data': event['data']
        })

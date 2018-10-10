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

from localhost.core.exceptions import (BidAmountError, SessionExpiredError,
                                       WalletOperationError)
from localhost.core.models import Bid, BiddingSession, PropertyItem, Notification
from localhost.messaging.models import Message

logger = logging.getLogger(__name__)
User = get_user_model()


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
        user = self.scope.get('user')
        notifications_id = 'notifications_' + str(user.id)
        if user and user.is_authenticated:
            self.accept()
            self.request_subscribe(notifications_id)
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
                pk = content['data']['property_item_id']
                amount = Decimal(content['data']['amount'])
                property_item = PropertyItem.objects.get(pk=pk)
                self.request_bid(property_item, amount)
            elif req == 'message':
                pk = content['data']['recipient_id']
                message = content['data']['message']
                recipient = User.objects.get(pk=pk)
                self.request_inbox(recipient, message)
            elif req == 'notification':
                instruction = content['data']['instruction']
                if instruction == 'clear':
                    Notification.objects.get(id=content['data']['notification_id']).delete()
        except KeyError as e:
            logger.exception('Invalid JSON format.', exc_info=e)

    def request_subscribe(self, group):
        """
        Handles a request to subscribe to a group.
        """
        if not self.is_subscribed(group):
            self.subscribe(group)

    def request_unsubscribe(self, group):
        """
        Handles a request to unsubscribe to a group.
        """
        if self.is_subscribed(group):
            self.unsubscribe(group)

    def request_bid(self, property_item, amount):
        """
        Handles a bid request.
        """
        user = self.scope['user']
        try:
            # The minimum next bid is either
            # * The starting price when there are no bids
            # * The next dollar amount if there is a bid
            latest_bid = property_item.bids.latest()
            min_next_bid = latest_bid.amount + 1
        except Bid.DoesNotExist:
            latest_bid = None
            min_next_bid = property_item.min_price

        try:
            check_bid(property_item, user, amount, min_next_bid, latest_bid)
            async_to_sync(self.channel_layer.group_send)(
                f'property_item_{property_item.id}', {
                    'type': 'propagate',
                    'identifier_type': 'bid',
                    'data': {
                        'property_item_id': property_item.id,
                        'amount': str(amount),
                        'user_id': user.id
                    }
                })

            if not property_item.bids.exists():
                user.credits -= amount
            elif latest_bid.bidder == user:
                user.credits -= amount - latest_bid.amount
            else:
                latest_bid.bidder.credits += latest_bid.amount
                latest_bid.bidder.save()
                user.credits -= amount
                notification = Notification.objects.create(
                    user=latest_bid.bidder,
                    message='O',
                    property_item=property_item)
                async_to_sync(self.channel_layer.group_send)(
                    f'notifications_{latest_bid.bidder.id}', {
                        'type': 'propagate',
                        'identifier_type': 'notification',
                        'data': {
                            'id': notification.id,
                            'message': 'You have been outbid!',
                            'url': '/property/' + str(property_item.id)
                        }
                    })
            user.save()

            Bid.objects.create(
                property_item=property_item, bidder=user, amount=amount)
        except (SessionExpiredError, WalletOperationError,
                BidAmountError) as e:
            self.send_json({'type': 'alert', 'data': {'description': str(e)}})

    def request_inbox(self, recipient, message):
        """
        Handles an inbox request
        """
        sender = self.scope['user']
        time_now = timezone.localtime()
        message_object = Message.objects.create(
            sender=sender, recipient=recipient, msg=message)
        async_to_sync(self.channel_layer.group_send)(
            f'inbox_{recipient.id}', {
                'type': 'propagate',
                'identifier_type': 'message',
                'data': {
                    'message': message_object.msg,
                    'time': str(time_now),
                    'sender': {
                        'id': sender.id,
                        'name': sender.first_name
                    },
                    'recipient': {
                        'id': recipient.id,
                        'name': recipient.first_name
                    }
                }
            })

        async_to_sync(self.channel_layer.group_send)(
            f'inbox_{sender.id}', {
                'type': 'propagate',
                'identifier_type': 'message',
                'data': {
                    'message': message_object.msg,
                    'time': time_now.strftime("%b %d, %-H:%M %P"),
                    'sender': {
                        'id': sender.id,
                        'name': sender.first_name
                    },
                    'recipient': {
                        'id': recipient.id,
                        'name': recipient.first_name
                    }
                }
            })
    def propagate(self, event):
        """
        Propagates a message to the client.
        """
        self.send_json({
            'type': event.get('identifier_type'),
            'data': event.get('data')
        })


def check_bid(property_item,
              user,
              incoming_bid_amount,
              min_next_bid,
              latest_bid=None):
    current_session = BiddingSession.current_session_of(property_item)
    if not current_session:
        raise SessionExpiredError('Bidding session expired.')
    elif (latest_bid and user == latest_bid.bidder
          and incoming_bid_amount > user.credits + latest_bid.amount):
        raise WalletOperationError(
            'Not enough credits! Go to Dashboard to add credits.')
    elif not latest_bid and incoming_bid_amount > user.credits:
        raise WalletOperationError(
            'Not enough credits! Go to Dashboard to add credits.')
    elif incoming_bid_amount < min_next_bid:
        raise BidAmountError('Your bid is too low.')

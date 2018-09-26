"""
This module provides the MultiplexJsonWebsocketConsumer and Consumer classes.
These classes are used to provide multiplexed socket commmunication between
the server and a variety of clients who can listen to different and many
groups.
"""

from decimal import Decimal
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from localhost.core.models import Bid, PropertyItem, BiddingSession
from django.contrib.auth import get_user_model

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
        async_to_sync(self.channel_layer.group_add)(
            group,
            self.channel_name
        )

    def unsubscribe(self, group):
        """
        Unsubscribes the consumer from a group.
        """
        self.groups.remove(group)
        async_to_sync(self.channel_layer.group_discard)(
            group,
            self.channel_name
        )

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
        print(content)
        try:
            req = content['type']
        except KeyError:
            pass

        if req == 'subscribe':
            try:
                group = content['data']['group']
                self.request_subscribe(str(group))
            except KeyError:
                pass
        elif req == 'unsubscribe':
            try:
                group = content['data']['group']
                self.request_unsubscribe(group)
            except KeyError:
                pass
        elif req == 'bid':
            try:
                property_item_id = content['data']['property_item_id']
                amount = Decimal(content['data']['amount'])
                self.request_bid(property_item_id, amount)
            except KeyError:
                pass

    def request_subscribe(self, group):
        """
        Handles a request to subscribe to a group
        """
        if not self.is_subscribed(group):
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
        User = get_user_model()
        time_now = timezone.localtime().time()
        property_item = PropertyItem.objects.get(pk=property_item_id)
        latest_bid = property_item.bids.latest('amount')
        bid_user = self.scope['user']

        try:
            # The minimum next bid is either
            # * The starting price when there are no bids
            # * The next dollar amount if there is a bid
            min_next_bid = latest_bid.amount+1
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
                    'description': 'Not enough credits! Go to Dashboard to add credits.'
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
                'property_item_' + str(property_item_id),
                {
                    'type': 'propagate',
                    'identifier_type': 'bid',
                    'data': {
                        'property_item_id': property_item_id,
                        'amount': str(amount),
                        'user': {
                            'id': self.scope['user'].id,
                            'name': self.scope['user'].first_name
                        }
                    }
                }
            )

            if latest_bid.bidder == self.scope['user']:
                self.scope['user'].credits-=(amount-latest_bid.amount)
                self.scope['user'].save()
            else:
                latest_bid.bidder.credits+=latest_bid.amount
                latest_bid.bidder.save()
                self.scope['user'].credits-=amount
                self.scope['user'].save()
            Bid.objects.create(
                property_item=property_item,
                bidder=self.scope['user'],
                amount=amount)

    def propagate(self, event):
        """
        Propagates a message to the client
        """
        self.send_json({
            'type': str(event['identifier_type']),
            'data': event['data']
        })

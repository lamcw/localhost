import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone
from localhost.core.models import Bid, PropertyItem, BiddingSession

OK = 0
ERROR_INVALID_BID = -1
ERROR_INVALID_SESSION = -2
ERROR_INSUFFICIENT_FUNDS = -3


class BidConsumer(WebsocketConsumer):
    def connect(self):
        pk = self.scope['url_route']['kwargs']['item_id']
        self.room_group_name = 'bidding_%s' % pk
        self.property_item = PropertyItem.objects.get(pk=pk)
        self.user = self.scope['user']

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        """
        Leave room group.
        """
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        """
        Receive message from WebSocket.
        """
        text_data_json = json.loads(text_data)
        user_bid = text_data_json['message']
        time_now = timezone.localtime().time()

        try:
            min_next_bid = Bid.objects.filter(
                property_item=self.property_item). \
                latest('amount').amount + 1
        except Bid.DoesNotExist:
            min_next_bid = self.property_item.min_price

        current_session = BiddingSession.objects.filter(
                propertyitem=self.property_item,
                end_time__gt=time_now,
                start_time__lte=time_now)

        if not current_session.exists():
            self.send(text_data=json.dumps({
                'type' : 'BID_RESPONSE',
                'status_code' : ERROR_INVALID_SESSION,
                'content': 'ERROR_INVALID_SESSION'
            }))

        elif user_bid > self.user.credits:
            self.send(text_data=json.dumps({
                'type' : 'BID_RESPONSE',
                'status_code' : ERROR_INSUFFICIENT_FUNDS,
                'content': 'ERROR_INSUFFICIENT_FUNDS'
            }))

        elif user_bid < min_next_bid:
            self.send(text_data=json.dumps({
                'type' : 'BID_RESPONSE',
                'status_code' : ERROR_INVALID_BID,
                'content': 'ERROR_INVALID_BID'
            }))
        else:
            Bid.objects.create(
                property_item=self.property_item,
                bidder=self.user,
                amount=user_bid)

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type' : 'bid',
                    'amount': user_bid,
                    'user_id' : self.user.id,
                    'user_name' : self.user.first_name
                }
            )
            self.send(text_data=json.dumps({
                'type' : 'BID_RESPONSE',
                'status_code' : OK,
                'content': 'SUCCESSFUL_BID'
            }))



    def bid(self, event):
        amount = event['amount']
        user_id = event['user_id']
        user_name = event['user_name']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type' : 'BID_GLOBAL',
            'status_code' : '0',
            'content': {
                'user_id' : user_id,
                'user_name' : user_name,
                'amount' : amount,
            }
        }))

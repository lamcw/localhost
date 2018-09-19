import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone
from localhost.core.models import Bid, PropertyItem, BiddingSession

ERROR_INVALID_BID = -1

class BidConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.user = self.scope['user']
        self.property_item = PropertyItem.objects.get(pk=self.room_name)

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
        bid_message = text_data_json['message']
        time_now = timezone.localtime(timezone.now()).time()
        latest_bid = Bid.objects.filter(
                property_item=self.room_name).latest('bid_amount').bid_amount
        current_session = BiddingSession.objects.filter(
                propertyitem__id=self.room_name,
                end_time__gt=time_now,
                start_time__lte=time_now)

        if current_session.exists():
            if bid_message > latest_bid:
                Bid.objects.create(
                        property_item=self.property_item,
                        bidder=self.user,
                        bid_amount=bid_message)

                async_to_sync(self.channel_layer.group_send)(
                        self.room_group_name,
                        {
                            'type': 'bid',
                            'message': bid_message
                            }
                        )
            else:
                self.send(text_data=json.dumps({
                    'message': ERROR_INVALID_BID
                }))
        else:
            self.send(text_data=json.dumps({
                'message': ERROR_NVALID_BID
            }))


            # if not Bid.objects.filter(property_item=self.room_name).exists():
        #     next_bid = PropertyItem.objects.get(pk=self.room_name).min_price
        # else:
        #     next_bid = Bid.objects.filter(
        #         property_item=self.room_name).latest('bid_amount').bid_amount + 5

        # if message == next_bid:
        #     Bid.objects.create(
        #         property_item=self.property_item,
        #         bidder=self.user,
        #         bid_amount=message)

        #     async_to_sync(self.channel_layer.group_send)(
        #         self.room_group_name,
        #         {
        #             'type': 'bid',
        #             'message': message
        #         }
        #     )

    def bid(self, event):
        """
        Receive message from room group.
        """
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
            }))

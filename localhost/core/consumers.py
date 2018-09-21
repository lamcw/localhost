import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone
from localhost.core.models import Bid, PropertyItem, BiddingSession

SUCCESFUL_BID = 0
ERROR_INVALID_BID = -1
ERROR_INVALID_SESSION = -2
ERROR_INSUFFICIENT_FUNDS = -3


class BidConsumer(WebsocketConsumer):
    def connect(self):
        self.property_item_id = self.scope['url_route']['kwargs']['item_id']
        self.room_group_name = 'bidding_%s' % self.property_item_id
        self.property_item = PropertyItem.objects.get(pk=self.property_item_id)
        self.user = self.scope['user']

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        print(self.channel_name)
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
        time_now = timezone.localtime(timezone.now()).time()

        try:
            min_next_bid = Bid.objects.filter(
                property_item=self.property_item_id). \
                latest('bid_amount').bid_amount + 1
        except Bid.DoesNotExist:
            min_next_bid = self.property_item.min_price

        current_session = BiddingSession.objects.filter(
                propertyitem__id=self.property_item_id,
                end_time__gt=time_now,
                start_time__lte=time_now)

        if current_session.exists():
            if user_bid <= self.user.credits:
                if user_bid > min_next_bid:
                    Bid.objects.create(
                            property_item=self.property_item,
                            bidder=self.user,
                            bid_amount=user_bid)

                    async_to_sync(self.channel_layer.group_send)(
                            self.room_group_name,
                            {
                                'type' : "bid",
                                'bid_amount': user_bid,
                                'user' : self.user.first_name
                            }
                    )
                    self.send(text_data=json.dumps({
                        'message': SUCCESFUL_BID
                    }))


                    #TODO subtract bid amount from credits
                else:
                    self.send(text_data=json.dumps({
                        'message': ERROR_INVALID_BID
                    }))
            else:
                self.send(text_data=json.dumps({
                    'message': ERROR_INSUFFICIENT_FUNDS}))
        else:
            self.send(text_data=json.dumps({
                'message': ERROR_INVALID_SESSION
            }))

    def bid(self, event):
        bid_amount = event['bid_amount']
        user = event['user']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': bid_amount,
            'user' : user
        }))

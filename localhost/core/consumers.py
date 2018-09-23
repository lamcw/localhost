from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer


class MultiplexJsonWebsocketConsumer(JsonWebsocketConsumer):
    """
    Variant of JsonWebsocketConsumer that is extended to support group
    multiplexing; allowing consumers to participate in multiple groups
    with a single socker connection.
    """

    def disconnect(self, code):
        for group in self.groups:
            self.unsubscribe(group)

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
    """

    def connect(self):
        if self.scope['user'].is_authenticated:
            self.accept()
        else:
            self.close()

    def receive_json(self, content, **kwargs):
        try:
            req = content['request']
        except KeyError:
            pass

        if req == 'subscribe':
            try:
                group = content['data']['group']
            except KeyError:
                pass
            self.request_subscribe(group)
        elif req == 'unsubscribe':
            try:
                group = content['data']['group']
            except KeyError:
                pass
            self.request_unsubscribe(group)

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

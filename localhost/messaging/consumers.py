import logging

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.utils import timezone

from localhost.core.consumers import BaseConsumer
from localhost.messaging.models import Message

logger = logging.getLogger(__name__)
User = get_user_model()


class ChatConsumer(BaseConsumer):
    def request_unsubscribe(self, group):
        sub_message = group.split('_')
        logger.debug(sub_message)
        logger.debug(group)
        logger.debug(self.scope['user'].id)
        if (sub_message[0] is 'inbox'
                and sub_message[1] is not self.scope['user'].id):
            logger.info("failed")
            self.close()
        else:
            super().request_unsubscribe(group)

    def receive_json(self, content, **kwargs):
        super().receive_json(content, **kwargs)
        try:
            req = content['type']
            if req == 'message':
                logger.debug(content['data'])
                recipient_id = content['data']['recipient_id']
                message = content['data']['message']
                self.request_inbox(recipient_id, message)
        except KeyError as e:
            logger.exception('Invalid JSON format.', exc_info=e)

    def request_inbox(self, recipient_id, message):
        """
        Handles a inbox request
        """
        sender_id = self.scope['user'].id
        time_now = timezone.localtime()
        message_object = Message.objects.create(
            sender=self.scope['user'],
            recipient=User.objects.get(id=recipient_id),
            time=time_now,
            msg=message)
        recipient = User.objects.get(id=recipient_id)
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

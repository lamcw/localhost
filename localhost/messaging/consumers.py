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
                pk = content['data']['recipient_id']
                message = content['data']['message']
                recipient = User.objects.get(pk=pk)
                self.request_inbox(recipient, message)
        except KeyError as e:
            logger.exception('Invalid JSON format.', exc_info=e)
        except User.DoesNotExist:
            logger.exception(
                'User in request does not exist. JSON may be tampered.')
        except User.MultipleObjectsReturned:
            logger.exception('More than one user found. JSON may be tampered.')

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

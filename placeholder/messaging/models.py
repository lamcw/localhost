from django.db import models

from placeholder.authentication.models import User


class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='sent_msg')
    recipient = models.ForeignKey(User, on_delete=models.PROTECT)
    time = models.DateTimeField(auto_now_add=True)
    msg = models.TextField()

from django.db import models

from placeholder.authentication.models import User


class Message(models.Model):
    sender = models.OneToOneField(User, on_delete=models.PROTECT, related_name='sent_msg')
    recipient = models.OneToOneField(User, on_delete=models.PROTECT)
    time = models.DateTimeField()
    msg = models.TextField()

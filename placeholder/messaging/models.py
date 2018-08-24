from django.contrib.auth import get_user_model
from django.db import models


class Message(models.Model):
    sender = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, related_name='sent_msg')
    recipient = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    time = models.DateTimeField(auto_now_add=True)
    msg = models.TextField()

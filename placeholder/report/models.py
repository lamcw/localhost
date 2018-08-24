from django.contrib.auth import get_user_model
from django.db import models

from placeholder.core.models import PropertyItem


class Report(models.Model):
    from_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    description = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class UserReport(Report):
    reported_user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='report')


class PropertyReport(Report):
    property_item = models.ForeignKey(
        PropertyItem, on_delete=models.PROTECT)

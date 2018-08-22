from django.db import models

from placeholder.authentication.models import User
from placeholder.core.models import PropertyItem


class Report(models.Model):
    from_user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField()
    time = models.DateTimeField()

    class Meta:
        abstract = True


class UserReport(Report):
    reported_user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='report')


class PropertyReport(Report):
    property_item = models.OneToOneField(
        PropertyItem, on_delete=models.PROTECT)

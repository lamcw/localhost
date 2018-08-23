from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models


class User(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )
    description = models.CharField(max_length=100, null=True, blank=True)
    dob = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    credits = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal('0.0'))

    def save(self, *args, **kwargs):
        if not self.pk:
            try:
                user = User.objects.get(user=self.user)
                self.pk = user.pk
            except User.DoesNotExist:
                pass
        super().save(*args, **kwargs)

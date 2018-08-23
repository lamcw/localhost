from django.db import models
from django.contrib.auth import get_user_model

from decimal import Decimal


class User(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    description = models.CharField(max_length=100, null=True, blank=True)
    dob = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    credits = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal('0.0'))

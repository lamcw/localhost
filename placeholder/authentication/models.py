from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

class User(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    description = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    credits = models.IntegerField()

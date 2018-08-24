from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    first_name = models.CharField(_('first name'), max_length=30, blank=False)
    last_name = models.CharField(_('last name'), max_length=150, blank=False)
    email = models.EmailField(_('email address'), blank=False)
    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )
    bio = models.CharField(
        _('bio'),
        max_length=100,
        null=True,
        blank=True,
        help_text=_('Biography')
    )
    dob = models.DateField(_('date of birth'), null=True)
    gender = models.CharField(
        _('gender'),
        max_length=1,
        choices=GENDER_CHOICES
    )
    credits = models.DecimalField(
        _('credits'),
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.0')
    )

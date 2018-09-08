from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel
from polymorphic.showfields import ShowFieldType


class Amenity(models.Model):
    item = models.CharField(max_length=15, unique=True)

    class Meta:
        verbose_name_plural = 'amenities'

    def __str__(self):
        return f"{self.item}"


class Session(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()


class Property(models.Model):
    host = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(
        _('title'), max_length=40, help_text=_('character limit: 40'))
    description = models.TextField(
        _('description'), max_length=200, help_text=_('character limit: 200'))
    address = models.CharField(
        _('address'), max_length=150, help_text=_('address of this property.'))
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    earliest_checkin_time = models.TimeField()
    latest_checkin_time = models.TimeField()
    session = models.ManyToManyField(Session, blank=True, null= True)

    class Meta:
        verbose_name_plural = 'properties'

    def __str__(self):
        return f"Property: {self.title} owned by {self.host}"


class PropertyItem(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    title = models.CharField(
        _('title'), max_length=40, help_text=_('character limit: 40'))
    description = models.TextField(
        _('description'), max_length=200, help_text=_('character limit: 200'))
    min_price = models.PositiveIntegerField(_('min price'))
    buyout_price = models.PositiveIntegerField(
        _('buyout price'), help_text=_('buyout price during auction.'))
    highest_bidder = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    amenities = models.ManyToManyField(Amenity, blank=True)
    capacity = models.PositiveIntegerField()
    bindable = models.BooleanField(default=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"


def property_item_img_path(instance, filename):
    """
    File will be uploaded to
    MEDIA_ROOT/user_<id>/property_item_<property_item_id>/<filename>
    """
    return f"user_{instance.user.id}/property_item_{instance.property_item.id}/{filename}"


def property_img_path(instance, filename):
    """
    File will be uploaded to
    MEDIA_ROOT/user_<id>/property_item_<property_item_id>/<filename>
    """
    return f"user_{instance.user.id}/property_{instance.property.id}/{filename}"


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    img = models.ImageField(upload_to=property_img_path)


class PropertyItemImage(models.Model):
    property_item = models.ForeignKey(PropertyItem, on_delete=models.CASCADE)
    img = models.ImageField(upload_to=property_item_img_path)


class Booking(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    property_item = models.ForeignKey(PropertyItem, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(_('price'))

    def __str__(self):
        return f"{self.user} booked {self.property_item}"


class Review(ShowFieldType, PolymorphicModel):
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(6)])
    description = models.TextField(_('description'))

    class Meta:
        abstract = True


class PropertyItemReview(Review):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)


class UserReview(Review):
    reviewer = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

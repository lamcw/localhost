import factory
from django.contrib.auth import get_user_model


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ('email', )

    first_name = 'a'
    last_name = 'b'
    email = 'c@c.com'
    gender = 'M'

from django.conf import settings


def gmaps_key(request):
    return {'GMAPS_KEY': settings.GMAPS_KEY}

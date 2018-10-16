import googlemaps

from django.conf import settings


def parse_address(address):
    """
    Parses address using Google Maps Geocode API.

    Args:
        address: Address in string

    Returns:
        (latitude, longitude)
    """
    gmaps = googlemaps.Client(key=settings.GMAPS_KEY)
    geocode = gmaps.geocode(address)
    latitude = geocode[0]['geometry']['location']['lat']
    longitude = geocode[0]['geometry']['location']['lng']
    return latitude, longitude

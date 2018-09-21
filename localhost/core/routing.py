from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/property-item/(?P<item_id>[^/]+)/$', consumers.BidConsumer),
]

from django.urls import path

from localhost.core import consumers

websocket_urlpatterns = [
    path('ws/bid/', consumers.BiddingConsumer),
    path('ws/notification/', consumers.NotificationConsumer)
]

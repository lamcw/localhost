from django.urls import path

from localhost.core import consumers

websocket_urlpatterns = [
    path('ws/realtime/', consumers.Consumer)
]

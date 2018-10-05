from django.urls import path

from localhost.messaging import consumers

websocket_urlpatterns = [
    path('ws/chat/', consumers.ChatConsumer)
]

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from localhost.core.routing import websocket_urlpatterns as bidding_ws_urlpatterns
from localhost.messaging.routing import websocket_urlpatterns as msg_ws_urlpatterns

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket':
    AuthMiddlewareStack(
        URLRouter(bidding_ws_urlpatterns + msg_ws_urlpatterns)
    ),
})

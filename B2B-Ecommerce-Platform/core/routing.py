from email.mime import application
from channels.auth import (
    AuthMiddlewareStack,
)  # ensures users have to log into access chatroom

# also used to identify the logged in user
from channels.routing import ProtocolTypeRouter, URLRouter
from manager.routing import websocket_urlpatterns

# similar to urlpatterns
application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
    }
)
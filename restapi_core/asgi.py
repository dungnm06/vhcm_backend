"""
ASGI config for restapi_core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""
import django
django.setup()
import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import vhcm.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restapi_core.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "https": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            vhcm.routing.websocket_urlpatterns
        )
    ),
})

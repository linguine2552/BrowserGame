# /backend/game_project/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_project.settings')
django.setup()

from game_app import routing as game_routing
from game_app.game_state import game_state

async def lifespan(scope, receive, send):
    while True:
        message = await receive()
        if message['type'] == 'lifespan.startup':
            await game_state.start_physics_update()
            print("Starting physics update loop")
            await send({'type': 'lifespan.startup.complete'})
        elif message['type'] == 'lifespan.shutdown':
            if game_state.physics_task:
                game_state.physics_task.cancel()
            print("Shutting down physics update loop")
            await send({'type': 'lifespan.shutdown.complete'})
            return

print("Loaded websocket_urlpatterns:", game_routing.websocket_urlpatterns)

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            game_routing.websocket_urlpatterns
        )
    ),
    "lifespan": lifespan,
})

print("ASGI application configured")
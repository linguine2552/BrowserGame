# /backend/game_app/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/game/(?P<player_id>[\w-]+)/$', consumers.GameConsumer.as_asgi()),
]

print("Websocket URL patterns loaded:", websocket_urlpatterns)
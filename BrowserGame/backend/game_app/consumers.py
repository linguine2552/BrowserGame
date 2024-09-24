# /backend/game_app/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .game_state import game_state

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.player_id = self.scope['url_route']['kwargs']['player_id']
        await self.channel_layer.group_add('game', self.channel_name)
        await self.accept()
        
        if not game_state.physics_task:
            await game_state.start_physics_update()
            print("Starting physics update loop")

        if not game_state.map_data:
            await game_state.load_map_data()

        initial_y = game_state.map_data['height'] if game_state.map_data else 0
        game_state.add_player(self.player_id, 0, initial_y)
        print(f"New player connected: {self.player_id}")
        await game_state.broadcast_state()

    async def disconnect(self, close_code):
        print(f"Player disconnected: {self.player_id}")
        game_state.remove_player(self.player_id)
        await game_state.broadcast_state()
        await self.channel_layer.group_discard('game', self.channel_name)

        if not game_state.players:
            await game_state.stop_physics_update()
            print("Shutting down physics update loop")

    async def receive(self, text_data):
        data = json.loads(text_data)
        x = data.get('x')
        jump = data.get('jump', False)
        running = data.get('running', False)
        crouching = data.get('crouching', False)
        
        if x is not None:
            game_state.movement_component.update_player_position(self.player_id, x, None, running, crouching)
        
        if jump:
            game_state.movement_component.player_jump(self.player_id)
        
        game_state.movement_component.update_player_crouch(self.player_id, crouching)
        
        await game_state.broadcast_state()

    async def game_state(self, event):
        # print(f"Sending game state to {self.player_id}: {event['state']}")
        await self.send(text_data=event['state'])
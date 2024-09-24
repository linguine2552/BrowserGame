# game_state.py
import json
import asyncio
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from .models import Map, MapTile
from .movement_component import MovementComponent
from .animation_component import AnimationComponent
from .collision_component import CollisionComponent

class GameState:
    def __init__(self):
        self.players = {}
        self.player_mouse_positions = {}        
        self.gravity = -37
        self.update_interval = 1/60
        self.jump_velocity = 6.5
        self.base_speed = 30  # pixels per second
        self.max_speed = 150
        self.acceleration_rate = 100  # pixels per second^2 
        self.deceleration_rate = 200      
        self.physics_task = None
        self.tile_width = 1
        self.tile_height = 1
        self.player_width = 1
        self.player_height = 2
        self.map_data = None
        self.map_id = 7
        self.collision_buffer = 0.1
        self.movement_component = MovementComponent(self)
        self.animation_component = AnimationComponent(self)
        self.collision_component = CollisionComponent(self)               

    @sync_to_async
    def _get_map_data(self):
        try:
            map_obj = Map.objects.get(id=self.map_id)
            return {
                'name': map_obj.name,
                'width': map_obj.width,
                'height': map_obj.height,
                'tiles': list(map_obj.tiles.values('x', 'y', 'color', 'layer'))
            }
        except Map.DoesNotExist:
            print(f"Map with id {self.map_id} not found")
            return None

    async def load_map_data(self):
        self.map_data = await self._get_map_data()
        if self.map_data:
            print("Map data loaded:")
            print(f"Map dimensions: {self.map_data['width']}x{self.map_data['height']}")
            print("Layer 1 tiles:")
            for tile in self.map_data['tiles']:
                if tile['layer'] == 1:
                    print(f"x: {tile['x']}, y: {tile['y']}")
        else:
            print(f"Failed to load map data for map_id: {self.map_id}")

    def get_ground_level(self, x):
        if not self.map_data:
            return 0

        player_left = x
        player_right = x + self.player_width
        
        highest_ground = 0
        for tile in self.map_data['tiles']:
            if tile['layer'] == 1:
                tile_left = tile['x']
                tile_right = tile['x'] + self.tile_width
                tile_top = self.map_data['height'] - tile['y'] - 1
                if (player_left < tile_right and player_right > tile_left and 
                    highest_ground + self.collision_buffer <= tile_top):
                    highest_ground = tile_top - self.tile_height

        print(f"Ground level at x={x}: {highest_ground}")
        return highest_ground

    async def start_physics_update(self):
        if not self.physics_task:
            print("Starting physics update loop")
            self.physics_task = asyncio.create_task(self._physics_loop())

    async def stop_physics_update(self):
        if self.physics_task:
            self.physics_task.cancel()
            self.physics_task = None
            print("Shutting down physics update loop")

    async def _physics_loop(self):
        while True:
            await self.physics_update()
            await asyncio.sleep(self.update_interval)

    async def physics_update(self):
        for player_id, player in self.players.items():
            old_y = player['y']
            old_x = player['x']
            
            player['vy'] += self.gravity * self.update_interval
            new_y = player['y'] + player['vy'] * self.update_interval
            
            ground_level = self.get_ground_level(player['x'])
            if new_y <= ground_level + self.player_height:
                new_y = ground_level + self.player_height
                player['vy'] = 0
            
            player['y'] = new_y
            
            if old_y != player['y'] or old_x != player['x']:
                print(f"Physics update for player {player_id}: old_y={old_y}, new_y={player['y']}, vy={player['vy']}, old_x={old_x}, new_x={player['x']}")
            
            running = player.get('speed', self.base_speed) > self.base_speed
            jumping = player['vy'] != 0
            crouching = player.get('crouching', False)
            self.animation_component.update_pivot_points(player, running, jumping, crouching)
        
        if self.players:
            await self.broadcast_state()

    def add_player(self, player_id, x, y):
        ground_level = self.get_ground_level(x)
        self.players[player_id] = {
            'x': float(x),
            'y': max(float(y), ground_level),
            'vy': 0,
            'direction': 'forward',
            'pivot_points': self.animation_component.get_idle_frame('forward', False),
            'crouching': False
        }
        self.animation_component.set_player_animation_state(player_id, 'IDLE')
        print(f"Player added: id={player_id}, x={x}, y={self.players[player_id]['y']}")

    def remove_player(self, player_id):
        if player_id in self.players:
            del self.players[player_id]
            print(f"Player removed: id={player_id}")

    def get_state(self):
        return {player_id: {
            'x': player['x'],
            'y': player['y'],
            'pivot_points': player['pivot_points'],
            'speed': player.get('speed', self.base_speed),
            'angle': player.get('angle', 0),
            'direction': player.get('direction', 'forward'),
            'crouching': player.get('crouching', False),
            'mouse_position': self.player_mouse_positions.get(player_id, {'x': 0, 'y': 0})
        } for player_id, player in self.players.items()}

    async def broadcast_state(self):
        state = self.get_state()
        # print(f"Broadcasting state: {state}")
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            'game',
            {
                'type': 'game.state',
                'state': json.dumps(state)
            }
        )
        # print("State broadcast complete")

game_state = GameState()
# /backend/game_app/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from asgiref.sync import async_to_sync
from .game_state import game_state
from .models import Map, MapTile, Player
import uuid
import json
import logging

logger = logging.getLogger(__name__)

def initialize_game(request):
    player_id = str(uuid.uuid4())
    
    try:
        map_obj = Map.objects.get(id=game_state.map_id)
        map_data = {
            'name': map_obj.name,
            'width': map_obj.width,
            'height': map_obj.height,
            'tiles': map_obj.get_tile_data()
        }
    except Map.DoesNotExist:
        map_data = None
        logger.error(f"Map with id {game_state.map_id} not found")

    response_data = {
        'player_id': player_id,
        'map': map_data
    }

    return JsonResponse(response_data)

@csrf_exempt
@require_http_methods(["POST"])
def save_map(request):
    try:
        data = json.loads(request.body)
        map_name = data.get('name')
        map_width = data.get('width')
        map_height = data.get('height')
        layers = data.get('layers')

        if not all([map_name, map_width, map_height, layers]):
            return JsonResponse({'error': 'Missing required data'}, status=400)

        map_obj, created = Map.objects.update_or_create(
            name=map_name,
            defaults={'width': map_width, 'height': map_height}
        )

        MapTile.objects.filter(map=map_obj).delete()

        tiles_to_create = []
        for layer_index, layer in enumerate(layers):
            for tile in layer.get('data', []):
                tiles_to_create.append(MapTile(
                    map=map_obj,
                    x=tile['x'],
                    y=tile['y'],
                    color=tile['color'],
                    layer=layer_index
                ))

        MapTile.objects.bulk_create(tiles_to_create)

        logger.info(f"Map '{map_name}' saved successfully")
        return JsonResponse({'success': True, 'map_id': map_obj.id})
    except Exception as e:
        logger.error(f"Error saving map: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)
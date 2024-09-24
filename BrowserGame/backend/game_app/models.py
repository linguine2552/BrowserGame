# /backend/game_app/models.py
from django.db import models
from django.db.models import JSONField

class Player(models.Model):
    player_id = models.CharField(max_length=100, unique=True)
    x = models.FloatField()
    y = models.FloatField()
    vx = models.FloatField(default=0)
    vy = models.FloatField(default=0)
    sword = JSONField(default=dict)    
    
    pivot_points = models.TextField(default='{}')
    
    def __str__(self):
        return f"Player {self.player_id} in world {self.world.name}"

    def set_pivot_point(self, name, x, y):
        import json
        points = json.loads(self.pivot_points)
        points[name] = [x, y]
        self.pivot_points = json.dumps(points)

    def get_pivot_point(self, name):
        import json
        points = json.loads(self.pivot_points)
        return points.get(name, [0, 0])
        
class Map(models.Model):
    name = models.CharField(max_length=100)
    width = models.IntegerField(default=250)
    height = models.IntegerField(default=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_first_map(cls):
        return cls.objects.first()

    def get_tile_data(self):
        return list(self.tiles.values('x', 'y', 'color', 'layer'))

class MapTile(models.Model):
    map = models.ForeignKey(Map, on_delete=models.CASCADE, related_name='tiles')
    x = models.IntegerField()
    y = models.IntegerField()
    color = models.CharField(max_length=7)
    layer = models.IntegerField()

    class Meta:
        unique_together = ('map', 'x', 'y', 'layer')

    def __str__(self):
        return f"Tile at ({self.x}, {self.y}) on layer {self.layer} in {self.map.name}"        
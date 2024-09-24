class CollisionComponent:
    def __init__(self, game_state):
        self.game_state = game_state

    def check_collision(self, player, new_x, new_y):
        adjusted_x = self.check_horizontal_collision(player, new_x, player['y'])
        adjusted_y = self.check_vertical_collision(player, adjusted_x, new_y)
        
        return adjusted_x, adjusted_y

    def check_horizontal_collision(self, player, new_x, y):
        player_left = new_x
        player_right = new_x + self.game_state.player_width
        player_top = self.game_state.map_data['height'] - y - self.game_state.player_height
        player_bottom = self.game_state.map_data['height'] - y

        for tile in self.game_state.map_data['tiles']:
            if tile['layer'] == 1:
                tile_left = tile['x']
                tile_right = tile['x'] + self.game_state.tile_width
                tile_top = tile['y']
                tile_bottom = tile['y'] + self.game_state.tile_height

                if self.check_box_collision(player_left, player_right, player_top, player_bottom,
                                            tile_left, tile_right, tile_top, tile_bottom):
                    if player['x'] < tile_left:  # Coming from left
                        return tile_left - self.game_state.player_width
                    else:  # Coming from right
                        return tile_right

        return new_x

    def check_vertical_collision(self, player, x, new_y):
        player_left = x
        player_right = x + self.game_state.player_width
        player_bottom = self.game_state.map_data['height'] - new_y
        player_top = player_bottom - self.game_state.player_height

        # Adjust the collision point to be slightly below the player's feet
        collision_point = player_bottom - self.game_state.collision_buffer

        for tile in self.game_state.map_data['tiles']:
            if tile['layer'] == 1:
                tile_left = tile['x']
                tile_right = tile['x'] + self.game_state.tile_width
                tile_top = tile['y']
                tile_bottom = tile['y'] + self.game_state.tile_height

                if (player_left < tile_right and player_right > tile_left and
                    collision_point < tile_bottom and player_top > tile_top):
                    if player['y'] > new_y:  # Falling
                        return self.game_state.map_data['height'] - tile_bottom + self.game_state.collision_buffer
                    else:  # Jumping
                        return self.game_state.map_data['height'] - tile_top - self.game_state.player_height

        return new_y

    @staticmethod
    def check_box_collision(box1_left, box1_right, box1_top, box1_bottom,
                            box2_left, box2_right, box2_top, box2_bottom):
        return (box1_left < box2_right and box1_right > box2_left and
                box1_top < box2_bottom and box1_bottom > box2_top)
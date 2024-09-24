# /backend/game_app/movement_component.py
import math
import time

class MovementComponent:
    def __init__(self, game_state):
        self.game_state = game_state
        self.player_speeds = {}
        self.player_directions = {}
        self.player_angles = {}
        self.max_tilt_angle = 7  # Maximum tilt angle in degrees
        self.tilt_speed = 180  # Degrees per second
        self.min_speed_for_tilt = 1  # Minimum speed to start tilting
        self.player_jumping_states = {}  # Track jumping state for each player
        self.player_jump_start_times = {}  # Track jump start time for each player
        self.jump_duration = 0.4  # Total duration of jump animation in seconds
        self.player_crouching_states = {}  # Track crouching state for each player

    def update_player_position(self, player_id, x, y, running, crouching):
        if player_id in self.game_state.players:
            player = self.game_state.players[player_id]
            
            current_speed = self.player_speeds.get(player_id, self.game_state.base_speed)
            current_direction = self.player_directions.get(player_id, 0)
            current_angle = self.player_angles.get(player_id, 0)
            
            direction_changed = False
            if x is not None:
                new_direction = 1 if x > player['x'] else -1 if x < player['x'] else 0
                if current_direction != 0 and new_direction != current_direction:
                    direction_changed = True
                self.player_directions[player_id] = new_direction
            else:
                new_direction = 0

            if direction_changed:
                # Bring the player to a complete stop when changing direction
                new_speed = 0
            elif crouching:
                # Set speed to base speed when crouching
                new_speed = self.game_state.base_speed
            elif running and new_direction != 0:
                new_speed = min(current_speed + self.game_state.acceleration_rate * self.game_state.update_interval, 
                                self.game_state.max_speed)
            else:
                new_speed = max(self.game_state.base_speed, 
                                current_speed - self.game_state.deceleration_rate * self.game_state.update_interval)
            
            self.player_speeds[player_id] = new_speed

            # Calculate new angle based on speed and direction
            if abs(new_speed - self.game_state.base_speed) > self.min_speed_for_tilt and new_direction != 0:
                target_angle = new_direction * self.max_tilt_angle * (new_speed - self.game_state.base_speed) / (self.game_state.max_speed - self.game_state.base_speed)
            else:
                target_angle = 0

            angle_change = self.tilt_speed * self.game_state.update_interval
            if abs(target_angle - current_angle) <= angle_change:
                new_angle = target_angle
            else:
                new_angle = current_angle + math.copysign(angle_change, target_angle - current_angle)
            
            self.player_angles[player_id] = new_angle

            if x is not None:
                max_distance = new_speed * self.game_state.update_interval
                desired_distance = abs(x - player['x'])
                actual_distance = min(desired_distance, max_distance)
                new_x = player['x'] + new_direction * actual_distance
            else:
                new_x = player['x']

            if y is None:
                new_y = player['y']
            else:
                new_y = float(y)

            adjusted_x, adjusted_y = self.game_state.collision_component.check_collision(player, new_x, new_y)
            
            player['x'] = adjusted_x
            player['y'] = adjusted_y
            player['speed'] = new_speed
            player['angle'] = new_angle
            
            # Update animation component with running state, jumping state, and crouching state
            jumping = self.is_player_jumping(player_id)
            self.game_state.animation_component.update_pivot_points(player, running, jumping, crouching)
            
        # print(f"Player position updated: id={player_id}, new state={self.game_state.players[player_id]}")

    def update_player_crouch(self, player_id, crouching):
        if player_id in self.game_state.players:
            self.game_state.players[player_id]['crouching'] = crouching
            print(f"Player {player_id} crouching state updated: {crouching}")

    def player_jump(self, player_id):
        if player_id in self.game_state.players:
            player = self.game_state.players[player_id]
            ground_level = self.game_state.get_ground_level(player['x'])
            
            if player['y'] == ground_level + self.game_state.player_height and not self.is_player_jumping(player_id):
                player['vy'] = self.game_state.jump_velocity
                self.player_jumping_states[player_id] = True
                self.player_jump_start_times[player_id] = time.time()
                print(f"Player jumped: id={player_id}, new vy={self.game_state.jump_velocity}")

    def is_player_jumping(self, player_id):
        if player_id in self.player_jumping_states and self.player_jumping_states[player_id]:
            current_time = time.time()
            jump_start_time = self.player_jump_start_times.get(player_id, current_time)
            
            if current_time - jump_start_time >= self.jump_duration:
                self.player_jumping_states[player_id] = False
                return False
            return True
        return False

    def update_player_mouse_position(self, player_id, position):
        if player_id in self.game_state.players:
            self.game_state.player_mouse_positions[player_id] = position
            jumping = self.player_jumping_states.get(player_id, False)
            self.game_state.animation_component.update_pivot_points(self.game_state.players[player_id], False, jumping)
            print(f"Updated mouse position for player {player_id}: {position}")

    def update_player_guard(self, player_id, guard_state):
        if player_id in self.game_state.player_guard_states:
            self.game_state.player_guard_states[player_id] = guard_state
            print(f"Player guard state updated: id={player_id}, guard={guard_state}")

    def update(self):
        current_time = time.time()
        for player_id, player in self.game_state.players.items():
            if self.is_player_jumping(player_id):
                player['y'] += player['vy'] * self.game_state.update_interval
                player['vy'] -= self.game_state.gravity * self.game_state.update_interval
                
                ground_level = self.game_state.get_ground_level(player['x'])
                if player['y'] <= ground_level + self.game_state.player_height:
                    player['y'] = ground_level + self.game_state.player_height
                    player['vy'] = 0
                    
                    # Only reset jumping state if the jump duration has passed
                    if current_time - self.player_jump_start_times[player_id] >= self.jump_duration:
                        self.player_jumping_states[player_id] = False

            # Update animation
            running = self.player_speeds.get(player_id, 0) > self.game_state.base_speed
            jumping = self.is_player_jumping(player_id)
            crouching = self.player_crouching_states.get(player_id, False)
            self.game_state.animation_component.update_pivot_points(player, running, jumping, crouching)
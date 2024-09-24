import json
import time
import math
import numpy as np

class AnimationComponent:
    def __init__(self, game_state):
        self.game_state = game_state
        self.animation_frames = self.load_animation_frames()
        self.player_animation_states = {}
        self.run_cycle_distance = 2.5
        self.walk_cycle_distance = 0.4
        self.crouch_cycle_distance = 0.85
        self.idle_transition_duration = 0.2
        self.walk_run_transition_duration = 0.5
        self.turn_duration = 0.1
        self.turn_exit_duration = 0.2
        self.jump_start_duration = 0.1
        self.jump_apex_duration = 0.2
        self.jump_land_duration = 0.1
        self.crouch_transition_duration = 0.2

    def load_animation_frames(self):
        with open('game_app/animation_frames.json', 'r') as file:
            frames = json.load(file)
            for frame in frames.values():
                if 'r_elbow' not in frame:
                    frame['r_elbow'] = [0.85, 0.8]
                if 'r_hand' not in frame:
                    frame['r_hand'] = [0.9, 1.1]
            return frames

    def get_frame(self, frame_name, direction):
        if direction == 'backward':
            flipped_frame_name = f"{frame_name}_FLIP"
            if flipped_frame_name in self.animation_frames:
                return self.animation_frames[flipped_frame_name]
            else:
                return self.flip_frame(self.animation_frames[frame_name])
        return self.animation_frames[frame_name]

    def get_idle_frame(self, direction, crouching):
        if crouching:
            return self.get_frame('CROUCH_IDLE', direction)
        return self.get_frame('IDLE', direction)

    def set_player_animation_state(self, player_id, state):
        self.player_animation_states[player_id] = {
            'current_state': state,
            'last_update_time': time.time(),
            'is_moving': False,
            'is_running': False,
            'is_jumping': False,
            'is_crouching': False,
            'jump_start_time': None,
            'jump_phase': None,
            'direction': 'forward',
            'facing_direction': 'forward',
            'last_x_position': None,
            'distance_traveled': 0.0,
            'cycle_progress': 0.0,
            'last_direction': 'forward',
            'idle_transition_start': None,
            'last_movement_frame': None,
            'walk_run_transition_start': None,
            'walk_run_blend_factor': 0.0,
            'turn_start_time': None,
            'is_turning': False,
            'crouch_transition_start': None,
            'crouch_blend_factor': 0.0
        }

    def flip_frame(self, frame):
        flipped_frame = {}
        for key, value in frame.items():
            flipped_frame[key] = [1 - value[0], value[1]]
        return flipped_frame

    def bicubic_interpolate(self, start_frame, end_frame, t):
        interpolated_frame = {}
        for key in start_frame.keys():
            p0 = np.array(start_frame[key])
            p1 = np.array(end_frame[key])
            
            # get tangent vectors
            t0 = (p1 - p0) * 0.5
            t1 = t0
            
            # hermite basis functions
            h00 = 2*t**3 - 3*t**2 + 1
            h10 = t**3 - 2*t**2 + t
            h01 = -2*t**3 + 3*t**2
            h11 = t**3 - t**2
            
            # final interpolation
            interpolated_point = h00*p0 + h10*t0 + h01*p1 + h11*t1
            interpolated_frame[key] = interpolated_point.tolist()
        
        return interpolated_frame

    def interpolate_to_idle(self, start_frame, end_frame, progress):
        return self.bicubic_interpolate(start_frame, end_frame, progress)

    def get_cycle_frame(self, cycle_progress, blend_factor, direction, crouching):
        if crouching:
            return self.get_crouch_cycle_frame(cycle_progress, direction)
        else:
            walk_frame = self.get_walk_frame(cycle_progress, direction)
            run_frame = self.get_run_frame(cycle_progress, direction)
            return self.blend_frames(walk_frame, run_frame, blend_factor)

    def get_crouch_cycle_frame(self, cycle_progress, direction):
        if cycle_progress < 0.5:
            start_frame = self.get_frame(self.crouch_cycle_frames[0], direction)
            end_frame = self.get_frame(self.crouch_cycle_frames[1], direction)
            t = cycle_progress * 2
        else:
            start_frame = self.get_frame(self.crouch_cycle_frames[1], direction)
            end_frame = self.get_frame(self.crouch_cycle_frames[0], direction)
            t = (cycle_progress - 0.5) * 2
        return self.bicubic_interpolate(start_frame, end_frame, t)

    def get_crouch_cycle_frame(self, cycle_progress, direction):
        if cycle_progress < 0.5:
            start_frame = self.get_frame('CROUCH_PASS', direction)
            end_frame = self.get_frame('CROUCH_REACH', direction)
            t = cycle_progress * 2
        else:
            start_frame = self.get_frame('CROUCH_REACH', direction)
            end_frame = self.get_frame('CROUCH_PASS', direction)
            t = (cycle_progress - 0.5) * 2
        return self.bicubic_interpolate(start_frame, end_frame, t)

    def get_walk_frame(self, cycle_progress, direction):
        if cycle_progress < 0.5:
            start_frame = self.get_frame('WALK_PASS', direction)
            end_frame = self.get_frame('WALK_REACH', direction)
            t = cycle_progress * 2
        else:
            start_frame = self.get_frame('WALK_REACH', direction)
            end_frame = self.get_frame('WALK_PASS', direction)
            t = (cycle_progress - 0.5) * 2
        return self.bicubic_interpolate(start_frame, end_frame, t)

    def get_run_frame(self, cycle_progress, direction):
        if cycle_progress < 0.5:
            start_frame = self.get_frame('RUN_PASS', direction)
            end_frame = self.get_frame('RUN_REACH', direction)
            t = cycle_progress * 2
        else:
            start_frame = self.get_frame('RUN_REACH', direction)
            end_frame = self.get_frame('RUN_PASS', direction)
            t = (cycle_progress - 0.5) * 2
        return self.bicubic_interpolate(start_frame, end_frame, t)

    def get_turn_frame(self, turn_progress, from_direction, to_direction, crouching):
        if crouching:
            start_frame = self.get_frame('CROUCH_IDLE', from_direction)
            end_frame = self.get_frame('CROUCH_IDLE', to_direction)
        else:
            start_frame = self.get_frame('TURN_PASS', from_direction)
            end_frame = self.get_frame('TURN_REACH', to_direction)
        
        return self.bicubic_interpolate(start_frame, end_frame, turn_progress)

    def get_jump_frame(self, jump_progress, direction, crouching):
        if not crouching:
            if jump_progress < 0.5:  # Rising
                start_frame = self.get_frame('JUMP_START_END', direction)
                end_frame = self.get_frame('JUMP_APEX', direction)
                t = jump_progress * 2
            else:  # Falling
                start_frame = self.get_frame('JUMP_APEX', direction)
                end_frame = self.get_frame('JUMP_START_END', direction)
                t = (jump_progress - 0.5) * 2
            
            return self.bicubic_interpolate(start_frame, end_frame, t)
        else:
            # For now, we'll use the CROUCH_IDLE frame for jumping while crouching
            return self.get_frame('CROUCH_IDLE', direction)

    def interpolate_frames(self, frame1, frame2, t):
        return self.bicubic_interpolate(frame1, frame2, t)

    def blend_frames(self, frame1, frame2, blend_factor):
        blended_frame = {}
        for key in frame1.keys():
            blended_frame[key] = [
                frame1[key][0] * (1 - blend_factor) + frame2[key][0] * blend_factor,
                frame1[key][1] * (1 - blend_factor) + frame2[key][1] * blend_factor
            ]
        return blended_frame

    def update_pivot_points(self, player, running, jumping, crouching):
        player_id = next(id for id, p in self.game_state.players.items() if p == player)
        
        if player_id not in self.player_animation_states:
            self.set_player_animation_state(player_id, 'IDLE')
        
        animation_state = self.player_animation_states[player_id]
        current_time = time.time()
        
        if animation_state['last_x_position'] is None:
            animation_state['last_x_position'] = player['x']

        distance_traveled = abs(player['x'] - animation_state['last_x_position'])
        animation_state['distance_traveled'] += distance_traveled

        was_moving = animation_state['is_moving']
        animation_state['is_moving'] = distance_traveled > 0.001

        if animation_state['is_moving']:
            new_movement_direction = 'forward' if player['x'] > animation_state['last_x_position'] else 'backward'
            animation_state['facing_direction'] = new_movement_direction
        else:
            new_movement_direction = animation_state['direction']

        direction_changed = new_movement_direction != animation_state['direction']

        # Determine the base frame based on crouching state and direction
        base_frame = self.get_idle_frame(animation_state['facing_direction'], crouching)
        current_frame = base_frame  # Initialize current_frame with base_frame

        # Handle crouching transition
        if crouching != animation_state['is_crouching']:
            if animation_state['crouch_transition_start'] is None:
                animation_state['crouch_transition_start'] = current_time
                if animation_state['is_moving']:
                    # If already moving, start from the current movement frame
                    animation_state['crouch_start_frame'] = animation_state['last_movement_frame'] or self.get_cycle_frame(
                        animation_state['cycle_progress'],
                        animation_state['walk_run_blend_factor'],
                        animation_state['facing_direction'],
                        not crouching
                    )
                    animation_state['crouch_end_frame'] = self.get_crouch_cycle_frame(
                        animation_state['cycle_progress'],
                        animation_state['facing_direction']
                    )
                else:
                    # If not moving, transition between idle frames
                    animation_state['crouch_start_frame'] = self.get_idle_frame(animation_state['facing_direction'], not crouching)
                    animation_state['crouch_end_frame'] = self.get_idle_frame(animation_state['facing_direction'], crouching)

        if animation_state['crouch_transition_start'] is not None:
            transition_progress = (current_time - animation_state['crouch_transition_start']) / self.crouch_transition_duration
            animation_state['crouch_blend_factor'] = min(1.0, transition_progress)
            
            if transition_progress >= 1.0:
                animation_state['crouch_transition_start'] = None
                animation_state['is_crouching'] = crouching
                current_frame = animation_state['crouch_end_frame']
            else:
                current_frame = self.interpolate_frames(
                    animation_state['crouch_start_frame'],
                    animation_state['crouch_end_frame'],
                    animation_state['crouch_blend_factor']
                )
        else:
            # Handle direction change for idle turning only
            if direction_changed and not animation_state['is_turning'] and not animation_state['is_jumping'] and not crouching:
                animation_state['is_turning'] = True
                animation_state['turn_start_time'] = current_time
                animation_state['turn_start_frame'] = animation_state['last_movement_frame'] or self.get_frame('TURN_PASS', animation_state['direction'])
                animation_state['target_direction'] = new_movement_direction
                animation_state['from_direction'] = animation_state['direction']

            # Handle jumping
            if jumping and not animation_state['is_jumping']:
                animation_state['is_jumping'] = True
                animation_state['jump_start_time'] = current_time
                animation_state['jump_phase'] = 'start'
                animation_state['jump_start_frame'] = animation_state['last_movement_frame'] or base_frame
            
            if animation_state['is_jumping']:
                jump_duration = self.jump_start_duration + self.jump_apex_duration + self.jump_land_duration
                jump_progress = (current_time - animation_state['jump_start_time']) / jump_duration
                
                if jump_progress >= 1.0:
                    animation_state['is_jumping'] = False
                    animation_state['jump_phase'] = None
                    animation_state['jump_end_time'] = current_time
                    animation_state['jump_end_frame'] = self.get_jump_frame(1.0, animation_state['direction'], crouching)
                else:
                    jump_frame = self.get_jump_frame(jump_progress, animation_state['direction'], crouching)
                    if jump_progress < 0.3:
                        current_frame = self.interpolate_frames(animation_state['jump_start_frame'], jump_frame, jump_progress / 0.3)
                    else:
                        current_frame = jump_frame
                    animation_state['current_state'] = 'JUMPING'
            elif animation_state.get('jump_end_time'):
                jump_end_progress = (current_time - animation_state['jump_end_time']) / self.jump_land_duration
                if jump_end_progress >= 1.0:
                    animation_state['jump_end_time'] = None
                    current_frame = self.get_cycle_frame(0, animation_state['walk_run_blend_factor'], animation_state['direction'], crouching) if animation_state['is_moving'] else base_frame
                else:
                    end_frame = self.get_cycle_frame(0, animation_state['walk_run_blend_factor'], animation_state['direction'], crouching) if animation_state['is_moving'] else base_frame
                    current_frame = self.interpolate_frames(animation_state['jump_end_frame'], end_frame, jump_end_progress)
            elif animation_state['is_turning']:
                turn_progress = (current_time - animation_state['turn_start_time']) / self.turn_duration
                if turn_progress >= 1.0:
                    animation_state['is_turning'] = False
                    animation_state['turn_exit_start_time'] = current_time
                    turn_end_frame = self.get_turn_frame(1.0, animation_state['from_direction'], animation_state['target_direction'], crouching)
                    animation_state['turn_exit_start_frame'] = turn_end_frame
                    animation_state['direction'] = animation_state['target_direction']
                    current_frame = animation_state['turn_exit_start_frame']
                else:
                    turn_frame = self.get_turn_frame(turn_progress, animation_state['from_direction'], animation_state['target_direction'], crouching)
                    current_frame = self.interpolate_frames(animation_state['turn_start_frame'], turn_frame, turn_progress)
                animation_state['current_state'] = 'TURNING'
            elif animation_state.get('turn_exit_start_time'):
                exit_progress = (current_time - animation_state['turn_exit_start_time']) / self.turn_exit_duration
                if exit_progress >= 1.0:
                    animation_state['turn_exit_start_time'] = None
                    current_frame = self.get_cycle_frame(0, animation_state['walk_run_blend_factor'], animation_state['direction'], crouching) if animation_state['is_moving'] else base_frame
                else:
                    exit_end_frame = self.get_cycle_frame(0, animation_state['walk_run_blend_factor'], animation_state['direction'], crouching) if animation_state['is_moving'] else base_frame
                    current_frame = self.interpolate_frames(animation_state['turn_exit_start_frame'], exit_end_frame, exit_progress)
            else:
                # Handle walk/run transition and movement
                if animation_state['is_running'] != running and not crouching:
                    if animation_state['walk_run_transition_start'] is None:
                        animation_state['walk_run_transition_start'] = current_time
                else:
                    animation_state['walk_run_transition_start'] = None

                if animation_state['walk_run_transition_start'] is not None:
                    transition_progress = (current_time - animation_state['walk_run_transition_start']) / self.walk_run_transition_duration
                    if running:
                        animation_state['walk_run_blend_factor'] = min(1.0, transition_progress)
                    else:
                        animation_state['walk_run_blend_factor'] = max(0.0, 1.0 - transition_progress)
                    
                    if transition_progress >= 1.0:
                        animation_state['walk_run_transition_start'] = None
                        animation_state['is_running'] = running
                else:
                    animation_state['walk_run_blend_factor'] = 1.0 if running else 0.0

                # Modify the movement handling to incorporate crouch state
                if animation_state['is_moving']:
                    animation_state['idle_transition_start'] = None

                    if crouching:
                        cycle_distance = self.crouch_cycle_distance
                    else:
                        cycle_distance = self.run_cycle_distance * animation_state['walk_run_blend_factor'] + \
                                         self.walk_cycle_distance * (1 - animation_state['walk_run_blend_factor'])
                    
                    animation_state['cycle_progress'] += distance_traveled / cycle_distance
                    animation_state['cycle_progress'] %= 1.0  # Ensure it wraps around to 0 when it reaches 1

                    if crouching:
                        moving_frame = self.get_crouch_cycle_frame(
                            animation_state['cycle_progress'],
                            animation_state['facing_direction']
                        )
                    else:
                        moving_frame = self.get_cycle_frame(
                            animation_state['cycle_progress'], 
                            animation_state['walk_run_blend_factor'],
                            animation_state['facing_direction'],
                            False
                        )
                    
                    # Interpolate between crouching and standing frames during transition
                    if animation_state['crouch_blend_factor'] > 0 and animation_state['crouch_blend_factor'] < 1:
                        standing_frame = self.get_cycle_frame(
                            animation_state['cycle_progress'],
                            animation_state['walk_run_blend_factor'],
                            animation_state['facing_direction'],
                            False
                        )
                        crouching_frame = self.get_crouch_cycle_frame(
                            animation_state['cycle_progress'],
                            animation_state['facing_direction']
                        )
                        current_frame = self.interpolate_frames(
                            standing_frame,
                            crouching_frame,
                            animation_state['crouch_blend_factor']
                        )
                    else:
                        current_frame = moving_frame

                    animation_state['current_state'] = 'MOVING'
                    animation_state['last_movement_frame'] = current_frame
                else:
                    if was_moving:
                        animation_state['idle_transition_start'] = current_time
                    
                    if animation_state['idle_transition_start'] is not None:
                        idle_progress = min(1.0, (current_time - animation_state['idle_transition_start']) / self.idle_transition_duration)
                        start_frame = animation_state['last_movement_frame'] or base_frame
                        
                        # Interpolate between crouching and standing idle frames
                        standing_idle_frame = self.get_idle_frame(animation_state['facing_direction'], False)
                        crouching_idle_frame = self.get_idle_frame(animation_state['facing_direction'], True)
                        
                        if animation_state['crouch_blend_factor'] > 0 and animation_state['crouch_blend_factor'] < 1:
                            interpolated_idle_frame = self.interpolate_frames(
                                standing_idle_frame,
                                crouching_idle_frame,
                                animation_state['crouch_blend_factor']
                            )
                        else:
                            interpolated_idle_frame = crouching_idle_frame if crouching else standing_idle_frame
                        
                        current_frame = self.interpolate_to_idle(start_frame, interpolated_idle_frame, idle_progress)
                        
                        if idle_progress == 1.0:
                            animation_state['idle_transition_start'] = None
                            animation_state['last_movement_frame'] = None
                    else:
                        current_frame = base_frame
                    
                    animation_state['current_state'] = 'IDLE' if not crouching else 'CROUCHING'

        # Update direction only if moving
        if animation_state['is_moving']:
            animation_state['direction'] = new_movement_direction
            animation_state['facing_direction'] = new_movement_direction

        player['pivot_points'] = current_frame
        animation_state['last_x_position'] = player['x']
        animation_state['last_update_time'] = current_time

    def get_animation_state(self, player_id):
        state = self.player_animation_states.get(player_id, {})
        return {
            'current': state.get('current_state', 'IDLE'),
            'direction': state.get('direction', 'forward'),
            'is_moving': state.get('is_moving', False),
            'is_running': state.get('is_running', False),
            'is_jumping': state.get('is_jumping', False),
            'is_crouching': state.get('is_crouching', False),  # New: Include crouching state
            'jump_phase': state.get('jump_phase', None),
            'distance_traveled': state.get('distance_traveled', 0.0),
            'last_direction': state.get('last_direction', 'forward'),
            'cycle_progress': state.get('cycle_progress', 0.0),
            'idle_transition_progress': (current_time - state.get('idle_transition_start', current_time)) / self.idle_transition_duration if state.get('idle_transition_start') is not None else 1.0,
            'walk_run_blend_factor': state.get('walk_run_blend_factor', 0.0),
            'is_turning': state.get('is_turning', False),
            'turn_progress': (current_time - state.get('turn_start_time', current_time)) / self.turn_duration if state.get('turn_start_time') is not None else 1.0,
            'jump_progress': (current_time - state.get('jump_start_time', current_time)) / (self.jump_start_duration + self.jump_apex_duration + self.jump_land_duration) if state.get('jump_start_time') is not None else 0.0,
            'crouch_blend_factor': state.get('crouch_blend_factor', 0.0)  # New: Include crouch blend factor
        }
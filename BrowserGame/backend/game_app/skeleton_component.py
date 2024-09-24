import math
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Joint:
    name: str
    parent: str
    position: List[float]
    min_angle: float
    max_angle: float
    length: float

class SkeletonComponent:
    def __init__(self):
        self.joints = {
            "root": Joint("root", None, [0.5, 1.1], 0, 0, 0),
            "spine_02": Joint("spine_02", "root", [0.475, 0.9], -15, 15, 0.2),
            "spine_01": Joint("spine_01", "spine_02", [0.5, 0.65], -10, 10, 0.25),
            "neck": Joint("neck", "spine_01", [0.5, 0.5], -30, 30, 0.15),
            "head": Joint("head", "neck", [0.65, 0.1], -45, 45, 0.2),
            "l_shoulder": Joint("l_shoulder", "spine_01", [0.35, 0.6], -90, 90, 0.2),
            "l_elbow": Joint("l_elbow", "l_shoulder", [0.25, 0.8], 0, 145, 0.25),
            "l_hand": Joint("l_hand", "l_elbow", [0.2, 1.2], -20, 20, 0.2),
            "r_shoulder": Joint("r_shoulder", "spine_01", [0.65, 0.6], -90, 90, 0.2),
            "r_elbow": Joint("r_elbow", "r_shoulder", [0.8, 0.8], 0, 145, 0.25),
            "r_hand": Joint("r_hand", "r_elbow", [0.9, 1.2], -20, 20, 0.2),
            "l_hip": Joint("l_hip", "root", [0.4, 1.1], -90, 45, 0.15),
            "l_knee": Joint("l_knee", "l_hip", [0.4, 1.55], 0, 145, 0.4),
            "l_ankle": Joint("l_ankle", "l_knee", [0.2, 1.95], -20, 20, 0.15),
            "r_hip": Joint("r_hip", "root", [0.6, 1.1], -90, 45, 0.15),
            "r_knee": Joint("r_knee", "r_hip", [0.75, 1.55], 0, 145, 0.4),
            "r_ankle": Joint("r_ankle", "r_knee", [0.72, 1.95], -20, 20, 0.15),
        }

    def update_joint_position(self, joint_name: str, new_position: List[float]) -> bool:
        if joint_name not in self.joints:
            return False

        joint = self.joints[joint_name]
        parent = self.joints.get(joint.parent)

        if parent:
            # Calculate the new angle and length
            dx = new_position[0] - parent.position[0]
            dy = new_position[1] - parent.position[1]
            new_angle = math.degrees(math.atan2(dy, dx))
            new_length = math.sqrt(dx**2 + dy**2)

            # Check angle constraints
            if new_angle < joint.min_angle or new_angle > joint.max_angle:
                return False

            # Check length constraint (allow some flexibility, e.g., ±10%)
            if not (0.9 * joint.length <= new_length <= 1.1 * joint.length):
                return False

        # Update the joint position if constraints are satisfied
        joint.position = new_position
        return True

    def get_all_joint_positions(self) -> dict:
        return {name: joint.position for name, joint in self.joints.items()}

    def apply_inverse_kinematics(self, end_effector: str, target_position: List[float], chain_length: int = 3):
        chain = self._get_joint_chain(end_effector, chain_length)
        
        for _ in range(10):  # Max iterations for IK solver
            for joint in reversed(chain):
                current_end = self.joints[end_effector].position
                to_target = [target_position[0] - current_end[0], target_position[1] - current_end[1]]
                to_joint = [current_end[0] - joint.position[0], current_end[1] - joint.position[1]]
                
                angle = math.atan2(
                    to_target[0] * to_joint[1] - to_target[1] * to_joint[0],
                    to_target[0] * to_joint[0] + to_target[1] * to_joint[1]
                )
                
                self._rotate_joint(joint.name, angle)
            
            # Check if we're close enough to the target
            if self._distance(self.joints[end_effector].position, target_position) < 0.01:
                break

    def _get_joint_chain(self, end_effector: str, chain_length: int) -> List[Joint]:
        chain = []
        current = self.joints[end_effector]
        
        while current and len(chain) < chain_length:
            chain.append(current)
            current = self.joints.get(current.parent)
        
        return chain

    def _rotate_joint(self, joint_name: str, angle: float):
        joint = self.joints[joint_name]
        parent = self.joints.get(joint.parent)
        
        if parent:
            current_angle = math.atan2(
                joint.position[1] - parent.position[1],
                joint.position[0] - parent.position[0]
            )
            new_angle = current_angle + angle
            
            # Clamp the new angle to the joint's constraints
            new_angle = max(math.radians(joint.min_angle), min(math.radians(joint.max_angle), new_angle))
            
            # Calculate the new position based on the new angle and the joint's length
            new_x = parent.position[0] + joint.length * math.cos(new_angle)
            new_y = parent.position[1] + joint.length * math.sin(new_angle)
            
            joint.position = [new_x, new_y]

    def _distance(self, pos1: List[float], pos2: List[float]) -> float:
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
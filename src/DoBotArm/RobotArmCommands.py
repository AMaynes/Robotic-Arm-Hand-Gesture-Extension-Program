import json
from src.DoBotArm.DobotArm import DobotArm  # Import specific arm classes here and make sure to update config file

class RobotArmInterface:
    def connect(self, port, baudrate):
        """Connect to the robotic arm."""
        raise NotImplementedError

    def move_to(self, x, y, z, r=0):
        """Move the arm to a specified position."""
        raise NotImplementedError
    
    def enableRail(self, enable):
        """Move the arm to a specified position."""
        raise NotImplementedError
    
    def rail_move_to(self, x, y, z, l, r=0):
        """Move the arm to a specified position."""
        raise NotImplementedError

    def set_gripper_state(self, state):
        """Set the gripper state (open/close)."""
        raise NotImplementedError
    
    def disconnect(self):
        """Connect to the robotic arm."""
        raise NotImplementedError

# Function to load the appropriate robotic arm from config
def load_robotic_arm(config_path="config.json"):
    """
    Load a robotic arm instance based on the configuration file.
    :param config_path: Path to the configuration JSON file.
    :return: An instance of the appropriate robotic arm class.
    """
    with open(config_path, "r") as f:
        config = json.load(f)

    arm_type = config["arm_type"]
    if arm_type == "Dobot":
        return DobotArm()
    # Add other arm types here as needed
    else:
        raise ValueError(f"Unsupported arm type: {arm_type}")
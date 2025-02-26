import DobotDllType as dType


class DobotArm:
    """
    A class to control and interface with the Dobot robotic arm.
    Provides methods for connection, movement, and gripper control.
    """

    def __init__(self):
        """Initialize DobotArm with empty API and version references."""
        self.api = None
        self.gobal_version = None

    def is_connected(self):
        """Check if the Dobot arm is connected."""
        return self.api is not None

    def get_port(self):
        """Get the serial port used for connection."""
        return self.port

    def get_baudrate(self):
        """Get the baudrate used for connection."""
        return self.baudrate

    def connect(self, port, baudrate):
        """
        Connect to the Dobot arm and initialize default parameters.

        Args:
            port (str): Serial port for connection
            baudrate (int): Communication baudrate

        Returns:
            bool: True if connection successful, False otherwise
        """
        self.api = dType.load()
        state = dType.ConnectDobot(self.api, port, baudrate)[0]

        ## todo check if this is where the issue is to connect to the dobot.
        if state == dType.DobotConnect.DobotConnect_NoError:
            self.gobal_version = dType.GetDeviceVersion(self.api)
            dType.SetQueuedCmdClear(self.api)
            dType.SetHOMEParams(self.api, 170, 0, 0, -90, 0)
            dType.SetPTPCommonParams(self.api, 100, 100, isQueued=0)
            dType.SetCPCommonParams(self.api, 100, 100, isQueued=0)
            dType.SetCPRHoldEnable(self.api, True)
            dType.SetPTPCmd(self.api, 2, 170, 0, 0, -90, isQueued=0)
            print("Connected to Dobot and moved to home position!")
            return True
        print("Failed to connect to Dobot. Dobot Arm line 52")
        return False



    def move_to(self, x, y, z):
        """
        Move the arm to an absolute position using Cartesian coordinates.

        Args:
            x (float): Target X coordinate
            y (float): Target Y coordinate
            z (float): Target Z coordinate
        """
        dType.SetQueuedCmdClear(self.api)
        pose = dType.GetPose(self.api)
        current_x, current_y, current_z = pose[0], pose[1], pose[2]
        x -= current_x
        y -= current_y
        z -= current_z
        dType.SetCPCmd(self.api, 0, x, y, z, 100, isQueued=0)

    def enableRail(self, enable):
        """
        Enable or disable the linear rail system.

        Args:
            enable (bool): True to enable, False to disable
        """
        dType.SetQueuedCmdClear(self.api)
        dType.SetDeviceWithL(self.api, enable, self.gobal_version[0], 0)

    def rail_move_to(self, x, y, z, l, r=0):
        """
        Move the arm using the linear rail system.

        Args:
            x (float): Target X coordinate
            y (float): Target Y coordinate
            z (float): Target Z coordinate
            l (float): Linear rail position
            r (float, optional): Rotation angle. Defaults to 0
        """
        dType.SetQueuedCmdClear(self.api)
        dType.SetPTPWithLCmd(self.api, 1, x, y, z, r, l, isQueued=0)

    def set_gripper_state(self, state):
        """
        Control the gripper state.

        Args:
            state (bool): True to close gripper, False to open
        """
        dType.SetQueuedCmdClear(self.api)
        dType.SetEndEffectorGripper(self.api, state, 1, isQueued=0)

    def disconnect(self):
        """Disconnect from the Dobot arm."""
        dType.DisconnectDobot(self.api)
        print("Disconnected from Dobot.")
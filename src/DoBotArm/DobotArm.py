import RoboticArms.SDKs.DobotDllType as dType
import atexit


class DobotArm:

    def __init__(self):
        self.api = None
        self.gobal_version = None

    def connect(self, port, baudrate):
        self.api = dType.load()
        state = dType.ConnectDobot(self.api, port, baudrate)[0]
        if state == dType.DobotConnect.DobotConnect_NoError:
            self.gobal_version = dType.GetDeviceVersion(self.api)
            dType.SetQueuedCmdClear(self.api)
            dType.SetHOMEParams(self.api, 170, 0, 0, -90, 0)
            dType.SetPTPCommonParams(self.api, 100, 100,  isQueued=0)
            dType.SetCPCommonParams(self.api, 100, 100,  isQueued=0)
            dType.SetCPRHoldEnable(self.api, True)
            dType.SetPTPCmd(self.api, 2, 170, 0, 0, -90, isQueued=0)
            print("Connected to Dobot and moved to home position!")
            # if we have connected to the dobot then make sure anytime we exit we disconnect
            atexit.register(self.turnOffAnnoyingThing)
            atexit.register(self.disconnect)
            return True
        print("Failed to connect to Dobot.")
        return False

    def move_to(self, x, y, z):
        dType.SetQueuedCmdClear(self.api)
        pose = dType.GetPose(self.api)
        current_x, current_y, current_z = pose[0], pose[1], pose[2]
        x -= current_x
        y -= current_y
        z -= current_z
        dType.SetCPCmd(self.api, 0, x, y, z, 100, isQueued=0)

    def enableRail(self, enable):
        dType.SetQueuedCmdClear(self.api)
        dType.SetDeviceWithL(self.api, enable, self.gobal_version[0], 0)

    def rail_move_to(self, x, y, z, l, r=0): # Linear Rail System Movement
        dType.SetQueuedCmdClear(self.api)
        dType.SetPTPWithLCmd(self.api, 1, x, y, z, r, l, isQueued=0)

    def set_gripper_state(self, state):
        dType.SetQueuedCmdClear(self.api)
        dType.SetEndEffectorGripper(self.api, 1, state, isQueued=0)

    # Turn off air compressor on close program bc its really annoying
    def turnOffAnnoyingThing(self):
        dType.SetQueuedCmdClear(self.api)
        dType.SetEndEffectorGripper(self.api, 0, 0, isQueued=0)

    def disconnect(self):
        dType.DisconnectDobot(self.api)
        print("Disconnected from Dobot.")

import threading
import DobotDllType as dType
from serial.tools import list_ports



available_ports = list_ports.comports()
print(f'Available ports: {[x.device for x in available_ports]}')

CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

api = dType.load()

state = dType.ConnectDobot(api, "COM5", 115200)[0]
print("Connect status:",CON_STR[state])

if (state == dType.DobotConnect.DobotConnect_NoError):
    dType.SetQueuedCmdClear(api)

    dType.SetHOMEParams(api, 200, 0, 50, 0, isQueued = 1)
    dType.SetPTPJointParams(api, 50, 50, 50, 50, 50, 50, 50, 50, isQueued = 1)
    dType.SetPTPCommonParams(api, 50, 50, isQueued = 1)

    dType.SetHOMECmd(api, temp = 0, isQueued = 1)

    dType.SetPTPCmd(api, dType.movementMode, 201, 5, 40, 0, isQueued = 1)

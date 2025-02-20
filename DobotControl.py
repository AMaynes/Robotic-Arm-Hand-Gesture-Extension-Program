import threading
import DobotDllType as dType
from serial.tools import list_ports

# TODO:  write try catch blocks to find where in here the code or dll files may not be working

# List and display all available serial ports
available_ports = list_ports.comports()
print(f'Available ports: {[x.device for x in available_ports]}')

# Dictionary mapping connection status codes to human-readable messages
CON_STR = {
    dType.DobotConnect.DobotConnect_NoError: "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

# Load the Dobot DLL into memory and get CDLL instance
api = dType.load()

# Establish connection with Dobot on COM5 port at 115200 baud rate
state = dType.ConnectDobot(api, "COM5", 115200)[0]
print("Connect status:", CON_STR[state])

# If connection is successful, proceed with robot control
if (state == dType.DobotConnect.DobotConnect_NoError):

    # Clear the command queue before sending new commands
    dType.SetQueuedCmdClear(api)

    # Configure motion parameters
    # HOME parameters: velocity and acceleration for each axis
    dType.SetHOMEParams(api, 200, 200, 200, 200, isQueued=1)
    # Joint movement parameters: velocity and acceleration for each joint
    dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued=1)
    # Common PTP (Point-To-Point) parameters: velocity ratio and acceleration ratio
    dType.SetPTPCommonParams(api, 100, 100, isQueued=1)

    # Send robot to home position
    dType.SetHOMECmd(api, temp=0, isQueued=1)

    # Execute a sequence of PTP movements
    for i in range(0, 5):
        # Alternate between positive and negative 50mm offsets
        if i % 2 == 0:
            offset = 50
        else:
            offset = -50
        # Move in linear mode (PTPMOVLXYZMode) with specified offsets for X, Y, Z coordinates
        lastIndex = \
        dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, 200 + offset, offset, offset, offset, isQueued=1)[0]

    # Begin executing the command queue
    dType.SetQueuedCmdStartExec(api)

    # Wait until all commands in the queue are executed
    while lastIndex > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(100)

    # Stop the command queue execution
    dType.SetQueuedCmdStopExec(api)

# Disconnect from the Dobot
dType.DisconnectDobot(api)


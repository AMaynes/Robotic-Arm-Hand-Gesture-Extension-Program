import cv2
import mediapipe as mp
import time
import numpy as np
import threading
import DobotDllType as dType
from serial.tools import list_ports
import math

"""
DEPENDENCIES:
================
Python version 3.7-3.11
math import
Time import
CV2 import
Mediapipe import
DobotDLLType.py file import
serial.tools import to list ports

IF DOBOT IS NOT CONNECTING:
================================

Press the reset button on the back of the dobot. When it goes red after reseting, simply move the arm manually and it should turn green.
If it does not turn green, you may need to reload the firmware via DobotStudio. After that, try reset button and move manually again.
"""

THUMB_IDX = 4
WRIST_IDX = 0
MID_KNUCKLE_IDX = 9
RING_KNUCKLE_IDX = 13
INDEX_FINGER_IDX = 8
INDEX_FINGER_BIDX = 5
MID_FINGER_IDX = 12
MID_FINGER_BIDX = 9
RING_FINGER_IDX = 16
RING_FINGER_BIDX = 13
PINKY_FINGER_IDX = 20
PINKY_FINGER_BIDX = 17
GESTURE_UPDATE_INTERVAL = 10
THRESHOLD = 0.1
global_api = ""

# Connect to dobot and test movement
def connectToDobot():
    global global_api
    available_ports = list_ports.comports()  # List ports
    print(f'Available ports: {[x.device for x in available_ports]}')

    CON_STR = {
        dType.DobotConnect.DobotConnect_NoError: "DobotConnect_NoError",
        dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
        dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

    global_api = dType.load()

    state = dType.ConnectDobot(global_api, "COM5", 115200)[0]  # Connect to Dobot
    print("Connect status:", CON_STR[state])

    if (state != dType.DobotConnect.DobotConnect_NoError):  # Exit program if dobot does not connect without error
        exit

    dType.SetQueuedCmdClear(global_api)  # Clear cmd que

    # Set movement params
    dType.SetHOMEParams(global_api, 170, 0, 0, -90, 0)
    dType.SetPTPJointParams(global_api, 200, 200, 200, 200, 200, 200, 200, 200, 0)
    dType.SetPTPJumpParams(global_api, 10, 200, 0)
    dType.SetPTPCommonParams(global_api, 200, 200, 0)

    dType.SetPTPCmd(global_api, 2, 170, 0, 0, 0, isQueued=0)  # Move Dobot to starting position
    dType.dSleep(10000)  # Await for dobot to move to starting position

    pos = dType.GetPose(global_api)  # Get current position of Dobot
    
    x = pos[0]
    y = pos[1]
    z = pos[2]
    rHead = pos[3]

# Normalize coordinate passed into the function on a scale of 0-1
def normalizeCoord(coord, maxCoord):
    newCoord = coord / maxCoord
    return newCoord

# Checks if a position is reachable
def is_position_reachable(x, y, z):
    # Arm Specifications (in mm)
    L1 = 135  # Length from Joint J1 to Joint J2
    L2 = 147  # Length from Joint J2 to Joint J3 (end-effector)

    # Joint Limits (in degrees)
    joint_limits = {
        'J1': (-90, 90),  # Joint J1 limits
        'J2': (5, 80),      # Joint J2 limits
        'J3': (-5, 75)     # Joint J3 limits
    }

   # Calculate planar distance r & total distance D from Joint J1 to target point
    r = math.hypot(x, y)
    euclidOffset = 1.5712 * z + 58.3408
    D = math.hypot(r, z) - euclidOffset

    # Check if target is within reach by distance
    if D > (L1 + L2) or D < abs(L1 - L2):
        print("ERROR: Position out of reach")
        return False

    # Calculate theta1 (Joint J1 angle)
    theta1 = math.atan2(y, x)
    theta1 = math.degrees(theta1)
    theta1 = round(theta1, 2)

    # Calculate theta2 (Joint J2 angle) using law of cosines
    try:
        phi = (L1**2 + D**2 - L2**2) / (2 * L1 * D)
        theta2 = math.degrees(math.acos(phi))
        theta2 = 90 - theta2 # 90 deg is marked as 0 deg in the dobot so an offset is req
        theta2 = round(theta2, 2)
    except ValueError:
        print("ERROR: Theta2 calculation out of range by cosine domain exceedence")
        return False

    # Calculate theta3 (Joint J3 angle) using law of sines and prev calculations for J2 ---> 180 - ('Left of elbow' angle + elbow angle) = 'right of elbow' angle
    try:
        theta3 = 180 - (math.degrees(math.asin( (D * math.sin( math.acos(phi) )) / L2)) + 90 - theta2)
        J3Offset = 0.7270 * z - 1.3
        theta3 = theta3 - J3Offset
        theta3 = round(theta3, 2)
    except ValueError:
        print("ERROR: Theta3 calculation out of range by sine domain exceedence")
        return False


    # Check if all joint angles are within mechanical limits
    within_limits = (
        joint_limits['J1'][0] <= theta1 <= joint_limits['J1'][1] and
        joint_limits['J2'][0] <= theta2 <= joint_limits['J2'][1] and
        joint_limits['J3'][0] <= theta3 <= joint_limits['J3'][1]
    )

    # Output joint angle results & if pos is reachable
    if within_limits:
        return True
    else:
        return False

# Interprets a closed hand
def closed_hand(landmarks):
    is_index_finger_closed = (landmarks[INDEX_FINGER_IDX].y - landmarks[INDEX_FINGER_BIDX].y) < THRESHOLD
    is_middle_finger_closed = (landmarks[MID_FINGER_IDX].y - landmarks[MID_FINGER_BIDX].y) < THRESHOLD
    is_ring_finger_closed = (landmarks[RING_FINGER_IDX].y - landmarks[RING_FINGER_BIDX].y) < THRESHOLD
    is_pinky_finger_closed = (landmarks[PINKY_FINGER_IDX].y - landmarks[PINKY_FINGER_BIDX].y) < THRESHOLD

    return (is_index_finger_closed and is_middle_finger_closed and is_ring_finger_closed and is_pinky_finger_closed)

# Interprets a open hand
def open_hand(landmarks):
    is_index_finger_open = (landmarks[INDEX_FINGER_IDX].y - landmarks[INDEX_FINGER_BIDX].y) > THRESHOLD
    is_middle_finger_open = (landmarks[MID_FINGER_IDX].y - landmarks[MID_FINGER_BIDX].y) > THRESHOLD
    is_ring_finger_open = (landmarks[RING_FINGER_IDX].y - landmarks[RING_FINGER_BIDX].y) > THRESHOLD
    is_pinky_finger_open = (landmarks[PINKY_FINGER_IDX].y - landmarks[PINKY_FINGER_BIDX].y) > THRESHOLD
 
    return (is_index_finger_open and is_middle_finger_open and is_ring_finger_open and is_pinky_finger_open)

# Determines z axis position (depth perception relative to the camera)
def estimate_depth(landmarks):
    # Calculate distance btwn wrist and middle knuckle
    distance = math.sqrt(abs(landmarks[MID_KNUCKLE_IDX].x - landmarks[WRIST_IDX].x) ** 2 + abs(landmarks[MID_KNUCKLE_IDX].y - landmarks[WRIST_IDX].y) ** 2)
    distance = (distance*100*4)-80

    return distance

# Begin hand tracking control of dobot
def beginTracking():
    global global_api
    
    # Opening cameras (0 for the default camera, 1 for an additional camera)
    videoCap1 = cv2.VideoCapture(0)  # Camera 1 for hand tracking
    videoCap2 = cv2.VideoCapture(1)  # Camera 2 for live feed

    lastFrameTime = 0
    frame = 0
    handSolution = mp.solutions.hands
    hands = handSolution.Hands()
    recent_positions = []
    stillOpen = False

    while True:
        frame += 1
        # Reading images from both cameras
        success1, img1 = videoCap1.read()
        success2, img2 = videoCap2.read()

        if success1 and success2:
            # Resize images to fit side by side
            img1_resized = cv2.resize(img1, (1080, 720))
            img2_resized = cv2.resize(img2, (1080, 720))

            # Concatenate images side by side
            combined_img = np.hstack((img1_resized, img2_resized))

            # Bring combined window to the foreground
            cv2.namedWindow("Combined Camera Output", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("Combined Camera Output", cv2.WND_PROP_TOPMOST, 1)
            cv2.resizeWindow("Combined Camera Output", 1920, 1080)  # Set to an enlarged window size

            # Processing the first camera feed for hand tracking
            imgRGB1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2RGB)
            recHands1 = hands.process(imgRGB1)

            # FPS calculation for the first camera feed
            thisFrameTime = time.time()
            fps = 1 / (thisFrameTime - lastFrameTime)
            lastFrameTime = thisFrameTime

            # Display FPS on the first camera feed
            cv2.putText(combined_img, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)

            # Hand tracking and gesture recognition
            if recHands1.multi_hand_landmarks:
                for hand in recHands1.multi_hand_landmarks:
                    sum_x = sum_y = palm_x = palm_y = 0

                    # Draw landmarks on the hand
                    for datapoint_id, point in enumerate(hand.landmark):
                        pix_h, pix_w, c = img1_resized.shape
                        x, y = int(point.x * pix_w), int(point.y * pix_h)
                        if datapoint_id in [MID_KNUCKLE_IDX, RING_KNUCKLE_IDX, WRIST_IDX]:
                            cv2.circle(combined_img, (x, y), 10, (0, 0, 255), cv2.FILLED)
                            sum_x += x
                            sum_y += y
                        else:
                            cv2.circle(combined_img, (x, y), 10, (255, 0, 255), cv2.FILLED)

                    # Calculate palm coordinates
                    palm_x = sum_x / 3
                    palm_y = sum_y / 3
                    cv2.circle(combined_img, (int(palm_x), int(palm_y)), 10, (255, 0, 0), cv2.FILLED) # Draw palm landmark
                    palm_x = (normalizeCoord(palm_x, pix_w)*640) - 320 # Convert to 320 scale then split the screen into +/- coords
                    palm_y = (normalizeCoord(palm_y, pix_h)*336) - 16 # Convert to 320 scale then split at +/- coords at 5% of 320
                    palm_z = estimate_depth(hand.landmark)*1.25

                    # Update recent positions (up to last 4 recent positions)
                    recent_positions.append((palm_x, palm_y, palm_z))
                    if len(recent_positions) > 4:
                        recent_positions.pop(0)

                    avg_x = sum(pos[0] for pos in recent_positions) / len(recent_positions)
                    avg_y = sum(pos[1] for pos in recent_positions) / len(recent_positions)
                    avg_z = sum(pos[2] for pos in recent_positions) / len(recent_positions)

                    """ COMMENTED OUT BECAUSE IT SUCKS SO FAR - Meant to reduce unintended movement that occurs due to hand trembles and such
                    if len(recent_positions) == 4:
                        distanceTraveled = math.sqrt(((recent_positions[3][0] - recent_positions[2][0])**2) + ((recent_positions[3][1] - recent_positions[2][1])**2) + ((recent_positions[3][2] - recent_positions[2][2])**2))
                    else: distanceTraveled = 5

                    if distanceTraveled >= 5: movement = True
                    else: movement = False
                    """

                    
                # Gesture recognition & movement tracking every GESTURE_UPDATE_INTERVAL frames
                if frame % GESTURE_UPDATE_INTERVAL == 0:

                    #Hand Gesture Interpretations
                    if closed_hand(hand.landmark):
                        stillOpen = False
                        dType.SetEndEffectorGripper(global_api, 1, 1, isQueued=0)
                    elif open_hand(hand.landmark) and stillOpen == False:
                        stillOpen = True
                        dType.SetEndEffectorGripper(global_api, 1, 0, isQueued=0)

                    #Dobot Movement
                    if 0 == 0:
                        # Note, currently this is for when the camera is overhead and upside down horizontally
                        final_x = avg_y
                        final_y = avg_x
                        final_z = avg_z
                        rHead = -90
                        if(is_position_reachable(final_x, final_y, final_z)):
                            cv2.circle(combined_img, (100, 100), 10, (255, 0, 0), cv2.FILLED) # Tracking Indicator
                            dType.SetQueuedCmdClear(global_api)
                            dType.SetPTPCmd(global_api, 2, final_x, final_y, final_z, rHead, isQueued=0)  # Move Dobot immediately to the position
                            time.sleep(0.05)
                        else:
                            cv2.circle(combined_img, (100, 100), 10, (0, 0, 255), cv2.FILLED) # Not Tracking Indicator

                    frame = 0

            # Display the combined camera feed
            cv2.imshow("Combined Camera Output", combined_img)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    videoCap1.release()
    videoCap2.release()
    cv2.destroyAllWindows()

connectToDobot()  # Connect to dobot, home it, and test movement

beginTracking()  # Begin hand tracking control of dobot
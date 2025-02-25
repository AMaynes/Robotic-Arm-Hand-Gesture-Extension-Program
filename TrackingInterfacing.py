import cv2
import mediapipe as mp
import time
import numpy as np
import HandGestureInterpretation # type: ignore
from Abstracting import DobotDllType as dType
from Abstracting.src import ControlModes
from serial.tools import list_ports
import math

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
    dType.SetPTPLParams(global_api, 200, 200, isQueued=0)

    dType.SetPTPCmd(global_api, 2, 170, 0, 0, 0, isQueued=0)  # Move Dobot to starting position
    dType.dSleep(10000)  # Await for dobot to move to starting position

    pos = dType.GetPose(global_api)  # Get current position of Dobot
    
    x = pos[0]
    y = pos[1]
    z = pos[2]
    rHead = pos[3]

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
    lockedCoords = [170, 0, 10]
    track = True
    controlMode = 1

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
                    palm_x = ((palm_x / pix_w)*640) - 320 # Convert to 320 scale then split the screen into +/- coords
                    palm_y = ((palm_y / pix_h)*336) - 16 # Convert to 320 scale then split at +/- coords at 5% of 320
                    palm_z = estimate_depth(hand.landmark)*1.25

                    # Update recent positions (up to last 4 recent positions)
                    recent_positions.append((palm_x, palm_y, palm_z))
                    if len(recent_positions) > 4:
                        recent_positions.pop(0)

                    avg_x = sum(pos[0] for pos in recent_positions) / len(recent_positions)
                    avg_y = sum(pos[1] for pos in recent_positions) / len(recent_positions)
                    avg_z = sum(pos[2] for pos in recent_positions) / len(recent_positions)
                    
                # Gesture recognition & movement tracking every GESTURE_UPDATE_INTERVAL frames
                if frame % GESTURE_UPDATE_INTERVAL == 0:

                    #Hand Gesture Interpretations
                    if HandGestureInterpretation.interpretHandGest(hand.landmark) == 1: # Tracking Disengaged/Engaged
                        if track == False:
                            track = True
                            time.sleep(2) # Make system wait 3 seconds before re-engaging tracking
                        else:
                            track = False
                            time.sleep(2) # Make system wait 3 seconds before dis-engaging tracking
                    elif HandGestureInterpretation.interpretHandGest(hand.landmark) == 2: # Rail Control Mode
                        if controlMode != 1:
                            lockedCoords = [avg_y, avg_x, avg_z] # Stores the current coordinates so the dobot can maintain this position
                        controlMode = 1
                    elif HandGestureInterpretation.interpretHandGest(hand.landmark) == 3: # Arm Control Mode
                        controlMode = 2
                    elif HandGestureInterpretation.interpretHandGest(hand.landmark) == 4: # Closed Hand
                        dType.SetEndEffectorGripper(global_api, 1, 1, isQueued=0)
                        dType.SetEndEffectorGripper(global_api, 0, 1, isQueued=1)
                    elif HandGestureInterpretation.interpretHandGest(hand.landmark) == 5: # Open Hnad
                        dType.SetEndEffectorGripper(global_api, 1, 0, isQueued=0)
                        dType.SetEndEffectorGripper(global_api, 0, 0, isQueued=1)


                    #Dobot Movement
                    if track == True:
                        # Note, currently this is for when the camera is overhead and horizontal plane is upside down aka inverted
                        if controlMode == 1: # Rail control mode
                            if(ControlModes.is_position_reachable(controlMode, avg_y, avg_x, avg_z)): # Intentional x&y swap due to axis' being opposite btwn cam and dobot
                                ControlModes.moveRail(global_api, lockedCoords[0], lockedCoords[1], lockedCoords[2], avg_y)
                                cv2.circle(combined_img, (100, 100), 10, (255, 0, 0), cv2.FILLED) # Tracking Indicator
                            else:
                                cv2.circle(combined_img, (100, 100), 10, (0, 0, 255), cv2.FILLED) # Not Tracking Indicator
                        if controlMode == 2: # Arm control mode
                            if(ControlModes.is_position_reachable(controlMode, avg_y, avg_x, avg_z)): # Intentional x&y swap due to axis' being opposite btwn cam and dobot
                                ControlModes.moveDobot(global_api, avg_y, avg_x, avg_z)
                                cv2.circle(combined_img, (100, 100), 10, (255, 0, 0), cv2.FILLED) # Tracking Indicator
                            else:
                                cv2.circle(combined_img, (100, 100), 10, (0, 0, 255), cv2.FILLED) # Not Tracking Indicator
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
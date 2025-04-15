import cv2
import mediapipe as mp
import time, sys
import numpy as np
import json
from src.DoBotArm import gestureInterpretation, coordProcessing
from src.fileLoading.fileLoader import *
from src.GUI.CameraSelector import getCameraOne, getCameraTwo
import atexit


WRIST_IDX = 0
MID_KNUCKLE_IDX = 9
RING_KNUCKLE_IDX = 13
GESTURE_UPDATE_INTERVAL = 10


# Detects arm type and connect to it
def initialize_robotic_arm(arm_type):
    # config_path = "config.json"

    # Load the configuration
    # with open(config_path, "r") as f:
    #     config = json.load(f)

    config = load_json_file("config.json")

    # Find the configuration for the specified arm type
    arm_config = next((arm for arm in config["robotic_arms"] if arm["arm_type"] == arm_type), None)
    if not arm_config:
        raise ValueError(f"Robotic arm type '{arm_type}' not found in configuration.")

    # Load the appropriate robotic arm class
    if arm_config["arm_type"] == "Dobot":
        from src.DoBotArm.DobotArm import DobotArm  # type: ignore
        robotic_arm = DobotArm()
    elif arm_config["arm_type"] == "uArm":
        from RoboticArms.uArm import UArm  # type: ignore
        robotic_arm = UArm()
    else:
        raise ValueError(f"Unsupported arm type: {arm_config['arm_type']}")

    # Connect to the robotic arm
    if robotic_arm.connect(arm_config["port"], arm_config["baudrate"]):
        print(f"{arm_type} connected successfully on port {arm_config['port']} with baudrate {arm_config['baudrate']}.")
        
        # Move to home position and initialize gripper
        robotic_arm.move_to(200, 0, 50)
        robotic_arm.set_gripper_state(1)
        return robotic_arm
    else:
        print(f"Failed to connect to {arm_type}.")
        sys.exit(f"Program terminated: Unable to connect to {arm_type}.")

# Cam display settings & variables functions
def camSettings(img1, img2):
    # Resize camera images to fit side by side & Concatenate images side by side
    # img1_resized = cv2.resize(img1, (640, 480))
    img1_resized = cv2.resize(img1, (1080, 720))


    if img2 is not None:
        # img2_resized = cv2.resize(img2, (640, 480))
        img2_resized = cv2.resize(img2, (1080, 720))
        combined_img = np.hstack((img1_resized, img2_resized))
    else:
        combined_img = img1_resized
        img2_resized = None


    # Process the first camera feed for hand tracking
    imgRGB1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2RGB)

    return (img1_resized, img2_resized, combined_img, imgRGB1)

#*****************************************************************

# Camera & Tracking Function
def beginTracking(arm_type):
    videoCap1 = None
    videoCap2 = None
    img2 = None

    def cleanUp():
        if videoCap1 is not None:
            videoCap1.release()
        if videoCap2 is not None:
            videoCap2.release()
        cv2.destroyAllWindows()

    atexit.register(cleanUp)

    # Open cameras (0 for the default camera, 1 for an additional camera)
    # Declare the type of robotic arm that is being used
    robotic_arm = initialize_robotic_arm(arm_type)
    hand_physics = coordProcessing.HandPhysics()


    #Get the index of the cameras we want to us
    cam1 = getCameraOne()
    cam2 = getCameraTwo()

    videoCap1 = cv2.VideoCapture(cam1)  # Camera 1 for hand tracking
    if(cam2 is not None):
        videoCap2 = cv2.VideoCapture(cam2)  # Camera 2 for live feed
    else:
        videoCap2 = None

    # Initialize required variables
    lastFrameTime = 0
    frame = 0
    handSolution = mp.solutions.hands
    hands = handSolution.Hands()
    robotic_arm.enableRail(0) # Disable Rail
    robotic_arm.set_gripper_state(0)
    track = False
    controlMode = 1
    lastGesture = 0

    # Bring combined window to the foreground
    cv2.namedWindow("Combined Camera Output", cv2.WINDOW_NORMAL)


    # cv2.resizeWindow("Combined Camera Output", 720, 360)
    cv2.resizeWindow("Combined Camera Output", 1920, 1080)

    #todo figure out why the window isn't responding when opened at home we can comment out anycomands to the arm


    # Video camera loop
    while True:
        frame += 1
        # Reading images from both cameras
        success1, img1 = videoCap1.read()
        if videoCap2 is not None:
            success2, img2 = videoCap2.read()
        else:
            im2 = None
            success2 = True

        # Ensure camera is working and define camera settings (including frame rate calculations)
        if not(success1 and (videoCap2 is None or success2)): # Quit program if camera error occurs
            print("Error: One camera did not work correctly.")
            quit(1)
        else:
            (img1_resized, img2_resized, combined_img, imgRGB1) = camSettings(img1, img2)
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
                cv2.circle(combined_img, (int(palm_x), int(palm_y)), 10, (255, 0, 0), cv2.FILLED)
                print("\nX: ", round(palm_x), "  -  Y: ", round(palm_y))

                invertedY = pix_h - palm_y # Invert Y because 0 Y is top of the camera
                invertedX = pix_w - palm_x # Invert X because 0 X is left of the camera
                normalPalm_x = invertedX / pix_w
                lineaRail_x = palm_x / pix_w # linearRail x value will be different than an invertedX
                palm_x = (normalPalm_x * 760) - 380 # Translate into a +/- 380 x-axis
                palm_y = ((invertedY / pix_h) * 516) - 16 # Translate into a +500/-16 y-axis

                print("Dobot X: ", round(palm_x), "  -  Dobot Y: ", round(palm_y))

                palm_z = coordProcessing.CoordinateProcessing.determineZCoord(hand.landmark)

            # Check for gesture updates
            if frame % GESTURE_UPDATE_INTERVAL == 0:

                # Gesture handling
                gesture = gestureInterpretation.interpretHandGest(hand.landmark)
                if lastGesture != gesture: # Only process gestures when the user intends one
                    if gesture == 1:  # Toggle tracking
                        track = not track
                    elif gesture == 2:  # Rail control mode
                        controlMode = 1
                        robotic_arm.enableRail(1) # Enable Rail
                    elif gesture == 3:  # Arm control mode
                        controlMode = 2
                        robotic_arm.enableRail(0) # Disable Rail
                    elif gesture == 4:  # Close gripper
                        robotic_arm.set_gripper_state(1)
                    elif gesture == 5:  # Open gripper
                        robotic_arm.set_gripper_state(0)
                    lastGesture = gesture

                frame = 0

            # Predict next hand position using physics
            predicted_position = hand_physics.predictNextPosition((palm_y, palm_x, palm_z), 0.1)
            lineaRail = lineaRail_x * 1000 # 1000 is perfect, if there are issues, its with the coordinate calibration

            # Movement handling (if track enables and predicted position is reachable then move to proposed position)
            if track and coordProcessing.CoordinateProcessing.isPositionValid(controlMode, palm_y, palm_x, palm_z, lineaRail):
                if controlMode == 1:  # Rail control mode
                    robotic_arm.rail_move_to(200, 0, 0, lineaRail)
                    cv2.circle(combined_img, (100, 100), 10, (255, 0, 0), cv2.FILLED) # Blue Tracking Indicator (Tracking Indicator)

                elif controlMode == 2:  # Arm control mode
                    # Current position
                    print("MOVING TO: ", predicted_position[0], predicted_position[1], predicted_position[2])
                    robotic_arm.move_to(predicted_position[0], predicted_position[1], predicted_position[2])
                    cv2.circle(combined_img, (100, 100), 10, (255, 0, 0), cv2.FILLED) # Blue Tracking Indicator (Tracking Indicator)
            else:
                cv2.circle(combined_img, (100, 100), 10, (0, 0, 255), cv2.FILLED) # Red Tracking Indicator (Not Tracking Indicator)

            # Display the camera feed
            # cv2.imshow("Combined Camera Output", combined_img)
            # Get the current window size
            win_name = "Combined Camera Output"
            _, _, win_w, win_h = cv2.getWindowImageRect(win_name)

            # Make sure width and height are valid before resizing
            if win_w > 0 and win_h > 0:
                display_img = cv2.resize(combined_img, (win_w, win_h))
            else:
                display_img = combined_img

            cv2.imshow(win_name, display_img)

            # Detect if window is closed
            if cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE) < 1:
                break


    # old shut off function
        # # Break loop on 'q' key press
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     robotic_arm.turnOffAnnoyingThing()
        #     robotic_arm.disconnect()
        #     exit(0)
        #     break


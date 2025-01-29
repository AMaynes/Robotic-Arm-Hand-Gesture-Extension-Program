import cv2
import mediapipe as mp
import time
import numpy as np
import json
import CoordGestureInterpretation
import sys

WRIST_IDX = 0
MID_KNUCKLE_IDX = 9
RING_KNUCKLE_IDX = 13
GESTURE_UPDATE_INTERVAL = 10

# Detects arm type and connect to it
def initialize_robotic_arm(arm_type, config_path="config.json"):
    # Load the configuration
    with open(config_path, "r") as f:
        config = json.load(f)

    # Find the configuration for the specified arm type
    arm_config = next((arm for arm in config["robotic_arms"] if arm["arm_type"] == arm_type), None)
    if not arm_config:
        raise ValueError(f"Robotic arm type '{arm_type}' not found in configuration.")

    # Load the appropriate robotic arm class
    if arm_config["arm_type"] == "Dobot":
        from RoboticArms.DobotArm import DobotArm  # type: ignore
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

#*****************************************************************

# Camera & Tracking Function
def beginTracking(arm_type):
    # Open cameras (0 for the default camera, 1 for an additional camera)
    robotic_arm = initialize_robotic_arm(arm_type)
    hand_physics = CoordGestureInterpretation.HandPhysics()
    videoCap1 = cv2.VideoCapture(0)  # Camera 1 for hand tracking
    videoCap2 = cv2.VideoCapture(1)  # Camera 2 for live feed

    lastFrameTime = 0
    frame = 0
    handSolution = mp.solutions.hands
    hands = handSolution.Hands()
    robotic_arm.enableRail(0) # Disable Rail
    robotic_arm.set_gripper_state(0)
    track = False
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
            cv2.resizeWindow("Combined Camera Output", 1920, 1080)

            # Process the first camera feed for hand tracking
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
                    cv2.circle(combined_img, (int(palm_x), int(palm_y)), 10, (255, 0, 0), cv2.FILLED)
                    normalPalm_x = palm_x / pix_w
                    palm_x = ((palm_x / pix_w) * 760) - 380
                    palm_y = ((palm_y / pix_h) * 516) - 16
                    palm_z = CoordGestureInterpretation.CoordinateProcessing.estimate_depth(hand.landmark)

                # Gesture recognition & movement tracking every GESTURE_UPDATE_INTERVAL frames
                if frame % 2 == 0:
                    if frame % GESTURE_UPDATE_INTERVAL == 0:
                        gesture = CoordGestureInterpretation.interpretHandGest(hand.landmark)

                        # Gesture handling
                        if gesture == 1:  # Toggle tracking
                            track = not track
                            time.sleep(2)  # Wait before toggling again
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

                        frame = 0
                    
                    predicted_position = hand_physics.predict_next_position((palm_y, palm_x, palm_z), 0.1)
                    lineaRail = normalPalm_x * 1000 # 1000 is perfect, if there are issues, its with the coordinate calibration

                    # Movement handling
                    if track and CoordGestureInterpretation.CoordinateProcessing.is_position_reachable(controlMode, predicted_position[0], predicted_position[1], predicted_position[2], lineaRail):
                        if controlMode == 1:  # Rail control mode
                            robotic_arm.rail_move_to(200, 0, 0, lineaRail)
                            cv2.circle(combined_img, (100, 100), 10, (255, 0, 0), cv2.FILLED) # Green Tracking Indicator (Tracking Indicator)
                            
                        elif controlMode == 2:  # Arm control mode
                            # Current position
                            robotic_arm.move_to(predicted_position[0], predicted_position[1], predicted_position[2])
                            cv2.circle(combined_img, (100, 100), 10, (255, 0, 0), cv2.FILLED) # Green Tracking Indicator (Tracking Indicator)
                    else:
                        cv2.circle(combined_img, (100, 100), 10, (0, 0, 255), cv2.FILLED) # Red Tracking Indicator (Not Tracking Indicator)

            # Display the combined camera feed
            cv2.imshow("Combined Camera Output", combined_img)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            robotic_arm.set_gripper_state(0)
            robotic_arm.disconnect()
            break

    # Release resources
    videoCap1.release()
    videoCap2.release()
    cv2.destroyAllWindows()

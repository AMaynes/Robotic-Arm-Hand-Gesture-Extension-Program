import cv2
import mediapipe as mp
import time
import numpy as np
import json
import CoordGestureInterpretation
import sys

# Constants for specific hand landmarks and update intervals
WRIST_IDX = 0
MID_KNUCKLE_IDX = 9
RING_KNUCKLE_IDX = 13
GESTURE_UPDATE_INTERVAL = 10

# we want to invert the camera so that the hand is being mirrored on the screen as you see it.


def initialize_robotic_arm(arm_type, config_path="config.json"):
    """
    Initializes the robotic arm based on the specified arm type and configuration.

    :param arm_type: The type of robotic arm (e.g., 'Dobot', 'uArm').
    :param config_path: Path to the configuration file (default is "config.json").
    :return: An instance of the initialized robotic arm.
    :raises ValueError: If the arm type is not found in the configuration or unsupported.
    """
    with open(config_path, "r") as f:
        config = json.load(f)

    # Find the configuration for the specified arm type
    arm_config = next((arm for arm in config["robotic_arms"] if arm["arm_type"] == arm_type), None)
    if not arm_config:
        raise ValueError(f"Robotic arm type '{arm_type}' not found in configuration.")

    # Load the appropriate robotic arm class based on configuration
    if arm_config["arm_type"] == "Dobot":
        from DobotArm import DobotArm  # type: ignore
        robotic_arm = DobotArm()
    elif arm_config["arm_type"] == "uArm":
        from RoboticArms.uArm import UArm  # type: ignore
        robotic_arm = UArm()
    else:
        raise ValueError(f"Unsupported arm type: {arm_config['arm_type']}")

    # Attempt to connect to the robotic arm
    if robotic_arm.connect(arm_config["port"], arm_config["baudrate"]):
        print(f"{arm_type} connected successfully on port {arm_config['port']} with baudrate {arm_config['baudrate']}.")

        # Move to home position and initialize gripper
        robotic_arm.move_to(200, 0, 50)
        robotic_arm.set_gripper_state(1)
        return robotic_arm
    else:
        print(f"Failed to connect to {arm_type}.")
        sys.exit(f"Program terminated: Unable to connect to {arm_type}.")


# *****************************************************************

def beginTracking(arm_type):
    """
    Begins tracking hand gestures and controls the robotic arm based on the gestures detected.

    :param arm_type: The type of robotic arm (e.g., 'Dobot', 'uArm').
    """
    robotic_arm = initialize_robotic_arm(arm_type)  # Initialize robotic arm based on provided type
    hand_physics = CoordGestureInterpretation.HandPhysics()  # Initialize hand physics for gesture tracking
    videoCap1 = cv2.VideoCapture(0)  # Camera 1 for hand tracking
    videoCap2 = cv2.VideoCapture(1)  # Camera 2 for live feed

    lastFrameTime = 0
    frame = 0
    handSolution = mp.solutions.hands
    hands = handSolution.Hands()  # Mediapipe hand tracking solution
    robotic_arm.enableRail(0)  # Disable Rail by default
    robotic_arm.set_gripper_state(0)  # Set gripper to open by default
    track = False  # Tracking state (off by default)
    controlMode = 1  # Default control mode (rail control)

    print("Initiate averages to 0")
    currX = 0
    currY = 0
    palmX_sum = 0
    palmY_sum = 0
    count = 0

    while True:
        frame += 1
        success1, img1 = videoCap1.read()  # Capture image from camera 1 (hand tracking)
        success2, img2 = videoCap2.read()  # Capture image from camera 2 (live feed)

        if success1 and success2:
            # Resize and concatenate both images for side-by-side display
            img1_resized = cv2.resize(img1, (1080, 720))
            img2_resized = cv2.resize(img2, (1080, 720))
            combined_img = np.hstack((img1_resized, img2_resized))

            # Bring combined camera feed window to the front
            cv2.namedWindow("Combined Camera Output", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("Combined Camera Output", cv2.WND_PROP_TOPMOST, 1)
            cv2.resizeWindow("Combined Camera Output", 1920, 1080)

            # Process the first camera feed for hand tracking
            imgRGB1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2RGB)
            recHands1 = hands.process(imgRGB1)

            # FPS calculation for performance monitoring
            thisFrameTime = time.time()
            fps = 1 / (thisFrameTime - lastFrameTime)
            lastFrameTime = thisFrameTime

            # Display FPS on the combined camera feed
            cv2.putText(combined_img, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)

            # Hand tracking and gesture recognition
            if recHands1.multi_hand_landmarks:
                for hand in recHands1.multi_hand_landmarks:
                    sum_x = sum_y = palm_x = palm_y = 0
                    normalPalm_x = 0

                    # Draw hand landmarks on the combined camera feed
                    # Draw landmarks on the hand and calculate palm position
                    for datapoint_id, point in enumerate(hand.landmark):
                        pix_h, pix_w, c = img1_resized.shape
                        x, y = int(point.x * pix_w), int(point.y * pix_h)
                        if datapoint_id in [MID_KNUCKLE_IDX, RING_KNUCKLE_IDX, WRIST_IDX]:
                            cv2.circle(combined_img, (x, y), 10, (0, 0, 255), cv2.FILLED)  # Draw specific points in red
                            sum_x += x
                            sum_y += y
                        else:
                            cv2.circle(combined_img, (x, y), 10, (255, 0, 255),
                                       cv2.FILLED)  # Draw other points in purple

                    # Calculate palm coordinates and normalize them
                    palm_x = sum_x / 3
                    palm_y = sum_y / 3
                    cv2.circle(combined_img, (int(palm_x), int(palm_y)), 10, (255, 0, 0),
                               cv2.FILLED)  # Draw palm in blue
                    normalPalm_x = palm_x / pix_w
                    palm_x = ((palm_x / pix_w) * 760) - 380
                    palm_y = ((palm_y / pix_h) * 516) - 16
                    palm_z = CoordGestureInterpretation.CoordinateProcessing.estimate_depth(hand.landmark)

                    palmX_sum += palm_x
                    palmY_sum += palm_y
                    count += 1


                    average_palm_x = palmX_sum / count
                    average_palm_y = palmY_sum / count

            #todo refine when averages should be coaught up so it looks natural
                    if(count % 30 == 0):
                        currX = average_palm_x
                        currY = average_palm_y


                    diffX = abs(abs(palm_x) - abs(average_palm_x))
                    diffY = abs(abs(palm_y) - abs(average_palm_y))

                    if(diffX > 55 or diffY > 55):
                        print("reset averages")
                        palmX_sum = 0
                        palmY_sum = 0
                        count = 0
                        #todo make average

                    # chang_in_x = abs(average_palm_x - currX)
                    # chang_in_y = abs(average_palm_y - currY)

                # Handle gesture recognition and movement tracking
                if frame % GESTURE_UPDATE_INTERVAL == 0:
                    print("X, Y, Z: ", palm_x, palm_y, palm_z)

                    print("Avg, X, Y: ", average_palm_x, average_palm_y)

                    print("Curr X, Y: ", currX, currY)

                    #todo make cords less shaky
                    gesture = CoordGestureInterpretation.interpretHandGest(hand.landmark)  # Interpret hand gesture

                    # Handle different gestures for controlling the robotic arm


                    if gesture == 1:  # Toggle tracking state
                        track = not track
                        time.sleep(2)  # Prevent repeated toggles in quick succession
                    elif gesture == 2:  # Enable Rail control mode
                        controlMode = 1
                        robotic_arm.enableRail(1)  # Enable Rail
                    elif gesture == 3:  # Enable Arm control mode

                        controlMode = 2
                        robotic_arm.enableRail(0)  # Disable Rail
                    elif gesture == 4:  # Close the gripper
                        robotic_arm.set_gripper_state(1)
                    elif gesture == 5:  # Open the gripper
                        robotic_arm.set_gripper_state(0)

                    frame = 0

                # Predict the next hand position for movement control

                    #todo replace with averages
                    predicted_position = hand_physics.predict_next_position((currX, currY, palm_z), 0.1)
                    lineaRail = normalPalm_x * 1000  # Convert palm x to rail position

                # Handle arm movement based on gesture control
                if track and CoordGestureInterpretation.CoordinateProcessing.is_position_reachable(controlMode,
                                                                                                   predicted_position[
                                                                                                       0],
                                                                                                   predicted_position[
                                                                                                       1],
                                                                                                   predicted_position[

                                                                                                       2], lineaRail):

                    if controlMode == 1:  # Rail control mode
                        robotic_arm.rail_move_to(200, 0, 0, lineaRail)
                        cv2.circle(combined_img, (100, 100), 10, (255, 0, 0), cv2.FILLED)  # Green tracking indicator
                    elif controlMode == 2:  # Arm control mode
                        #todo remove this print
                        print("We are in control mode 2!")
                        robotic_arm.move_to(predicted_position[0], predicted_position[1], predicted_position[2])
                        cv2.circle(combined_img, (100, 100), 10, (255, 0, 0), cv2.FILLED)  # Green tracking indicator
                else:
                    cv2.circle(combined_img, (100, 100), 10, (0, 0, 255),
                               cv2.FILLED)  # Red tracking indicator (not tracking)

            # Display the combined camera feed with hand tracking and gesture info
            cv2.imshow("Combined Camera Output", combined_img)

        # Exit the loop if the user presses 'q'
        if cv2.waitKey(2) & 0xFF == ord('q'):
            robotic_arm.set_gripper_state(0)  # Close the gripper before exiting
            robotic_arm.disconnect()  # Disconnect the robotic arm
            break

    # Release the video capture objects and close any open windows
    videoCap1.release()
    videoCap2.release()
    cv2.destroyAllWindows()

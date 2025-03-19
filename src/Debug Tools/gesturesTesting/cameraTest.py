import time

import cv2
import mediapipe as mp
import gestures

GESTURE_UPDATE_INTERVAL = 30

# Open camera
videoCap1 = cv2.VideoCapture(0)
lastFrameTime = 0
frame = 0
handSolution = mp.solutions.hands
hands = mp.solutions.hands.Hands(
    model_complexity=0,  # Set to 0 to reduce model load time
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

mpDraw = mp.solutions.drawing_utils
trackEngaged = False
lastGesture = 0
camResWidth = float(videoCap1.get(cv2.CAP_PROP_FRAME_WIDTH))
camResHeight = float(videoCap1.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Main loop for hand tracking and gesture detection

while True:
    frame += 1
    success1, img1 = videoCap1.read()
    if success1:

        imgRGB1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)

        recHands1 = hands.process(imgRGB1)

        # FPS calculation

        thisFrameTime = time.time()

        fps = 1 / (thisFrameTime - lastFrameTime)

        lastFrameTime = thisFrameTime

        # Display FPS on the first camera feed

        cv2.putText(img1, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 230, 0), 2)

        # Hand tracking and gesture recognition
        # Draw a cross at the location of the robot arm base for reference

        if recHands1.multi_hand_landmarks:

            for hand in recHands1.multi_hand_landmarks:

                mpDraw.draw_landmarks(img1, hand, handSolution.HAND_CONNECTIONS)

                # Check for hand gestures.py every GESTURE_UPDATE_INTERVAL frames

                if frame % GESTURE_UPDATE_INTERVAL == 0:
                    # Gesture handling
                    gesture = gestures.interpretHandGest(hand.landmark)
                    if lastGesture != gesture:
                        if gesture == 1:  # Toggle tracking
                            if trackEngaged: trackEngaged = False
                            else: trackEngaged = True
                            print("Track:", trackEngaged)
                        elif gesture == 2:  # Rail control mode
                            print("Rail Control Mode")
                        elif gesture == 3:  # Arm control mode
                            print("Arm Control Mode")
                        elif gesture == 4:  # Close gripper
                            print("Close End Effector")
                        elif gesture == 5:  # Open gripper
                            print("Open End Effector")
                        lastGesture = gesture
                    frame = 0

        # Display the first camera feed

        cv2.imshow("Camera 1 Output", img1)

    # Break loop on 'q' key press

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

videoCap1.release()

cv2.destroyAllWindows()
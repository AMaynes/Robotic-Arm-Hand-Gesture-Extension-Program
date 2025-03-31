import cv2
import mediapipe as mp
import time
import math

THUMB_IDX = 4
THUMB_KNUCKLE_BIDX = 1
INDEX_FINGER_IDX = 8
INDEX_KNUCKLE_BIDX = 5
MID_FINGER_IDX = 12
MID_KNUCKLE_BIDX = 9
RING_FINGER_IDX = 16
RING_KNUCKLE_BIDX = 13
PINKY_FINGER_IDX = 20
PINKY_KNUCKLE_BIDX = 17
GESTURE_UPDATE_INTERVAL = 15
THRESHOLD = 0.1

videoCap1 = cv2.VideoCapture(0)
lastFrameTime = 0
frame = 0
frame_counter = 0
handSolution = mp.solutions.hands
hands = handSolution.Hands()
mpDraw = mp.solutions.drawing_utils

# Interprets what hand gesture user is performing
def interpretHandGest(landmarks):
    handGestures = [
        trackingDisengaged(landmarks), 
        railControlGest(landmarks), 
        armControlGest(landmarks), 
        closed_hand(landmarks), 
        open_hand(landmarks) ]
    
    for gesture in range(len(handGestures)):
        if handGestures[gesture] == True:
            return gesture+1 # add 1 to make it a 1-5 index range instead of 0-4 index range

    return 0 # Returns 0 if no listed gesture detected



# ** Individual hand gesture functions **

# Engages/Disengages control
def trackingDisengaged(landmarks):
    # Calculate distances between fingertips and knuckles
    dist_index_finger = math.hypot(
        landmarks[INDEX_FINGER_IDX].x - landmarks[INDEX_KNUCKLE_BIDX].x,
        landmarks[INDEX_FINGER_IDX].y - landmarks[INDEX_KNUCKLE_BIDX].y)
    dist_middle_finger = math.hypot(
        landmarks[MID_FINGER_IDX].x - landmarks[MID_KNUCKLE_BIDX].x,
        landmarks[MID_FINGER_IDX].y - landmarks[MID_KNUCKLE_BIDX].y)
    dist_ring_finger = math.hypot(
        landmarks[RING_FINGER_IDX].x - landmarks[RING_KNUCKLE_BIDX].x,
        landmarks[RING_FINGER_IDX].y - landmarks[RING_KNUCKLE_BIDX].y)
    dist_pinky_finger = math.hypot(
        landmarks[PINKY_FINGER_IDX].x - landmarks[PINKY_KNUCKLE_BIDX].x,
        landmarks[PINKY_FINGER_IDX].y - landmarks[PINKY_KNUCKLE_BIDX].y)

    # Define a threshold for "closed" state
    is_index_finger_closed = dist_index_finger < THRESHOLD
    is_middle_finger_closed = dist_middle_finger < THRESHOLD
    is_ring_finger_closed = dist_ring_finger < THRESHOLD
    is_pinky_finger_closed = dist_pinky_finger < THRESHOLD

    # Consider the thumb differently (it often moves along x-axis more prominently)
    is_thumb_open = (
        math.hypot(landmarks[THUMB_IDX].x - landmarks[INDEX_FINGER_IDX].x,
            landmarks[THUMB_IDX].y - landmarks[INDEX_FINGER_IDX].y) 
            > THRESHOLD)

    return ( is_index_finger_closed
        and is_middle_finger_closed
        and is_ring_finger_closed
        and is_pinky_finger_closed
        and is_thumb_open )

# Engages rail control
def railControlGest(landmarks):
    is_index_finger_open = (landmarks[INDEX_FINGER_IDX].y - landmarks[INDEX_KNUCKLE_BIDX].y) > THRESHOLD
    is_middle_finger_closed = (landmarks[MID_FINGER_IDX].y - landmarks[MID_KNUCKLE_BIDX].y) < THRESHOLD
    is_ring_finger_closed = (landmarks[RING_FINGER_IDX].y - landmarks[RING_KNUCKLE_BIDX].y) < THRESHOLD
    is_pinky_finger_closed = (landmarks[PINKY_FINGER_IDX].y - landmarks[PINKY_KNUCKLE_BIDX].y) < THRESHOLD

    is_thumb_closed = (
        math.hypot(landmarks[THUMB_IDX].x - landmarks[MID_KNUCKLE_BIDX].x,
            landmarks[THUMB_IDX].y - landmarks[MID_KNUCKLE_BIDX].y) 
            < THRESHOLD)
 
    return (is_index_finger_open and is_middle_finger_closed and is_ring_finger_closed and is_pinky_finger_closed and is_thumb_closed)

# Engages arm control
def armControlGest(landmarks):
    is_index_finger_open = (landmarks[INDEX_FINGER_IDX].y - landmarks[INDEX_KNUCKLE_BIDX].y) > THRESHOLD
    is_middle_finger_open = (landmarks[MID_FINGER_IDX].y - landmarks[MID_KNUCKLE_BIDX].y) > THRESHOLD
    is_ring_finger_open = (landmarks[RING_FINGER_IDX].y - landmarks[RING_KNUCKLE_BIDX].y) > THRESHOLD
    is_pinky_finger_closed = (landmarks[PINKY_FINGER_IDX].y - landmarks[PINKY_KNUCKLE_BIDX].y) < THRESHOLD

    is_thumb_closed = (
        math.hypot(landmarks[THUMB_IDX].x - landmarks[PINKY_FINGER_IDX].x,
            landmarks[THUMB_IDX].y - landmarks[PINKY_FINGER_IDX].y) 
            < THRESHOLD)
 
    return (is_index_finger_open and is_middle_finger_open and is_ring_finger_open and is_pinky_finger_closed and is_thumb_closed)

# Closes mechanical hand
def closed_hand(landmarks):
    is_index_finger_closed = (landmarks[INDEX_FINGER_IDX].y - landmarks[INDEX_KNUCKLE_BIDX].y) < THRESHOLD
    is_middle_finger_closed = (landmarks[MID_FINGER_IDX].y - landmarks[MID_KNUCKLE_BIDX].y) < THRESHOLD
    is_ring_finger_closed = (landmarks[RING_FINGER_IDX].y - landmarks[RING_KNUCKLE_BIDX].y) < THRESHOLD
    is_pinky_finger_closed = (landmarks[PINKY_FINGER_IDX].y - landmarks[PINKY_KNUCKLE_BIDX].y) < THRESHOLD

    is_thumb_closed = (
        math.hypot(landmarks[THUMB_IDX].x - landmarks[INDEX_FINGER_IDX].x,
            landmarks[THUMB_IDX].y - landmarks[INDEX_FINGER_IDX].y) 
            < THRESHOLD)

    return (is_index_finger_closed and is_middle_finger_closed and is_ring_finger_closed and is_pinky_finger_closed and is_thumb_closed)

# Opens mechanical hand
def open_hand(landmarks):
    is_index_finger_open = (landmarks[INDEX_FINGER_IDX].y - landmarks[INDEX_KNUCKLE_BIDX].y) > THRESHOLD
    is_middle_finger_open = (landmarks[MID_FINGER_IDX].y - landmarks[MID_KNUCKLE_BIDX].y) > THRESHOLD
    is_ring_finger_open = (landmarks[RING_FINGER_IDX].y - landmarks[RING_KNUCKLE_BIDX].y) > THRESHOLD
    is_pinky_finger_open = (landmarks[PINKY_FINGER_IDX].y - landmarks[PINKY_KNUCKLE_BIDX].y) > THRESHOLD

    is_thumb_open = (
        math.hypot(landmarks[THUMB_IDX].x - landmarks[INDEX_FINGER_IDX].x,
            landmarks[THUMB_IDX].y - landmarks[INDEX_FINGER_IDX].y) 
            > THRESHOLD)
 
    return (is_index_finger_open and is_middle_finger_open and is_ring_finger_open and is_pinky_finger_open and is_thumb_open)


# ** VIDEO CODE **
# ** VIDEO CODE **
# ** VIDEO CODE **

track = True
while True:

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

        # Increment frame counter
        frame_counter += 1

        # Hand tracking and gesture recognition
        if recHands1.multi_hand_landmarks:
            for hand in recHands1.multi_hand_landmarks:
                mpDraw.draw_landmarks(img1, hand, handSolution.HAND_CONNECTIONS)
                    # Check for hand gestures.py

                if frame_counter % GESTURE_UPDATE_INTERVAL == 0:

                    gesture = interpretHandGest(hand.landmark)

                    if gesture == 1: # Tracking Disengaged/Engaged
                        if track == False:
                            track = True
                            time.sleep(2) # Make system wait 3 seconds before re-engaging tracking
                            print("Tracking Disengaged")
                        else:
                            track = False
                            time.sleep(2) # Make system wait 3 seconds before dis-engaging tracking
                            print("Tracking Engaged")

                    elif gesture == 2: # Rail Control Mode
                        controlMode = 1
                        print("Rail Control Mode")

                    elif gesture == 3: # Arm Control Mode
                        controlMode = 2
                        print("Arm Control Mode")

                    elif gesture == 4: # Closed Hand
                        print("Closed Hand")
                        
                    elif gesture == 5: # Open Hand
                        print("Open Hand")

                    frame_counter = 0

        # Display the first camera feed
        cv2.imshow("Camera 1 Output", img1)

    # Break loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

videoCap1.release()

cv2.destroyAllWindows()
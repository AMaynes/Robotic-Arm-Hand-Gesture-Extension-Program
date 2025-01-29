import math

THUMB_IDX = 4
THUMB_BIDX = 1
INDEX_FINGER_IDX = 8
INDEX_KNUCKLE_BIDX = 5
MID_FINGER_IDX = 12
MID_KNUCKLE_BIDX = 9
RING_FINGER_IDX = 16
RING_KNUCKLE_BIDX = 13
PINKY_FINGER_IDX = 20
PINKY_KNUCKLE_BIDX = 17
GESTURE_UPDATE_INTERVAL = 30
THRESHOLD = 0.1

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
import math

THUMB_IDX = 4
THUMB_KNUCKLE_IDX = 3
THUMB_BIDX = 1
INDEX_FINGER_IDX = 8
INDEX_KNUCKLE_BIDX = 5
MID_FINGER_IDX = 12
MID_KNUCKLE_BIDX = 9
RING_FINGER_IDX = 16
RING_KNUCKLE_BIDX = 13
PINKY_FINGER_IDX = 20
PINKY_KNUCKLE_BIDX = 17
WRIST_IDX = 0
MID_KNUCKLE_IDX = 9
RING_KNUCKLE_IDX = 13
GESTURE_UPDATE_INTERVAL = 10
THRESHOLD = 0.1

# *** Hand Gestures & Interpretations ***
def interpretHandGest(landmarks):
    (first, middle, ring, pinky, thumb) = determineFingers(landmarks)

    handGestures = [
        HandGestures.trackingDisengaged(first, middle, ring, pinky, thumb),
        HandGestures.railControlGest(first, middle, ring, pinky, thumb),
        HandGestures.armControlGest(first, middle, ring, pinky, thumb),
        HandGestures.closed_hand(first, middle, ring, pinky, thumb),
        HandGestures.open_hand(first, middle, ring, pinky, thumb) ]

    printFingers(first, middle, ring, pinky, thumb)

    for gesture in range(len(handGestures)):
        if handGestures[gesture] == True:
            return gesture+1 # add 1 to make it a 1-5 index range instead of 0-4 index range

    return 0 # Returns 0 if no listed gesture detected

def printFingers(first, middle, ring, pinky, thumb):
    print("\n\n===========\nFingers open\n---------\n", "First: ", first, "\nMiddle: ",
          middle, "\nRing: ", ring, "\nPinky: ", pinky,
          "\nThumb: ", thumb)

def determineFingers(landmarks):
    is_index_finger_open = (abs(landmarks[INDEX_FINGER_IDX].y - landmarks[INDEX_KNUCKLE_BIDX].y)) > THRESHOLD
    is_middle_finger_open = (abs(landmarks[MID_FINGER_IDX].y - landmarks[MID_KNUCKLE_BIDX].y)) > THRESHOLD
    is_ring_finger_open = (abs(landmarks[RING_FINGER_IDX].y - landmarks[RING_KNUCKLE_BIDX].y)) > THRESHOLD

    is_pinky_finger_open = (abs(landmarks[PINKY_FINGER_IDX].y - landmarks[PINKY_KNUCKLE_BIDX].y)) > THRESHOLD+0.04

    is_thumb_open = (abs(
            math.hypot(landmarks[THUMB_KNUCKLE_IDX].x - landmarks[INDEX_KNUCKLE_BIDX].x,
                       landmarks[THUMB_KNUCKLE_IDX].y - landmarks[INDEX_KNUCKLE_BIDX].y))
            > THRESHOLD-0.02)

    return (is_index_finger_open, is_middle_finger_open, is_ring_finger_open, is_pinky_finger_open, is_thumb_open)

class HandGestures:
    # Engages/Disengages control
    def trackingDisengaged(first, middle, ring, pinky, thumb):
        return (not first and not middle and not ring and not pinky and thumb)

    # Engages rail control
    def railControlGest(first, middle, ring, pinky, thumb):
        return (first and not middle and not ring and not pinky and not thumb)

    # Engages arm control
    def armControlGest(first, middle, ring, pinky, thumb):
        return (first and middle and ring and not pinky and not thumb)

    # Closes mechanical hand
    def closed_hand(first, middle, ring, pinky, thumb):
        return (not first and not middle and not ring and not pinky and not thumb)

    # Opens mechanical hand
    def open_hand(first, middle, ring, pinky, thumb):
        return (first and middle and ring and pinky and thumb)

import math, time

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
WRIST_IDX = 0
MID_KNUCKLE_IDX = 9
RING_KNUCKLE_IDX = 13
GESTURE_UPDATE_INTERVAL = 10
THRESHOLD = 0.1


# *** Coordinate Processing ***
class CoordinateProcessing:
    # Determines z axis position (depth perception relative to the camera)
    def estimate_depth(landmarks):
        # Calculate distance between wrist and middle knuckle
        distance = math.sqrt(
            (landmarks[MID_KNUCKLE_IDX].x - landmarks[WRIST_IDX].x) ** 2 +
            (landmarks[MID_KNUCKLE_IDX].y - landmarks[WRIST_IDX].y) ** 2
        )

        # Normalize distance (Assume typical hand distance falls within [0.3, 0.5])
        min_distance = 0.3  # Adjust based on calibration
        max_distance = 0.5  # Adjust based on calibration

        # Clamp the distance to avoid out-of-range issues
        distance = max(min(distance, max_distance), min_distance)

        # Map to range [-180, 180]
        z_coordinate = (distance - min_distance) / (max_distance - min_distance) * 180 - 90
      #  print(f"Distance: {distance} ZCoord: {z_coordinate}")

        return z_coordinate

    def is_position_reachable(mode, x, y, z, l):
        if mode == 1 and l >= 0 and l <= 1000:  # Rail control mode
            return True

        if mode == 2:  # Arm control mode
            L1 = 135  # Length from Joint J1 to Joint J2
            L2 = 147  # Length from Joint J2 to Joint J3 (end-effector)

            # Planar Angle & Euclidean Distance Calculations (for base to end effector)
            h = math.hypot(x, y)  # Horizontal planar distance
            euclideanDistance = round(math.hypot(h, z), 2)
            horizontalAngle = round(math.degrees(math.atan2(y, x)), 2)
            VerticalAngle = round(math.degrees(math.atan2(z, h)), 2)

            # Dynamic euclidean distance limit calculations (Forms an arc like limit pathing)
            if VerticalAngle > 27.3:
                minimumEDistance = round(0.00002 * z ** 3 - 0.00778 * z ** 2 + 1.66028 * z + 110.66023, 2)
            elif VerticalAngle < 27.3 and z != 0:
                minimumEDistance = round(-0.0019 * z ** 2 - 1.1724 * z + 112.1743, 2)
            else:
                minimumEDistance = 111
            if VerticalAngle > -3.5:
                maximumEDistance = round(L1 + L2, 2)
            elif VerticalAngle < -3.5:
                maximumEDistance = round(-0.02395 * z ** 2 - 4.38796 * z + 124.43856, 2)
            else:
                maximumEDistance = 327

            minimumEDistance -= 10  # 10mm Safety barrier
            maximumEDistance -= 10  # 10mm Safety barrier

            # Planar Angle limits
            angle_limits = {
                'Hz_Angle': (-90, 90),
                'Vrt_Angle': (-30, 41.67),
            }

            within_limits = (
                    angle_limits['Hz_Angle'][0] <= horizontalAngle <= angle_limits['Hz_Angle'][1] and
                    angle_limits['Vrt_Angle'][0] <= VerticalAngle <= angle_limits['Vrt_Angle'][1] and
                    minimumEDistance <= euclideanDistance <= maximumEDistance
            )

            # print(f"{minimumEDistance} | {euclideanDistance} | {maximumEDistance}")
            # print(f"{angle_limits['Hz_Angle'][0]} | {horizontalAngle} | {angle_limits['Hz_Angle'][1]}")
            # print(f"{angle_limits['Vrt_Angle'][0]} | {VerticalAngle} | {angle_limits['Vrt_Angle'][1]}")

            if within_limits:
                return True
            else:
                return False


# *** Hand Gestures & Interpretations ***
def interpretHandGest(landmarks):
    (first, middle, ring, pinky, thumb) = determineFingers(landmarks)

    handGestures = [
        HandGestures.trackingDisengaged(first, middle, ring, pinky, thumb),
        HandGestures.railControlGest(first, middle, ring, pinky, thumb),
        HandGestures.armControlGest(first, middle, ring, pinky, thumb),
        HandGestures.closed_hand(first, middle, ring, pinky, thumb),
        HandGestures.open_hand(first, middle, ring, pinky, thumb)]

    # printFingers(first, middle, ring, pinky, thumb) # FOR DEBUGGING

    for gesture in range(len(handGestures)):
        if handGestures[gesture] == True:
            return gesture + 1  # add 1 to make it a 1-5 index range instead of 0-4 index range

    return 0  # Returns 0 if no listed gesture detected


def printFingers(first, middle, ring, pinky, thumb):
    print("\n\n===========\nFingers open\n---------\n", "First: ", first, "\nMiddle: ",
          middle, "\nRing: ", ring, "\nPinky: ", pinky,
          "\nThumb: ", thumb)


def determineFingers(landmarks):
    is_index_finger_open = (abs(landmarks[INDEX_FINGER_IDX].y - landmarks[INDEX_KNUCKLE_BIDX].y)) > THRESHOLD
    is_middle_finger_open = (abs(landmarks[MID_FINGER_IDX].y - landmarks[MID_KNUCKLE_BIDX].y)) > THRESHOLD
    is_ring_finger_open = (abs(landmarks[RING_FINGER_IDX].y - landmarks[RING_KNUCKLE_BIDX].y)) > THRESHOLD
    is_pinky_finger_open = (abs(landmarks[PINKY_FINGER_IDX].y - landmarks[PINKY_KNUCKLE_BIDX].y)) > THRESHOLD

    is_thumb_open = (abs(
        math.hypot(landmarks[THUMB_IDX].x - landmarks[INDEX_KNUCKLE_BIDX].x,
                   landmarks[THUMB_IDX].y - landmarks[INDEX_KNUCKLE_BIDX].y))
                     > THRESHOLD + 0.009)

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


# Determines hand physics for prediction tracking to make a more fluid tracking system
class HandPhysics:
    def __init__(self):
        self.previous_position = None
        self.previous_velocity = (0, 0, 0)
        self.previous_time = None

    def calculate_physics(self, current_position):
        current_time = time.time()

        if self.previous_position is None:
            self.previous_position = current_position
            self.previous_time = current_time
            return (0, 0, 0), (0, 0, 0)

        delta_time = current_time - self.previous_time

        velocity = tuple(
            (c - p) / delta_time for c, p in zip(current_position, self.previous_position)
        )

        acceleration = tuple(
            (v - pv) / delta_time for v, pv in zip(velocity, self.previous_velocity)
        )

        self.previous_position = current_position
        self.previous_velocity = velocity
        self.previous_time = current_time

        return velocity, acceleration

    def predict_next_position(self, current_position, time_interval):
        """
        Predict the next position based on velocity and acceleration.
        """
        velocity, acceleration = self.calculate_physics(current_position)

        # Predict next position
        next_position = tuple(
            c + v * time_interval + 0.5 * a * (time_interval ** 2)
            for c, v, a in zip(current_position, velocity, acceleration)
        )
        """
        swapped_position = (next_position[1], next_position[0], next_position[2])
        return swapped_position # MIGHT NEED TO DO THIS TO SWAP Y AND X - BUT ALSO THAT WOULD CAUSE ISSUES IN ABSTRACT DEVELOPMENT FOR OTHER BOTS
        """
        return next_position

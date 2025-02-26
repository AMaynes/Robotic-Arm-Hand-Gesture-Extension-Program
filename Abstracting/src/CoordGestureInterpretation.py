import math, time

# Landmark indices for hand tracking
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


class CoordinateProcessing:
    """Handles coordinate processing and position validation for robotic control."""

    @staticmethod
    def estimate_depth(landmarks):
        """
        Estimates the Z-axis position (depth) relative to the camera.

        Args:
            landmarks: List of hand landmarks from hand tracking

        Returns:
            float: Z-coordinate mapped to range [-180, 180]
        """
        # Calculate distance between wrist and middle knuckle
        distance = math.sqrt(
            (landmarks[MID_KNUCKLE_IDX].x - landmarks[WRIST_IDX].x) ** 2 +
            (landmarks[MID_KNUCKLE_IDX].y - landmarks[WRIST_IDX].y) ** 2
        )

        min_distance = 0.3  # Minimum calibrated hand distance
        max_distance = 0.5  # Maximum calibrated hand distance
        distance = max(min(distance, max_distance), min_distance)
        z_coordinate = (distance - min_distance) / (max_distance - min_distance) * 180 - 90
        # print(f"Distance: {distance} ZCoord: {z_coordinate}")
        return z_coordinate

    @staticmethod
    def is_position_reachable(mode, x, y, z, l):
        """
        Validates if a position is reachable by the robot.

        Args:
            mode (int): 1 for rail control, 2 for arm control
            x (float): X coordinate
            y (float): Y coordinate
            z (float): Z coordinate
            l (float): Length parameter for rail mode

        Returns:
            bool: True if position is reachable, False otherwise
        """
        if mode == 1 and l >= 0 and l <= 1000:  # Rail control mode
            return True

        if mode == 2:  # Arm control mode
            L1 = 135  # Length from Joint J1 to Joint J2
            L2 = 147  # Length from Joint J2 to Joint J3

            h = math.hypot(x, y)  # Horizontal planar distance
            euclideanDistance = round(math.hypot(h, z), 2)
            horizontalAngle = round(math.degrees(math.atan2(y, x)), 2)
            VerticalAngle = round(math.degrees(math.atan2(z, h)), 2)

            # Calculate dynamic reach limits based on vertical angle
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

            minimumEDistance -= 10  # Safety barrier
            maximumEDistance -= 10  # Safety barrier

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

            return within_limits


def interpretHandGest(landmarks):
    """
    Interprets hand gestures from landmarks.

    Args:
        landmarks: List of hand landmarks from hand tracking

    Returns:
        int: Gesture ID (0-5), where 0 means no recognized gesture
    """
    handGestures = [
        HandGestures.trackingDisengaged(landmarks),
        HandGestures.railControlGest(landmarks),
        HandGestures.armControlGest(landmarks),
        HandGestures.closed_hand(landmarks),
        HandGestures.open_hand(landmarks)
    ]

    for gesture in range(len(handGestures)):
        if handGestures[gesture]:
            return gesture + 1
    return 0


class HandGestures:
    """Contains methods for recognizing different hand gestures."""

    @staticmethod
    def trackingDisengaged(landmarks):
        """Recognizes the gesture for disengaging tracking (thumb out, other fingers closed)."""
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

        is_index_finger_closed = dist_index_finger < THRESHOLD
        is_middle_finger_closed = dist_middle_finger < THRESHOLD
        is_ring_finger_closed = dist_ring_finger < THRESHOLD
        is_pinky_finger_closed = dist_pinky_finger < THRESHOLD
        is_thumb_open = (
                math.hypot(landmarks[THUMB_IDX].x - landmarks[INDEX_FINGER_IDX].x,
                           landmarks[THUMB_IDX].y - landmarks[INDEX_FINGER_IDX].y)
                > THRESHOLD)

        return (is_index_finger_closed and is_middle_finger_closed and
                is_ring_finger_closed and is_pinky_finger_closed and is_thumb_open)

    @staticmethod
    def railControlGest(landmarks):
        """Recognizes the gesture for rail control (index finger up, others closed)."""
        is_index_finger_open = (landmarks[INDEX_FINGER_IDX].y - landmarks[INDEX_KNUCKLE_BIDX].y) > THRESHOLD
        is_middle_finger_closed = (landmarks[MID_FINGER_IDX].y - landmarks[MID_KNUCKLE_BIDX].y) < THRESHOLD
        is_ring_finger_closed = (landmarks[RING_FINGER_IDX].y - landmarks[RING_KNUCKLE_BIDX].y) < THRESHOLD
        is_pinky_finger_closed = (landmarks[PINKY_FINGER_IDX].y - landmarks[PINKY_KNUCKLE_BIDX].y) < THRESHOLD
        is_thumb_closed = (
                math.hypot(landmarks[THUMB_IDX].x - landmarks[MID_KNUCKLE_BIDX].x,
                           landmarks[THUMB_IDX].y - landmarks[MID_KNUCKLE_BIDX].y)
                < THRESHOLD)

        return (is_index_finger_open and is_middle_finger_closed and
                is_ring_finger_closed and is_pinky_finger_closed and is_thumb_closed)

    @staticmethod
    def armControlGest(landmarks):
        """Recognizes the gesture for arm control (three fingers up, pinky and thumb closed)."""
        is_index_finger_open = (landmarks[INDEX_FINGER_IDX].y - landmarks[INDEX_KNUCKLE_BIDX].y) > THRESHOLD
        is_middle_finger_open = (landmarks[MID_FINGER_IDX].y - landmarks[MID_KNUCKLE_BIDX].y) > THRESHOLD
        is_ring_finger_open = (landmarks[RING_FINGER_IDX].y - landmarks[RING_KNUCKLE_BIDX].y) > THRESHOLD
        is_pinky_finger_closed = (landmarks[PINKY_FINGER_IDX].y - landmarks[PINKY_KNUCKLE_BIDX].y) < THRESHOLD
        is_thumb_closed = (
                math.hypot(landmarks[THUMB_IDX].x - landmarks[PINKY_FINGER_IDX].x,
                           landmarks[THUMB_IDX].y - landmarks[PINKY_FINGER_IDX].y)
                < THRESHOLD)
        #we are going to 3d
        print(is_index_finger_open and is_middle_finger_open and
                is_ring_finger_open and is_pinky_finger_closed and is_thumb_closed)

        return (is_index_finger_open and is_middle_finger_open and
                is_ring_finger_open and is_pinky_finger_closed and is_thumb_closed)

    @staticmethod
    def closed_hand(landmarks):
        """Recognizes closed hand gesture (all fingers closed)."""
        is_index_finger_closed = (landmarks[INDEX_FINGER_IDX].y - landmarks[INDEX_KNUCKLE_BIDX].y) < THRESHOLD
        is_middle_finger_closed = (landmarks[MID_FINGER_IDX].y - landmarks[MID_KNUCKLE_BIDX].y) < THRESHOLD
        is_ring_finger_closed = (landmarks[RING_FINGER_IDX].y - landmarks[RING_KNUCKLE_BIDX].y) < THRESHOLD
        is_pinky_finger_closed = (landmarks[PINKY_FINGER_IDX].y - landmarks[PINKY_KNUCKLE_BIDX].y) < THRESHOLD
        is_thumb_closed = (
                math.hypot(landmarks[THUMB_IDX].x - landmarks[INDEX_FINGER_IDX].x,
                           landmarks[THUMB_IDX].y - landmarks[INDEX_FINGER_IDX].y)
                < THRESHOLD)

        return (is_index_finger_closed and is_middle_finger_closed and
                is_ring_finger_closed and is_pinky_finger_closed and is_thumb_closed)

    @staticmethod
    def open_hand(landmarks):
        """Recognizes open hand gesture (all fingers open)."""
        is_index_finger_open = (landmarks[INDEX_FINGER_IDX].y - landmarks[INDEX_KNUCKLE_BIDX].y) > THRESHOLD
        is_middle_finger_open = (landmarks[MID_FINGER_IDX].y - landmarks[MID_KNUCKLE_BIDX].y) > THRESHOLD
        is_ring_finger_open = (landmarks[RING_FINGER_IDX].y - landmarks[RING_KNUCKLE_BIDX].y) > THRESHOLD
        is_pinky_finger_open = (landmarks[PINKY_FINGER_IDX].y - landmarks[PINKY_KNUCKLE_BIDX].y) > THRESHOLD
        is_thumb_open = (
                math.hypot(landmarks[THUMB_IDX].x - landmarks[INDEX_FINGER_IDX].x,
                           landmarks[THUMB_IDX].y - landmarks[INDEX_FINGER_IDX].y)
                > THRESHOLD)

        return (is_index_finger_open and is_middle_finger_open and
                is_ring_finger_open and is_pinky_finger_open and is_thumb_open)


class HandPhysics:
    """Handles hand motion physics calculations for smooth tracking."""

    def __init__(self):
        """Initialize physics tracking variables."""
        self.previous_position = None
        self.previous_velocity = (0, 0, 0)
        self.previous_time = None

    def calculate_physics(self, current_position):
        """
        Calculate velocity and acceleration based on current position.

        Args:
            current_position: Tuple of (x, y, z) coordinates

        Returns:
            tuple: (velocity, acceleration) as 3D vectors
        """
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
        Predict the next position based on physics calculations.

        Args:
            current_position: Tuple of (x, y, z) coordinates
            time_interval: Time step for prediction

        Returns:
            tuple: Predicted (x, y, z) position
        """
        velocity, acceleration = self.calculate_physics(current_position)

        next_position = tuple(
            c + v * time_interval + 0.5 * a * (time_interval ** 2)
            for c, v, a in zip(current_position, velocity, acceleration)
        )
        return next_position
import math, time

WRIST_IDX = 0
MID_KNUCKLE_IDX = 9

# Various coordinate processing functions
class CoordinateProcessing:

    # Determines z axis position (depth perception relative to the camera)
    def determineZCoord(landmarks):
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

        return z_coordinate

    def isPositionValid(mode, x, y, z, l):
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

            if within_limits:
                return True
            else:
                return False

# Determines hand physics for prediction tracking to make a more fluid tracking system
class HandPhysics:
    def __init__(self):
        self.previous_position = None
        self.previous_velocity = (0, 0, 0)
        self.previous_time = None

    # Calculate velocity & acceleration of the hand on camera
    def calculatePhysics(self, current_position):
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

    # Predict next hand coordinates based on calculated velocity & acceleration
    def predictNextPosition(self, current_position, time_interval):
        """
        Predict the next position based on velocity and acceleration.
        """
        velocity, acceleration = self.calculatePhysics(current_position)

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
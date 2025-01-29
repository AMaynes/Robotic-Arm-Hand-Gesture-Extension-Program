import math
import DobotDllType as dType

def is_position_reachable(mode, x, y, z):
    if mode == 1: # Rail control mdoe
        return True
    
    if mode == 2: # Arm control mode
        # Arm Specifications (in mm)
        L1 = 135  # Length from Joint J1 to Joint J2
        L2 = 147  # Length from Joint J2 to Joint J3 (end-effector)

        # Joint Limits (in degrees)
        joint_limits = {
            'J1': (-90, 90),  # Joint J1 limits
            'J2': (5, 80),      # Joint J2 limits
            'J3': (-5, 75)     # Joint J3 limits
        }

    # Calculate planar distance r & total distance D from Joint J1 to target point
        r = math.hypot(x, y)
        euclidOffset = 1.5712 * z + 58.3408
        D = math.hypot(r, z) - euclidOffset

        # Check if target is within reach by distance
        if D > (L1 + L2) or D < abs(L1 - L2):
            print("ERROR: Position out of reach")
            return False

        # Calculate theta1 (Joint J1 angle)
        theta1 = math.atan2(y, x)
        theta1 = math.degrees(theta1)
        theta1 = round(theta1, 2)

        # Calculate theta2 (Joint J2 angle) using law of cosines
        try:
            phi = (L1**2 + D**2 - L2**2) / (2 * L1 * D)
            theta2 = math.degrees(math.acos(phi))
            theta2 = 90 - theta2 # 90 deg is marked as 0 deg in the dobot so an offset is req
            theta2 = round(theta2, 2)
        except ValueError:
            print("ERROR: Theta2 calculation out of range by cosine domain exceedence")
            return False

        # Calculate theta3 (Joint J3 angle) using law of sines and prev calculations for J2 ---> 180 - ('Left of elbow' angle + elbow angle) = 'right of elbow' angle
        try:
            theta3 = 180 - (math.degrees(math.asin( (D * math.sin( math.acos(phi) )) / L2)) + 90 - theta2)
            J3Offset = 0.7270 * z - 1.3
            theta3 = theta3 - J3Offset
            theta3 = round(theta3, 2)
        except ValueError:
            print("ERROR: Theta3 calculation out of range by sine domain exceedence")
            return False


        # Check if all joint angles are within mechanical limits
        within_limits = (
            joint_limits['J1'][0] <= theta1 <= joint_limits['J1'][1] and
            joint_limits['J2'][0] <= theta2 <= joint_limits['J2'][1] and
            joint_limits['J3'][0] <= theta3 <= joint_limits['J3'][1]
        )

        # Output joint angle results & if pos is reachable
        if within_limits:
            return True
        else:
            return False
    
def moveRail(api, x, y, z, l):
    dType.SetQueuedCmdClear(api)
    dType.SetPTPWithLCmd(api, 2, x, y, z, 0, l, isQueued=0)  # Move rail immediately to the position

def moveDobot(api, x, y, z):
    dType.SetQueuedCmdClear(api)
    dType.SetPTPCmd(api, 2, x, y, z, 0, isQueued=0)  # Move Dobot immediately to the position
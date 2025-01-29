import math
from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink

urdf_file_path = "C:/Users/alexm/Documents/School/Projects/Python Code/Dobot Research/Abstracting/RoboticArms/URDFs/Dobot.urdf"
robot_arm = Chain.from_urdf_file(
    urdf_file_path, 
    active_links_mask=[False, True, True, True]  # Ensure only rotating links are active
)


def is_position_reachable(x, y, z):
    # Convert mm to meters
    x, y, z = x / 1000.0, y / 1000.0, z / 1000.0

    # Define target position
    target_position = [x, y, z, 0, 0, 0]  # No rotation (roll, pitch, yaw)

    try:
        # Calculate inverse kinematics
        joint_angles = robot_arm.inverse_kinematics(target_position)

        # Convert to degrees for readability
        theta1 = round(math.degrees(joint_angles[1]), 2)
        theta2 = round(math.degrees(joint_angles[2]), 2)
        theta3 = round(math.degrees(joint_angles[3]), 2)

        # Joint limits
        joint_limits = {
            'J1': (-90, 90),
            'J2': (-5, 80),
            'J3': (-5, 80)
        }

        within_limits = (
            joint_limits['J1'][0] <= theta1 <= joint_limits['J1'][1] and
            joint_limits['J2'][0] <= theta2 <= joint_limits['J2'][1] and
            joint_limits['J3'][0] <= theta3 <= joint_limits['J3'][1]
        )

        if within_limits:
            return theta1, theta2, theta3
        else:
            print(f"Joint angles out of bounds: {theta1}, {theta2}, {theta3}")
            return None

    except Exception as e:
        print(f"Error in IK calculation: {e}")
        return None

def calculateCorrectEuclidean(theta2, theta3):
    L1 = 135  # Length from Joint J1 to Joint J2
    L2 = 147  # Length from Joint J2 to Joint J3 (end-effector)
    theta2 = math.radians(theta2)
    theta3 = math.radians(theta3)
    L1_e = L1*math.sin(theta2)
    L2_e = L2*math.cos(theta3)

    e = L1_e + L2_e

    return e

# Prints the test results in a table (for more tests enter them in and update the size of the arrays)
def printTable():
    testCoords = [
        " ",                     # Placeholder for the first index
        (100, -100, 0),          # T1
        (50, -100, 0),           # T2
        (200, -100, 0),          # T3
        (160, -100, 0),          # T4
        (150, 120, 0),           # T5
        (150, 120, -20),         # T6
        (120, 110, 0),           # T7
        (120, 110, -20),         # T8
        (170, -130, 0),          # T9
        (170, -130, -20),        # T10
        (170, -130, 20),         # T11
        (120, 110, 20),          # T12
        (150, 120, 20),          # T13
        (150, 120, -30),         # T14
        # Incremental Z Tests
        (150, 120, -40),         # T15
        (150, 120, -60),         # T16
        (150, 120, -80),         # T17
        (150, 120, -100),        # T18
        (150, 120, -120),        # T19
        (150, 120, 40),          # T20
        (150, 120, 60),          # T21
        (150, 120, 80),          # T22
        (150, 120, 100),         # T23
        # Incremental Z Tests for another (x, y) pair
        (120, 110, -40),         # T24
        (120, 110, 40),          # T25
        (170, -130, -130),       # T26
        (170, -130, 130),        # T27
        (200, 0, -130),          # T28
        (200, 0, 130)            # T29
    ]

    results = [None] * len(testCoords)
    results[0] = "Prediction Test Results"

    # Test cases
    for i in range(1, len(testCoords)):
        results[i] = is_position_reachable(*testCoords[i])

    # Angle Values measured in Dobot Studio relating to the corresponding xyz coordinates
    idealResults = [
        "Ideal Test Results",
        (-45.00, 8.58, 65.24),   # (x=100, y=-100, z=0)    # T1
        (-63.44, -2.73, 66.54),  # (x=50, y=-100, z=0)     # T2
        (-26.57, 32.05, 51.12),  # (x=200, y=-100, z=0)    # T3
        (-32.00, 22.37, 58.13),  # (x=160, y=-100, z=0)    # T4
        (38.66, 23.31, 57.50),   # (x=150, y=120, z=0)     # T5
        (38.66, 32.31, 65.81),   # (x=150, y=120, z=-20)   # T6
        (42.51, 15.08, 62.46),   # (x=120, y=110, z=0)     # T7
        (42.51, 26.62, 73.15),   # (x=120, y=110, z=-20)   # T8
        (-37.41, 29.36, 53.17),  # (x=170, y=-130, z=0)    # T9
        (-37.41, 37.10, 60.28),  # (x=170, y=-130, z=-20)  # T10
        (-37.41, 22.33, 45.51),  # (x=170, y=-130, z=20)   # T11
        (42.51, 4.66, 51.19),    # (x=120, y=110, z=20)    # T12
        (38.66, 15.13, 48.63),   # (x=150, y=120, z=20)    # T13
        (38.66, 37.00, 69.64),   # (x=150, y=120, z=-30)   # T14
        (38.66, 41.75, 73.19), # (x=150, y=120, z=-40)   # T15
        (38.66, 51.26, 79.38), # (x=150, y=120, z=-60)   # T16
        (38.66, 60.61, 84.23), # (x=150, y=120, z=-80)   # T17
        (38.66, 69.68, 87.74), # (x=150, y=120, z=-100)  # T18
        (38.66, 78.46, 89.95), # (x=150, y=120, z=-120)  # T19
        (38.66, 8.13, 39.57), # (x=150, y=120, z=40)    # T20
        (38.66, 2.50, 30.62), # (x=150, y=120, z=60)    # T21
        (38.66, -1.68, 21.95), # (x=150, y=120, z=80)    # T22
        (38.66, -4.45, 13.61), # (x=150, y=120, z=100)   # T23
        (42.51, 38.44, 82.51), # (x=120, y=110, z=-40)   # T24
        (42.51, -3.97, 40.09), # (x=120, y=110, z=40)    # T25
        (-37.41, 83.36, 82.10), # (x=170, y=-130, z=-130) # T26
        (-37.41, 3.14, 1.87), # (x=170, y=-130, z=130)  # T27
        (0, 82.82, 87.52), # (x=200, y=0, z=-130)    # T28
        (0, -2.81, 1.89)  # (x=200, y=0, z=130)     # T29
    ]

    tableJ1 = [None] * len(testCoords)
    tableJ2 = [None] * len(testCoords)
    tableJ3 = [None] * len(testCoords)
    avgDiff = [0, 0, 0]

    print("\n=================\nTest Summary:\n---------\n")
    print(f"{'Test':<10} {'J1 (Calculated, Ideal, Difference)':<40} {'J2 (Calculated, Ideal, Difference)':<40} {'J3 (Calculated, Ideal, Difference)'}")
    for i in range(1, len(testCoords)):
        try:
            difference = abs(results[i][0]-idealResults[i][0])
            difference = round(difference, 2)
            tableJ1[i] = f"({results[i][0]},  {idealResults[i][0]},    {difference})"
            avgDiff[0] += difference

            difference = abs(results[i][1]-idealResults[i][1])
            difference = round(difference, 2)
            tableJ2[i] = f"({results[i][1]},  {idealResults[i][1]},    {difference})"
            avgDiff[1] += difference

            difference = abs(results[i][2]-idealResults[i][2])
            difference = round(difference, 2)
            tableJ3[i] = f"({results[i][2]},  {idealResults[i][2]},    {difference})"
            avgDiff[2] += difference

            print(f"T{i:<10} {tableJ1[i]:<40} {tableJ2[i]:<40} {tableJ3[i]}")
        except TypeError:
            print(f"T{i:<10} ERROR - Position out of reach")

    avgDiff[0] /= len(testCoords) - 1
    avgDiff[1] /= len(testCoords) - 1
    avgDiff[2] /= len(testCoords) - 1
    print(f"\nAverage Joint Calculation Differences \nJ1: {avgDiff[0]:.2f}  \nJ2: {avgDiff[1]:.2f}  \nJ3: {avgDiff[2]:.2f}\n")

    print("\nEuclidean Info (Calculated, Ideal, Difference)")
    for i in range(1, len(testCoords)):
        if i == 0:
            continue
        else:
            e1 = round(math.sqrt(testCoords[i][0]**2 + testCoords[i][1]**2 + testCoords[i][2]**2), 4)
            e2 = round(calculateCorrectEuclidean(float(idealResults[i][1]), float(idealResults[i][2])), 4)
            difference = abs(e1-e2)
            difference = round(difference, 2)
            print(f"T{i:<5} ({e1},   {e2},     {difference})")


printTable()
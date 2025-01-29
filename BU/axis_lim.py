import math

def is_position_reachable(x, y, z):
    # Arm Specifications (in mm)
    LB = 158 # Length of square base
    L0 = 138  # Base height from ground to Joint J1
    L1 = 135  # Length from Joint J1 to Joint J2
    L2 = 147  # Length from Joint J2 to Joint J3 (end-effector)

    # Joint Limits (in degrees)
    joint_limits = {
        'J1': (-90, 90),  # Joint J1 limits
        'J2': (0, 85),      # Joint J2 limits
        'J3': (-10, 90)     # Joint J3 limits
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
        return theta1, theta2, theta3
    else:
        return theta1, theta2, theta3

def reverseJ2CalculateEuclidean(theta2):
    # Adjust theta2 to match the original phi (add 90 degrees)
    phi = 90 - theta2
    phi_rad = math.radians(phi)

    # Solve for D using the quadratic formula
    e = ( ( 270*math.cos(phi_rad) ) + ( math.sqrt( ((270*math.cos(phi_rad))**2) - (4*(-3384))) ) ) / 2
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
        (150, 120, -10),         # T15
        (150, 120, 5),           # T16
        (150, 120, 25),          # T17
        (150, 120, 40),          # T18
        (120, 110, -30),         # T19
        (120, 110, -5),          # T20
        (120, 110, 10),          # T21
        (120, 110, 30),          # T22
        (120, 110, 40)]          # T23

    results = [None] * 24
    results[0] = "Prediction Test Results"

    # Test cases
    results[1] = is_position_reachable(100, -100, 0)
    results[2] = is_position_reachable(50, -100, 0)
    results[3] = is_position_reachable(200, -100, 0)
    results[4] = is_position_reachable(160, -100, 0)
    results[5] = is_position_reachable(150, 120, 0)
    results[6] = is_position_reachable(150, 120, -20)
    results[7] = is_position_reachable(120, 110, 0)
    results[8] = is_position_reachable(120, 110, -20)
    results[9] = is_position_reachable(170, -130, 0)
    results[10] = is_position_reachable(170, -130, -20)
    results[11] = is_position_reachable(170, -130, 20)
    results[12] = is_position_reachable(120, 110, 20)
    results[13] = is_position_reachable(150, 120, 20)
    results[14] = is_position_reachable(150, 120, -30)  
    results[15] = is_position_reachable(150, 120, -10)  
    results[16] = is_position_reachable(150, 120, 5)   
    results[17] = is_position_reachable(150, 120, 25)   
    results[18] = is_position_reachable(150, 120, 40)   
    results[19] = is_position_reachable(120, 110, -30)  
    results[20] = is_position_reachable(120, 110, -5)   
    results[21] = is_position_reachable(120, 110, 10)   
    results[22] = is_position_reachable(120, 110, 30)   
    results[23] = is_position_reachable(120, 110, 40)   

    # Angle Values measured in Dobot Studio relating to the cooresponding xyz coordinates
    idealResults = ["Ideal Test Results",
        (-45.00, 8.58, 65.24),   # T1: 100, -100, 0
        (-63.44, -2.73, 66.54),  # T2: 50, -100, 0
        (-26.57, 32.05, 51.12),  # T3: 200, -100, 0
        (-32.00, 22.37, 58.13),  # T4: 160, -100, 0
        (38.66, 23.31, 57.50),   # T5: 150, 120, 0
        (38.66, 32.31, 65.81),   # T6: 150, 120, -20
        (42.51, 15.08, 62.46),   # T7: 120, 110, 0
        (42.51, 26.62, 73.15),   # T8: 120, 110, -20
        (-37.41, 29.36, 53.17),  # T9: 170, -130, 0
        (-37.41, 37.10, 60.28),  # T10: 170, -130, -20
        (-37.41, 22.33, 45.51),  # T11: 170, -130, 20
        (42.51, 4.66, 51.19),    # T12: 120, 110, 20
        (38.66, 15.13, 48.63),   # T13: 150, 120, 20
        (38.66, 37.00, 69.64),   # T14: 150, 120, -30
        (38.66, 27.73, 61.75),   # T15: 150, 120, -10
        (38.66, 21.17, 55.32),   # T16: 150, 120, 5
        (38.66, 13.26, 46.37),   # T17: 150, 120, 25
        (38.66, 8.13, 39.57),    # T18: 150, 120, 40
        (42.51, 32.54, 78.04),   # T19: 120, 110, -30
        (42.51, 17.90, 65.22),   # T20: 120, 110, -5
        (42.51, 9.68, 56.85),    # T21: 120, 110, 10
        (42.51, 0.09, 45.58),    # T22: 120, 110, 30
        (42.51, -3.98, 40.09)]   # T23: 120, 110, 40

    tableJ1 = [None] * 24
    tableJ2 = [None] * 24
    tableJ3 = [None] * 24
    avgDiff = [0, 0, 0]

    print("\n=================\nTest Summary:\n---------\n")
    print(f"{'Test':<10} {'J1 (Calculated, Ideal, Difference)':<40} {'J2 (Calculated, Ideal, Difference)':<40} {'J3 (Calculated, Ideal, Difference)'}")
    for i in range(24):
        if i == 0:
            continue
        else:
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

            print(f"{str(i)+':':<10} {str(tableJ1[i]):<40} {str(tableJ2[i]):<40} {str(tableJ3[i])}")

    avgDiff[0] /= 13
    avgDiff[0] = round(avgDiff[0], 2)
    avgDiff[1] /= 13
    avgDiff[1] = round(avgDiff[1], 2)
    avgDiff[2] /= 13
    avgDiff[2] = round(avgDiff[2], 2)
    print(f"\nAverage Joint Calculation Differences \nJ1: {avgDiff[0]}  \nJ2: {avgDiff[1]}  \nJ3: {avgDiff[2]}\n")

    print("\nEuclidean Info (Calculated, Ideal, Difference)")
    for i in range(24):
        if i == 0:
            continue
        else:
            e1 = round(math.sqrt(testCoords[i][0]**2 + testCoords[i][1]**2 + testCoords[i][2]**2), 4)
            e2 = round(reverseJ2CalculateEuclidean(float(idealResults[i][1])), 4)
            difference = abs(e1-e2)
            difference = round(difference, 2)
            print(f"T{i:<5} ({e1},   {e2},     {difference})")

printTable()
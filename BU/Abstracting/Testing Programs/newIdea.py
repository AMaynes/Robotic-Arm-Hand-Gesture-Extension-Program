import math


def is_position_reachable(x, y, z):
    L1 = 135  # Length from Joint J1 to Joint J2
    L2 = 147  # Length from Joint J2 to Joint J3 (end-effector)

    # Planar Angle & Euclidean Distance Calculations (for base to end effector)
    h = math.hypot(x, y) # Horizontal planar distance
    euclideanDistance =  round(math.hypot(h, z), 2)
    horizontalAngle = round(math.degrees(math.atan2(y, x)), 2)
    VerticalAngle = round(math.degrees(math.atan2(z, h)), 2)

    # Dynamic euclidean distance limit calculations (Forms an arc like limit pathing)
    if VerticalAngle > 27.3: minimumEDistance = round(0.00002*z**3-0.00778*z**2+1.66028*z+110.66023, 2)
    elif VerticalAngle < 27.3 and z != 0: minimumEDistance = round(-0.0019*z**2-1.1724*z+112.1743, 2)
    else: minimumEDistance = 111
    if VerticalAngle > -3.5: maximumEDistance = round(L1 + L2, 2)
    elif VerticalAngle < -3.5: maximumEDistance = round(-0.02395*z**2-4.38796*z+124.43856, 2)
    else: maximumEDistance = 327

    minimumEDistance-=10 # 5mm Safety barrier
    maximumEDistance-=10 # 5mm Safety barrier

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

    print(f"{minimumEDistance} | {euclideanDistance} | {maximumEDistance}")
    print(f"{angle_limits['Hz_Angle'][0]} | {horizontalAngle} | {angle_limits['Hz_Angle'][1]}")
    print(f"{angle_limits['Vrt_Angle'][0]} | {VerticalAngle} | {angle_limits['Vrt_Angle'][1]}")

    if within_limits:
        return "Reachable"
    else:
        return "****Not Reachable****"

# Prints the test results in a table (for more tests enter them in and update the size of the arrays)
def printTable():
    testCoords = [
        " ",                     # Placeholder for the first index
        (180, 0, 155),          # T1
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
        (180, 120, 170),         # T23
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
        print(f"Test {i}: {results[i]}\n({testCoords[i]})\n")

printTable()
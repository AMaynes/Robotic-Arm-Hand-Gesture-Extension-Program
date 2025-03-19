import math
from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink

# Load the URDF file
urdf_file_path = r"C:/Users/alexm/Documents/School/Projects/Python Code/Dobot Research/Abstracting/RoboticArms/URDFs/Dobot.urdf"
robot_arm = Chain.from_urdf_file(
    urdf_file_path, 
    active_links_mask=[False, True, True, True, False]  # Ensure only rotating links are active (first and last are base height and endeffector urdf formating joints)
)

heightOffSetInMeters = 138 # Height of joint 2 from the ground

def test_forward_kinematics(joint_angles):
    fk = robot_arm.forward_kinematics(joint_angles)
    mmCoords = [float(round(coord * 1000, 2)) for coord in fk[:3, 3]]
    mmCoords[2] = round(mmCoords[2] - heightOffSetInMeters, 2) # Adjustment to mm for print

    print(f"Joints Input: {[round(math.degrees(angle), 2) for angle in joint_angles[1:-1]]}\n\tEnd-effector Position: {mmCoords}") # Print data

    return mmCoords

def test_inverse_kinematics(x, y, z):
    target_position = [x, y, z]
    try:
        joint_angles = robot_arm.inverse_kinematics(target_position)

        # Print data
        print(f"\nXYZ Input: {[x*1000, y*1000, round((z*1000)-heightOffSetInMeters, 1)]}\n\tInverse Kinematics Joint Angles (degrees): {[round(math.degrees(angle), 2) for angle in joint_angles[1:-1]]}") # skips 1st index due to the fixed initial height joint
        
        # Run a FK test using the IK calculated joint angles
        fkCoords = test_forward_kinematics(joint_angles) # Compare with FK to ensure an the IK calculations are valid
        target_position = [x*1000, y*1000, (z*1000)-heightOffSetInMeters] # Adjustment to mm for print

        # Check validity of Calculations by comparing IK and FK calculations and identify anomalies
        for i in range(len(fkCoords)):

            rounding = abs(fkCoords[i] - target_position[i])

            if rounding > 0.5:
                print("\t*INVALID OR UNREACHABLE*") # Error in comparison detected if there is an accuracy difference between FK and IK of more than 0.5 degrees
                print("===================")
                return
            
    except Exception as e:
        print(f"Error in IK calculation: {e}\n")

    print("===================")



# Inital FK values 0 test (Max height of dobot 420mm)
print("Initial test using 0 angles for all joints:")
joints = 0, math.radians(0), math.radians(0), math.radians(0), 0
test_forward_kinematics(joints)
print("===================")

testCoords = [
        (100, -100, 0),          # T1 --- -45.00, 8.58, 65.24 joint angles
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

# Run all test coordinates
for i, each in enumerate(testCoords):
    x, y, z = each

    # Account for the base height from ground to joint 2
    z += heightOffSetInMeters

    # Conversion to meters for URDF testing
    x /= 1000
    z /= 1000
    y /= 1000
    test_inverse_kinematics(x, y, z)

#-45.00, 8.58, 65.24 joint angles for 1st test of 100 -100 0


# Current thoughts for when I inevitably forget:

# My leading thought on what the issue is - is that it is not a range of motion value problem.
# The issue is likely a reference angle issue.
# Need to figure out EXACTLY what the dobot considers 0 as and to ensure that it is not a dynamic value.
# By dynamic value I mean that it is not refering to a reference angle of 0 that exists in reality independent of the dobot.
# What I need is the reference angle that is always with respect to link 1's ending.
# It is unlikely that this is the case as it would be ridiculous to make but not impossible.

# TODO:
# Find joint 2's reference angle
# Find joint 3's reference angle
# Correct the URDF accordingly

# NOTES:
# If J3 does not have a dynamic reference angle independent of the dobot - you're an idiot and a biased liar to yourself
# It means you manipulated the data to see what you wanted to see because it was easier to make sense of - and you couldn't see it
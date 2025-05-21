# Robotic-Arm-Hand-Gesture-Extension-Program  

This program is designed to interface with the dobot magician robotic arm and allow for control of it using hand gestures via machine learning and computer vision APIs.
This is achieved through utilizing Google's open sourced Mediapipe and OpenCV. The idea is that
this program can be used to teach college students about emerging AI & robotics technologies using Open Source APIs and solve real world solutions.

## Requirements & Dependencies
- Dobot Magician
- Standard Camera for hand detecting
- Mediapipe
- OpenCV (cv2)
- DobotDllType.py (Main import for robotic arm commands)
- Dobot DLL Files (DobotDllType.py dependency)

### Directory Breakdown

- Docs -> A location for the main research publication and any supporting documentations/publications or other informative files
- Resources -> A location for UI icons and other images used in the scripts
- src -> A location for all the program scripts

  
## Known Bugs/Issues

- Infinite loop when selecting 2nd camera
- Tracking camera must see hand in order to work
- COM3 Port is hardcoded, thus any other computers that require other COM Ports instead cannot connect to the Dobot
- Program loading may take a while to appear for low end GPUs computers without GPUs

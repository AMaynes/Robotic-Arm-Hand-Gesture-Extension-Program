# Dobot Hand Gesture Software
This program is designed to interface with the dobot magician and allow for control of it using hand gestures.
This is achieved through utilizing Google's open sourced Mediapipe and OpenCV. The idea is that
this program can be used to teach ME-150 students about emerging AI & robotics technologies.

## Requirements & Dependencies
- Dobot Magician
- Standard Camera for hand detecting
- Mediapipe
- OpenCV (cv2)
- DobotDllType.py (Main import for robotic arm commands)
- Dobot DLL Files (DobotDllType.py dependency)

## General Design Diagram 
UserInterface ->  *Calls "Tracker" Methods*  

Tracker -> (prev. named TrackingInterfacing) *Main logic/program flow*

- RobotArmCommands -> (prev. named RobotArmInterfacing) *Provides access to a generalized set of robot commands*  
  

- gestureInterpretation -> *Provides gesture interpretation logic*  
  

- coordProcessing -> *Provides camera & hand coordinate logic, computations, and hand physics functions*
  

- Config.json file -> *Provides robotic arm specific details*

### Directory Breakdown

- Docs -> A location for the main research publication and any supporting documentations/publications or other informative files
- Resources -> A location for UI icons and other images used in the scripts
- src -> A location for all the program scripts

### Other Specific files:
- Req. Python File: DobotArm *Provides access to the dobot magician specific commands*
- Req. Python File: DobotDllType *Provides the dobot company provided hardware commands (Basically the dobot library)*
- URDF File: Dobot.urdf *Provides a simulation of the dobot (Was used for debugging purposes)*
- favicon.ico *GUI Taskbar Icon that doesnt work*
- My_logo.png *A generated logo for the program*
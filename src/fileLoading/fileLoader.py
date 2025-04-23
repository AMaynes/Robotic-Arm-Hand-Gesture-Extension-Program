import pkg_resources
import ctypes
import tempfile
import os
import atexit
import json
import sys
import shutil

# Global variable to store the DLL paths
all_Paths = []


def resource_path(relative_path):
    """ Get path to resource, works for dev and PyInstaller bundle """
    if hasattr(sys, "_MEIPASS"):
        # When running as an exe with PyInstaller
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # When running in development, ensure it resolves to the src directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # Go two levels up to src
        return os.path.join(project_root, relative_path)

def load_json_file(relative_path):
    """Load a JSON file from the correct path"""
    try:
        full_path = resource_path(relative_path)

        print(full_path)
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {relative_path}: {e}")
        return None

# This function loads a DLL from the package and returns its path for CDLL function
def loadDll(path, dll_name, end):
    global all_Paths  # Declare global to modify the variable outside the function

    try:
        # Step 1: Use pkg_resources to read the DLL as a byte string from the package
        dll_bytes = pkg_resources.resource_string(__name__, f"DLLS/{path}")

        # Step 2: Create the subdirectory for DLLs if it doesn't exist already
        temp_dll_dir = os.path.join(tempfile.gettempdir(), "DobotDlls")
        os.makedirs(temp_dll_dir, exist_ok=True)  # Create the folder if it doesn't exist

        # Step 3: Write the byte string to a file in the specified directory
        temp_dll_path = os.path.join(temp_dll_dir, dll_name + end)  # Ensure the DLL has the original name
        with open(temp_dll_path, "wb") as temp_file:
            temp_file.write(dll_bytes)

        # # Step 4: Print the result and check if the file exists
        # print(f"Written DLL to: {temp_dll_path}")
        # print(f"Exists? {os.path.exists(temp_dll_path)}")

        # Step 5: Add the DLL path to the global list
        # all_Paths.append(temp_dll_path)

        return temp_dll_path

    except Exception as e:
        print(f"Error loading DLL {path}: {e}")
        return None


def loadAllDLLs():
    global all_Paths  # Declare global to modify the variable outside the function

    #no need for clean up the DLLs will always write to the same folder and the os should clean it up eventually if
    # wanted
    # atexit.register(cleanUp)  # Register the cleanup function to be called at exit

    loadDll('DobotCalibrateDll.dll', 'DobotCalibrateDll', ".dll")
    loadDll('msvcp120.dll', 'msvcp120', ".dll")
    loadDll('Qt5Core.dll', 'Qt5Core', ".dll")
    loadDll('msvcr120.dll', 'msvcr120', ".dll")
    loadDll('Qt5Network.dll', 'Qt5Network', ".dll")
    loadDll('Qt5SerialPort.dll', 'Qt5SerialPort', ".dll")
    loadDll('DobotDll.h', 'DobotDll', ".h")

    return loadDll('DobotDll.dll', 'DobotDll', ".dll")


def cleanUp():
    global all_Paths  # Declare global to modify the variable outside the function

    # Ensure that we only attempt to remove the files if the list is not empty
    if all_Paths:  # This checks if the list is not empty
        for path in all_Paths:  # Loop over each stored path
            if os.path.exists(path):  # Ensure the file exists before deleting
                os.remove(path)  # Remove the file
        all_Paths = []  # Reset the list after cleanup (local scope)


# Function to load a text file from the package
def load_text_file(file_path):
    """
    Loads a text file from the package and returns its contents as a string.

    :param file_path: Path to the file inside the package
    :return: File contents as a string
    """
    try:
        # Use pkg_resources to read the file as a byte string from the package
        file_data = pkg_resources.resource_string(__name__, file_path)
        # Decode the byte string into a regular text string (assuming UTF-8 encoding)
        return file_data.decode('utf-8')
    except Exception as e:
        print(f"Error loading text file {file_path}: {e}")
        return None


# Function to load an image or binary file from the package
def load_image_file(file_path):
    """
    Loads an image or binary file from the package and returns its contents as raw byte data.

    :param file_path: Path to the file inside the package
    :return: File contents as raw byte data
    """
    try:
        # Use pkg_resources to read the file as a byte string from the package
        file_data = pkg_resources.resource_string(__name__, file_path)
        # Return the raw byte data for binary files like images or DLLs
        return file_data
    except Exception as e:
        print(f"Error loading image file {file_path}: {e}")
        return None


def load_icon_from_package(file_path):
    """
    Loads an icon file from the package and returns the icon's file path.
    :param file_path: Path to the icon file inside the package
    :return: Path to the loaded icon
    """
    try:
        # Use pkg_resources to get the icon file as a byte string
        icon_data = pkg_resources.resource_string(__name__, file_path)

        # Optionally, save the icon to a temporary file and return its path
        # Save the icon data to a file in a temporary location or a desired directory
        temp_file_path = "temp_icon.ico"  # You could choose a location for this file

        all_Paths.append(temp_file_path)  # Store the path in the global variable
        atexit.register(cleanUp)  # Register the cleanup function to be called at exit

        # Write the icon data to the file
        with open(temp_file_path, 'wb') as icon_file:
            icon_file.write(icon_data)

        return temp_file_path
    except Exception as e:
        print(f"Error loading icon file {file_path}: {e}")
    return None


# # Load JSON file function
# def load_json_file(file_path):
#     """
#         Loads a JSON file from the package and returns its parsed contents.
#         :param file_path: Path to the JSON file inside the package
#         :return: Parsed JSON data as a dictionary, or None if an error occurs
#         """
#
#     # tempPath = get_config_path(file_path)
#
#     try:
#         # Use pkg_resources to read the file as a byte string from the package
#         json_data = pkg_resources.resource_string(__name__, file_path).decode('utf-8')
#         # json_data = pkg_resources.resource_string('fileLoader', file_path).decode('utf-8')
#
#         return json.loads(json_data)  # Parse the JSON string into a dictionary
#     except Exception as e:
#         print(f"Error loading JSON file {file_path}: {e}")
#         return None

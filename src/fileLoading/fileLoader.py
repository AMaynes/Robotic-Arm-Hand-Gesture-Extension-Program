import pkg_resources
import ctypes
import tempfile
import os
import atexit

# Global variable to store the DLL paths
all_Paths = []

# This function loads a DLL from the package and returns its path for CDLL function
def loadDll(path):
    global all_Paths  # Declare global to modify the variable outside the function

    # Step 1: Use pkg_resources to read the DLL as a byte string from the package
    dll_bytes = pkg_resources.resource_string(__name__, f"Dll/{path}")

    # Step 2: Write the byte string to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(dll_bytes)
        temp_dll_path = temp_file.name  # Get the temporary file path

    all_Paths.append(temp_dll_path)  # Store the path in the global variable
    atexit.register(cleanUp)  # Register the cleanup function to be called at exit
    return temp_dll_path


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

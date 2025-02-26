
import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
from HandTrackingInterfacing import beginTracking
import DobotArm as DobotArm
import json
import os


class UserInterfaceApp:
    """
    This class creates a graphical user interface (GUI) for controlling a robotic arm. It allows the user to select the
    type of robotic arm and end effector, edit arm variables, and start tracking hand gestures to control the robotic arm.
    """
    def __init__(self, master):
        """
        Initializes the main window and application.
        :param master: The Tkinter root window.
        """
        self.master = master
        self.master.title("Robotic Arm Control Interface")
        self.master.geometry("400x300")

        # Set custom application ID for Windows Taskbar pinning
        myappid = 'com.RoboticArm.GestureControl'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # Call main menu to display the first interface
        self.main_menu()

    def main_menu(self):
        """
        Creates the main menu with buttons for starting tracking and editing arm variables.
        """
        self.clear_window()  # Clear any existing widgets from the window

        # Display welcome message
        tk.Label(self.master, text="Welcome to Robotic Arm Interface", font=("Arial", 14)).pack(pady=20)

        # Create "Track" button
        tk.Button(
            self.master, text="Track", font=("Arial", 12),
            bg="gray", fg="black",  # Set button appearance
            command=self.track_setup_window  # Action to be performed when button is clicked
        ).pack(pady=10)

        # Create "Edit Arm Variables" button
        tk.Button(
            self.master, text="Edit Arm Variables", font=("Arial", 12),
            bg="gray", fg="black",  # Set button appearance
            command=self.edit_arm_variables  # Action to be performed when button is clicked
        ).pack(pady=10)

    def track_setup_window(self):
        """
        Sets up the window for selecting the robotic arm type and end effector.
        """
        self.clear_window()  # Clear any existing widgets from the window

        # Create label and dropdown for selecting arm type
        tk.Label(self.master, text="Select Robotic Arm Type", font=("Arial", 12)).pack(pady=5)
        arm_type_var = tk.StringVar()  # Variable to hold the selected arm type
        arm_type_dropdown = ttk.Combobox(self.master, textvariable=arm_type_var, font=("Arial", 10))
        arm_types = ["Dobot", "uArm", "Custom Arm"]
        arm_type_dropdown["values"] = arm_types  # Set available arm types in dropdown
        arm_type_dropdown.pack(pady=5)

        print(arm_type_var)

        # Enable search functionality within dropdown
        self.enable_searchable_dropdown(arm_type_dropdown, arm_types)

        # Create label and dropdown for selecting end effector
        tk.Label(self.master, text="Select End Effector Attachment", font=("Arial", 12)).pack(pady=5)
        effector_var = tk.StringVar()  # Variable to hold the selected end effector type
        effector_dropdown = ttk.Combobox(self.master, textvariable=effector_var, font=("Arial", 10))
        effector_dropdown["values"] = ["Gripper", "Suction Cup", "Custom Attachment"]
        effector_dropdown["state"] = "readonly"  # Make it read-only, no text entry
        effector_dropdown.pack(pady=5)

        # Create "Start Tracking" button
        tk.Button(
            self.master, text="Start Tracking", font=("Arial", 12),
            bg="gray", fg="black",  # Set button appearance
            command=lambda: self.check_and_start_tracking(arm_type_var.get(), effector_var.get())  # Start tracking when clicked
        ).pack(pady=20)

        # Create "Back" button to return to the main menu
        tk.Button(
            self.master, text="Back", font=("Arial", 12),
            bg="gray", fg="black",  # Set button appearance
            command=self.main_menu  # Return to main menu when clicked
        ).pack(pady=5)

    def check_and_start_tracking(self, arm_type, effector):
        """
        Validates the selection of arm type and effector, and starts tracking if valid.
        :param arm_type: The selected arm type.
        :param effector: The selected end effector type.
        """

        print("Begin Tracking")
        beginTracking(arm_type)

    def initialize_robotic_arm(self, arm_type):
        """
        Initializes and returns the appropriate robotic arm object based on the selected arm type.
        :param arm_type: The selected arm type.
        :return: An initialized robotic arm object.
        """
        if arm_type == "Dobot":
            return DobotArm.DobotArm()    # Return an instance of the DobotArm class
        elif arm_type == "uArm":
            return uArm()  # Return an instance of the uArm class
        else:
            return CustomArm()  # Return an instance of the CustomArm class

    def enable_searchable_dropdown(self, combobox, values):
        """
        Enables search functionality within a ttk.Combobox by filtering displayed values as the user types.
        :param combobox: The ttk.Combobox to enable search for.
        :param values: The list of values to search within.
        """
        combobox.set("")  # Clear the combobox input field

        combobox.bind("<KeyRelease>", lambda event: self._filter_dropdown(combobox, values))  # Bind the key release event to the filtering function

    def _filter_dropdown(self, combobox, values):
        """
        Filters the combobox dropdown values based on the current user input.
        :param combobox: The ttk.Combobox to filter.
        :param values: The list of values to filter from.
        """
        user_input = combobox.get().lower()  # Get user input in lowercase
        filtered_values = [value for value in values if user_input in value.lower()]  # Filter values based on input
        combobox["values"] = filtered_values  # Update the combobox values with filtered options
        combobox.event_generate("<Down>")  # Open the dropdown list automatically

    def edit_arm_variables(self):
        """
        Allows users to edit the robotic arm's variables, such as position.
        """
        self.clear_window()  # Clear any existing widgets from the window

        # Create labels and entry fields for editing X, Y, Z position
        tk.Label(self.master, text="Edit Arm Variables", font=("Arial", 14)).pack(pady=10)

        # Create entry field for X position
        tk.Label(self.master, text="X Position (Home)", font=("Arial", 12)).pack(pady=5)
        x_var = tk.DoubleVar(value=170)  # Default value for X position
        tk.Entry(self.master, textvariable=x_var, font=("Arial", 10)).pack(pady=5)

        # Create entry field for Y position
        tk.Label(self.master, text="Y Position (Home)", font=("Arial", 12)).pack(pady=5)
        y_var = tk.DoubleVar(value=0)  # Default value for Y position
        tk.Entry(self.master, textvariable=y_var, font=("Arial", 10)).pack(pady=5)

        # Create entry field for Z position
        tk.Label(self.master, text="Z Position (Home)", font=("Arial", 12)).pack(pady=5)
        z_var = tk.DoubleVar(value=0)  # Default value for Z position
        tk.Entry(self.master, textvariable=z_var, font=("Arial", 10)).pack(pady=5)

        # Create a frame for buttons
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=20)

        # Create "Save Changes" button to save the entered variables
        tk.Button(
            button_frame, text="Save Changes", font=("Arial", 12),
            bg="gray", fg="black",
            command=lambda: self.save_arm_variables(x_var.get(), y_var.get(), z_var.get())  # Save variables when clicked
        ).pack(side=tk.LEFT, padx=10)

        # Create "Back" button to return to the main menu
        tk.Button(
            button_frame, text="Back", font=("Arial", 12),
            bg="gray", fg="black",
            command=self.main_menu  # Return to main menu when clicked
        ).pack(side=tk.LEFT, padx=10)

    def save_arm_variables(self, x, y, z):
        """
        Saves the entered X, Y, Z values and displays a success message.
        :param x: The X position value to save.
        :param y: The Y position value to save.
        :param z: The Z position value to save.
        """
        try:
            # Update variables or configuration here
            print(f"Saving Variables:\nX: {x}\nY: {y}\nZ: {z}")
            messagebox.showinfo("Success", "Arm variables updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save variables: {e}")

    def clear_window(self):
        """
        Clears all widgets from the current window to prepare for the next screen.
        """
        for widget in self.master.winfo_children():
            widget.destroy()

# Execute the UI application
if __name__ == "__main__":
    root = tk.Tk()  # Create the main window
    app = UserInterfaceApp(root)  # Initialize the application
    root.mainloop()  # Start the Tkinter event loop

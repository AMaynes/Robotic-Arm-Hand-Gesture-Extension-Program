import os
import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
from src.GUI.Tracker import beginTracking
from src.fileLoading.fileLoader import *


class UserInterfaceApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Robotic Arm Control Interface")
        self.master.geometry("400x300")
        myappid = 'com.RoboticArm.GestureControl'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # base_dir = os.path.dirname(os.path.dirname(__file__))  # Moves up one level from "src"
        # icon_path = os.path.join(base_dir, "Resources", "favicon.ico")

        icon_path = load_icon_from_package('Resources/favicon.ico')
        self.master.iconbitmap(icon_path)

        # DEBUG QUICK START (Don't have to go through the UI to connect to the dobot)
        debugStart = True
        if debugStart:
            beginTracking("Dobot")


        # Main Menu
        self.main_menu()

    def main_menu(self):
        """Main menu with 'Track' and 'Edit Arm Variables' options."""
        self.clear_window()

        # Welcome
        tk.Label(self.master, text="Welcome to Robotic Arm Interface", font=("Arial", 14)).pack(pady=20)

        # Track Button
        tk.Button(
            self.master, text="Track", font=("Arial", 12),
            bg="gray", fg="black",  # Gray background, black text
            command=self.track_setup_window
        ).pack(pady=10)

        # Edit Arm Variables Button
        tk.Button(
            self.master, text="Edit Arm Variables", font=("Arial", 12),
            bg="gray", fg="black",  # Gray background, black text
            command=self.edit_arm_variables
        ).pack(pady=10)

    def track_setup_window(self):
        """Setup window for selecting robotic arm type and end effector."""
        self.clear_window()

        # Dropdown Labels
        tk.Label(self.master, text="Select Robotic Arm Type", font=("Arial", 12)).pack(pady=5)

        # Searchable Robotic Arm Type Dropdown
        arm_type_var = tk.StringVar()
        arm_type_dropdown = ttk.Combobox(self.master, textvariable=arm_type_var, font=("Arial", 10))
        arm_types = ["Dobot", "uArm", "Custom Arm"]
        arm_type_dropdown["values"] = arm_types
        arm_type_dropdown.pack(pady=5)

        # Enable searching within dropdown
        self.enable_searchable_dropdown(arm_type_dropdown, arm_types)

        # End Effector Dropdown Label
        tk.Label(self.master, text="Select End Effector Attachment", font=("Arial", 12)).pack(pady=5)

        # End Effector Dropdown
        effector_var = tk.StringVar()
        effector_dropdown = ttk.Combobox(self.master, textvariable=effector_var, font=("Arial", 10))
        effector_dropdown["values"] = ["Gripper", "Suction Cup", "Custom Attachment"]
        effector_dropdown["state"] = "readonly"
        effector_dropdown.pack(pady=5)

        # Confirm Button
        tk.Button(
            self.master, text="Start Tracking", font=("Arial", 12),
            bg="gray", fg="black",  # Gray background, black text
            command=lambda: self.start_tracking(arm_type_var.get(), effector_var.get())
        ).pack(pady=20)

        # Back Button
        tk.Button(
            self.master, text="Back", font=("Arial", 12),
            bg="gray", fg="black",  # Gray background, black text
            command=self.main_menu
        ).pack(pady=5)

    def enable_searchable_dropdown(self, combobox, values):
        """
        Enable searching within a ttk.Combobox by filtering displayed values.
        :param combobox: The ttk.Combobox to enhance.
        :param values: The list of values to search within.
        """
        combobox.set("")
        combobox.bind("<KeyRelease>", lambda event: self._filter_dropdown(combobox, values))

    def _filter_dropdown(self, combobox, values):
        """
        Filter the values in the dropdown based on the current input.
        :param combobox: The ttk.Combobox to filter.
        :param values: The list of values to filter from.
        """
        user_input = combobox.get().lower()
        filtered_values = [value for value in values if user_input in value.lower()]
        combobox["values"] = filtered_values
        combobox.event_generate("<Down>")  # Open the dropdown automatically

    def edit_arm_variables(self):
        """Allow users to edit robotic arm variables. Only place holding variables for now."""
        self.clear_window()

        # Create labels and entry fields for variables
        tk.Label(self.master, text="Edit Arm Variables", font=("Arial", 14)).pack(pady=10)

        # Variable 1: X Position
        tk.Label(self.master, text="X Position (Home)", font=("Arial", 12)).pack(pady=5)
        x_var = tk.DoubleVar(value=170)  # Default value
        tk.Entry(self.master, textvariable=x_var, font=("Arial", 10)).pack(pady=5)

        # Variable 2: Y Position
        tk.Label(self.master, text="Y Position (Home)", font=("Arial", 12)).pack(pady=5)
        y_var = tk.DoubleVar(value=0)  # Default value
        tk.Entry(self.master, textvariable=y_var, font=("Arial", 10)).pack(pady=5)

        # Variable 3: Z Position
        tk.Label(self.master, text="Z Position (Home)", font=("Arial", 12)).pack(pady=5)
        z_var = tk.DoubleVar(value=0)  # Default value
        tk.Entry(self.master, textvariable=z_var, font=("Arial", 10)).pack(pady=5)

        # Frame for Buttons
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=20)

        # Save Button
        tk.Button(
            button_frame, text="Save Changes", font=("Arial", 12),
            bg="gray", fg="black",
            command=lambda: self.save_arm_variables(x_var.get(), y_var.get(), z_var.get())
        ).pack(side=tk.LEFT, padx=10)

        # Back Button
        tk.Button(
            button_frame, text="Back", font=("Arial", 12),
            bg="gray", fg="black",
            command=self.main_menu
        ).pack(side=tk.LEFT, padx=10)

    def save_arm_variables(self, x, y, z):
        """Save the edited arm variables."""
        try:
            # Update variables in your program
            print(f"Saving Variables:\nX: {x}\nY: {y}\nZ: {z}")
            
            # Example: Update a configuration file or global variables
            # config["robotic_arm"]["home_position"] = {"x": x, "y": y, "z": z}

            # Display success message
            messagebox.showinfo("Success", "Arm variables updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save variables: {e}")

    def start_tracking(self, arm_type, end_effector):
        """Handle starting the tracking functionality."""
        if not arm_type or not end_effector:
            messagebox.showwarning("Incomplete Selection", "Please select both Arm Type and End Effector!")
            return
        else:
            beginTracking(arm_type)

        print(f"Tracking Started!\nArm: {arm_type}\nEnd Effector: {end_effector}")

    def clear_window(self):
        """Clear all widgets from the current window."""
        for widget in self.master.winfo_children():
            widget.destroy()


# Execute UI
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = UserInterfaceApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        print("Exiting... on error")
        exit(1)

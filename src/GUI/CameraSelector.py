import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import atexit

MAX_CAMERAS = 5  # You can change this based on your system


class CameraPreview:
    def __init__(self, master, cam_index):
        self.master = master
        self.cam_index = cam_index
        self.var = tk.IntVar()
        self.cap = cv2.VideoCapture(cam_index)

        self.frame = tk.Frame(master)

        self.label = tk.Label(self.frame)  # For showing the video frame
        self.label.grid(row=0, column=0, padx=10)  # Camera on the left

        self.checkbox = tk.Checkbutton(self.frame, text=f"Camera {cam_index}", variable=self.var)
        self.checkbox.grid(row=0, column=1, sticky='w')  # Checkbox on the right, aligned to west

        self.running = True
        self.update_frame()

    def update_frame(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (200, 150))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.config(image=imgtk)

        self.master.after(30, self.update_frame)

    def stop(self):
        self.running = False
        self.cap.release()


def find_available_cameras(max_index=MAX_CAMERAS):
    available = []
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.append(i)
            cap.release()
        else:
            break
    return available


## this creates a GUI and returns the index of the selected camera it also takes in a
def getCamera(label, ignore):
    root = tk.Tk()
    root.title("Camera Selector")
    root.geometry("400x500")
    root.minsize(400, 500)

    tk.Label(root, text=label, font=("Arial", 14)).pack(pady=10)

    # Wrap canvas and scrollbar in a content frame (top portion)
    content_frame = tk.Frame(root)
    content_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(content_frame)
    scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Centered grid container
    grid_container = tk.Frame(scrollable_frame)
    grid_container.pack(anchor="center", pady=10)

    previews = []
    selected_camera = {'index': None}
    available = find_available_cameras()

    columns = 1  # Number of columns in the grid

    for idx, cam_idx in enumerate(available):
        if cam_idx == ignore:
            continue
        preview = CameraPreview(grid_container, cam_idx)
        previews.append(preview)
        preview.frame.grid(row=idx, column=0, padx=40, pady=10)

    if not previews:
        return None

    def submit_selection():
        selected = [p.cam_index for p in previews if p.var.get() == 1]
        if not selected:
            messagebox.showwarning("Warning", "No camera selected.")
        elif len(selected) > 1:
            messagebox.showwarning("Warning", "Please select only one camera.")
        else:
            selected_camera['index'] = selected[0]
            root.quit()

    def on_close():
        for preview in previews:
            preview.stop()
        root.quit()

    # Button frame at the bottom
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    # Submit button
    submit_button = tk.Button(button_frame, text="Submit", command=submit_selection)
    submit_button.pack(side="left", padx=10)

    def return_none_and_quit():
        selected_camera['index'] = None
        root.quit()

    # Ignore button
    if(label == "Please Select a Vision Camera"):
        ignore_button = tk.Button(button_frame, text="Ignore", command=return_none_and_quit)
        ignore_button.pack(side="left", padx=10)

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()

    for preview in previews:
        preview.stop()
    root.destroy()

    return selected_camera['index']



# Run it
camera = getCamera("Please Select a Tracking Camera", -1)

camera = getCamera("Please Select a Vision Camera", -1)
print(f"Selected camera: {camera}")

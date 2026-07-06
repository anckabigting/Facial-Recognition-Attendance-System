import dlib
import numpy as np
import cv2
import os
import shutil
import logging
import tkinter as tk
from tkinter import font as tkFont, messagebox
from PIL import Image, ImageTk

detector = dlib.get_frontal_face_detector()


class Face_Register:
    def __init__(self):

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.path_photos_from_camera = os.path.join(
            BASE_DIR, "data", "data_faces_from_camera"
        )

        # ================= STATE =================
        self.current_frame_faces_cnt = 0
        self.existing_faces_cnt = 0
        self.ss_cnt = 0
        self.current_face_dir = ""
        self.face_folder_created_flag = False
        self.current_frame = None
        
        # Variables for face ROI with padding (like in attached code)
        self.face_ROI_width_start = 0
        self.face_ROI_height_start = 0
        self.face_ROI_width = 0
        self.face_ROI_height = 0
        self.ww = 0  # padding width
        self.hh = 0  # padding height
        self.out_of_range_flag = False

        self.cap = cv2.VideoCapture(0)

        # ================= WINDOW =================
        self.win = tk.Tk()
        self.win.title("CvSU | Face Registration System")
        self.win.geometry("1320x820")
        self.win.configure(bg="#f1f3f5")
        self.win.resizable(False, False)

        # ================= COLORS =================
        self.GREEN = "#006837"
        self.GREEN_DARK = "#004d26"
        self.WHITE = "#ffffff"
        self.TEXT_MUTED = "#6c757d"
        self.SUCCESS = "#198754"
        self.DANGER = "#dc3545"

        # ================= FONTS =================
        self.font_title = tkFont.Font(family="Poppins", size=18, weight="bold")
        self.font_subtitle = tkFont.Font(family="Inter", size=11)
        self.font_section = tkFont.Font(family="Inter", size=13, weight="bold")
        self.font_metric = tkFont.Font(family="Inter", size=22, weight="bold")
        self.font_text = tkFont.Font(family="Inter", size=10)
        self.font_button = tkFont.Font(family="Inter", size=11, weight="bold")

        # ================= HEADER =================
        header = tk.Frame(self.win, bg=self.GREEN, height=110)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="CAVITE STATE UNIVERSITY",
                 font=self.font_title, fg="white", bg=self.GREEN).pack(pady=(25, 2))

        tk.Label(header, text="Face Recognition Registration Module",
                 font=self.font_subtitle, fg="#d4edda", bg=self.GREEN).pack()

        # ================= BODY =================
        body = tk.Frame(self.win, bg="#f1f3f5")
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # ================= CAMERA =================
        cam_card = tk.Frame(body, bg=self.WHITE)
        cam_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 16))

        tk.Label(cam_card, text="Live Camera Feed",
                 font=self.font_section, bg=self.WHITE).pack(anchor="w", padx=20, pady=(16, 8))

        self.label = tk.Label(cam_card, bg="black")
        self.label.pack(padx=20, pady=20)

        # ================= RIGHT PANEL =================
        right = tk.Frame(body, bg="#f1f3f5", width=420)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)

        # ---------- METRICS ----------
        metrics = tk.Frame(right, bg="#f1f3f5")
        metrics.pack(fill=tk.X)

        def metric(title, value):
            card = tk.Frame(metrics, bg=self.WHITE)
            card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)
            tk.Label(card, text=title, fg=self.TEXT_MUTED,
                     font=self.font_text, bg=self.WHITE).pack(pady=(12, 2))
            lbl = tk.Label(card, text=value,
                           font=self.font_metric, bg=self.WHITE)
            lbl.pack(pady=(0, 12))
            return lbl

        self.kpi_students = metric("REGISTERED STUDENTS", "0")
        self.kpi_faces = metric("FACES DETECTED", "0")

        # ---------- STATUS ----------
        status = tk.Frame(right, bg=self.WHITE)
        status.pack(fill=tk.X, padx=6, pady=12)

        tk.Label(status, text="SYSTEM STATUS",
                 font=self.font_section, bg=self.WHITE).pack(anchor="w", padx=12, pady=(10, 4))

        self.label_status = tk.Label(status, text="READY",
                                     fg=self.SUCCESS, bg=self.WHITE,
                                     font=self.font_text)
        self.label_status.pack(anchor="w", padx=12, pady=(0, 10))

        # ---------- CONTROLS ----------
        def step(title):
            box = tk.LabelFrame(right, text=title,
                                font=self.font_section, bg=self.WHITE)
            box.pack(fill=tk.X, padx=6, pady=8)
            return box

        step1 = step("Step 1: Reset Database")
        tk.Button(step1, text="Clear Face Records",
                  bg=self.DANGER, fg="white", relief=tk.FLAT,
                  font=self.font_button,
                  command=self.GUI_clear_data).pack(fill=tk.X, padx=12, pady=10)

        step2 = step("Step 2: Register Student")
        tk.Label(step2, text="Last Name, First Name Middle Initial (e.g., Dela Cruz, Juan A.)",
                 font=self.font_text, bg=self.WHITE).pack(anchor="w", padx=12)
        self.input_name = tk.Entry(step2)
        self.input_name.pack(fill=tk.X, padx=12, pady=6)

        tk.Button(step2, text="Create Student Profile",
                  bg=self.GREEN, fg="white", relief=tk.FLAT,
                  font=self.font_button,
                  command=self.GUI_get_input_name).pack(fill=tk.X, padx=12, pady=10)

        step3 = step("Step 3: Capture Face Images")
        tk.Button(step3, text="Save Face Image",
                  bg=self.GREEN_DARK, fg="white", relief=tk.FLAT,
                  font=self.font_button,
                  command=self.save_current_face).pack(fill=tk.X, padx=12, pady=12)

        # ---------- EXIT (FIXED) ----------
        exit_frame = tk.Frame(right, bg="#f1f3f5")
        exit_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=(6, 6))

        tk.Button(exit_frame, text="Exit System",
                  bg=self.DANGER, fg="white",
                  relief=tk.FLAT, font=self.font_button,
                  command=self.safe_exit).pack(fill=tk.X)

        # ---------- SYSTEM LOG ----------
        log_frame = tk.LabelFrame(right, text="System Activity Log",
                                  font=self.font_section, bg=self.WHITE)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=(10, 6))

        self.log_box = tk.Text(log_frame, wrap="word",
                               bg=self.WHITE, fg=self.TEXT_MUTED,
                               font=self.font_text, relief=tk.FLAT)
        self.log_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        self.log_box.insert(
            tk.END,
            "🟢 System ready.\n➡ Register a student to begin face enrollment.\n"
        )
        self.log_box.config(state=tk.DISABLED)

    # ================= BACKEND =================
    def log(self, message):
        self.log_box.config(state=tk.NORMAL)
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state=tk.DISABLED)

    def safe_exit(self):
        if messagebox.askyesno("Exit", "Exit face registration system?"):
            self.cap.release()
            self.win.destroy()

    def load_existing_students(self):
        if not os.path.isdir(self.path_photos_from_camera):
            return
        folders = [d for d in os.listdir(self.path_photos_from_camera)
                   if d.startswith("person_")]
        self.existing_faces_cnt = len(folders)
        self.kpi_students["text"] = str(self.existing_faces_cnt)

    def GUI_clear_data(self):
        if os.path.isdir(self.path_photos_from_camera):
            for f in os.listdir(self.path_photos_from_camera):
                shutil.rmtree(os.path.join(self.path_photos_from_camera, f))
        self.existing_faces_cnt = 0
        self.kpi_students["text"] = "0"
        self.log("✔ Database reset completed.")

    def GUI_get_input_name(self):
        name = self.input_name.get().strip()
        if not name:
            self.log("⚠ Please enter a valid name.")
            return

        self.existing_faces_cnt += 1
        self.current_face_dir = os.path.join(
            self.path_photos_from_camera,
            f"person_{self.existing_faces_cnt}_{name}"
        )
        os.makedirs(self.current_face_dir, exist_ok=True)
        self.face_folder_created_flag = True
        self.ss_cnt = 0
        self.kpi_students["text"] = str(self.existing_faces_cnt)

        self.log(f"✔ Student registered: {name}")
        self.log("➡ Look straight at the camera and click 'Save Face Image'.")

    def save_current_face(self):
        if not self.face_folder_created_flag:
            self.log("⚠ Create student profile first.")
            return

        if self.current_frame_faces_cnt != 1:
            self.log("⚠ Ensure exactly ONE face is visible.")
            return

        if self.ss_cnt >= 5:
            self.log("✔ Face enrollment already complete.")
            return

        # Check if face is out of range (like in attached code)
        if self.out_of_range_flag:
            self.log("⚠ Please do not go out of range!")
            return

        self.ss_cnt += 1
        
        # Create a blank image with double the size of face ROI (like in attached code)
        face_ROI_image = np.zeros((int(self.face_ROI_height * 2), 
                                  self.face_ROI_width * 2, 3), np.uint8)
        
        # Copy the face region with padding from current frame to the blank image
        for ii in range(self.face_ROI_height * 2):
            for jj in range(self.face_ROI_width * 2):
                face_ROI_image[ii][jj] = self.current_frame[
                    self.face_ROI_height_start - self.hh + ii
                ][
                    self.face_ROI_width_start - self.ww + jj
                ]
        
        filename = os.path.join(
            self.current_face_dir, f"img_face_{self.ss_cnt}.jpg"
        )

        # Convert from RGB to BGR for saving with OpenCV
        face_ROI_image_bgr = cv2.cvtColor(face_ROI_image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(filename, face_ROI_image_bgr)

        tips = [
            "Look straight at the camera",
            "Turn slightly left",
            "Turn slightly right",
            "Tilt your head up",
            "Tilt your head down"
        ]

        self.log(f"📸 Face picture captured successfully ({self.ss_cnt}/5)")
        if self.ss_cnt < 5:
            self.log(f"➡ {tips[self.ss_cnt]}")
        else:
            self.log("✔ Face enrollment complete.")

    def get_frame(self):
        ret, frame = self.cap.read()
        frame = cv2.resize(frame, (640, 480))
        return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def process(self):
        ret, self.current_frame = self.get_frame()
        faces = detector(self.current_frame, 0)

        if ret:
            self.current_frame_faces_cnt = len(faces)
            self.kpi_faces["text"] = str(len(faces))
            self.label_status["text"] = "READY" if faces else "WAITING"
            self.label_status["fg"] = self.SUCCESS if faces else self.TEXT_MUTED

            # Process each detected face (like in attached code)
            for d in faces:
                # Get face coordinates
                self.face_ROI_width_start = d.left()
                self.face_ROI_height_start = d.top()
                self.face_ROI_height = (d.bottom() - d.top())
                self.face_ROI_width = (d.right() - d.left())
                self.hh = int(self.face_ROI_height / 2)  # Half height for padding
                self.ww = int(self.face_ROI_width / 2)   # Half width for padding

                # Check if face is within frame boundaries (like in attached code)
                if (d.right() + self.ww > 640 or 
                    d.bottom() + self.hh > 480 or 
                    d.left() - self.ww < 0 or 
                    d.top() - self.hh < 0):
                    self.out_of_range_flag = True
                    rect_color = (255, 0, 0)  # Blue for out of range
                    self.label_status["text"] = "OUT OF RANGE"
                    self.label_status["fg"] = self.DANGER
                else:
                    self.out_of_range_flag = False
                    rect_color = (255, 255, 255)  # White for in range
                    self.label_status["text"] = "READY"
                    self.label_status["fg"] = self.SUCCESS

                # Draw the rectangle (this shows exactly what will be saved)
                # The rectangle size is face width + padding on all sides
                cv2.rectangle(
                    self.current_frame,
                    (self.face_ROI_width_start - self.ww, self.face_ROI_height_start - self.hh),
                    (self.face_ROI_width_start + self.face_ROI_width + self.ww, 
                     self.face_ROI_height_start + self.face_ROI_height + self.hh),
                    rect_color,  # White or blue based on position
                    2  # Line thickness
                )

            img = ImageTk.PhotoImage(Image.fromarray(self.current_frame))
            self.label.configure(image=img)
            self.label.image = img

        self.win.after(20, self.process)

    def run(self):
        os.makedirs(self.path_photos_from_camera, exist_ok=True)
        self.load_existing_students()
        self.process()
        self.win.mainloop()


def main():
    logging.basicConfig(level=logging.INFO)
    Face_Register().run()


if __name__ == "__main__":
    main()
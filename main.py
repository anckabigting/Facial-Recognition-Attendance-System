import tkinter as tk
import subprocess
import sys
import os
import time
import webbrowser
from tkinter import font as tkFont
from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================= ACTIONS ================= #

def run_enrollment():
    subprocess.call([sys.executable, "get_faces_from_camera_tkinter.py"])

def run_feature_extraction():
    subprocess.call([sys.executable, "features_extraction_to_csv.py"])

def run_attendance():
    subprocess.call([sys.executable, "attendance_taker.py"])

def run_attendance_viewer():
    """
    Start Flask server in background and open browser automatically
    """
    flask_app = os.path.join(BASE_DIR, "app.py")

    subprocess.Popen(
        [sys.executable, flask_app],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Give Flask time to boot
    time.sleep(2)

    webbrowser.open("http://127.0.0.1:5000")

def exit_app():
    root.destroy()

# ---------------- GUI ---------------- #
root = tk.Tk()
root.title("CvSU | Face Recognition Attendance System")
root.geometry("520x720")
root.configure(bg="#f1f3f5")
root.resizable(False, False)

# Colors
CVSU_GREEN = "#006837"
CVSU_GREEN_DARK = "#004d26"
EXIT_RED = "#dc3545"
EXIT_RED_DARK = "#b02a37"
TEXT_DARK = "#212529"
TEXT_MUTED = "#6c757d"
WHITE = "#ffffff"

# Fonts
title_font = tkFont.Font(family="Poppins", size=18, weight="bold")
subtitle_font = tkFont.Font(family="Inter", size=11)
section_font = tkFont.Font(family="Inter", size=13, weight="bold")
button_font = tkFont.Font(family="Inter", size=11, weight="bold")
footer_font = tkFont.Font(family="Inter", size=9)

# ================= HEADER ================= #
header = tk.Frame(root, bg=CVSU_GREEN, height=180)
header.pack(fill=tk.X)
header.pack_propagate(False)

# Logo
logo_path = os.path.join(BASE_DIR, "logo.png")
logo_img = Image.open(logo_path).resize((80, 80), Image.LANCZOS)
logo = ImageTk.PhotoImage(logo_img)

tk.Label(header, image=logo, bg=CVSU_GREEN).pack(pady=(16, 6))

tk.Label(
    header,
    text="CAVITE STATE UNIVERSITY",
    font=title_font,
    fg=WHITE,
    bg=CVSU_GREEN
).pack(pady=(0, 2))

tk.Label(
    header,
    text="Face Recognition Attendance System",
    font=subtitle_font,
    fg="#d4edda",
    bg=CVSU_GREEN
).pack(pady=(0, 14))

# ================= MAIN CARD ================= #
card = tk.Frame(root, bg=WHITE)
card.pack(padx=25, pady=(20, 15), fill=tk.X)

tk.Label(
    card,
    text="System Controls",
    font=section_font,
    fg=TEXT_DARK,
    bg=WHITE
).pack(pady=(25, 5))

tk.Label(
    card,
    text="Please select an operation below",
    font=subtitle_font,
    fg=TEXT_MUTED,
    bg=WHITE
).pack(pady=(0, 20))

btn_container = tk.Frame(card, bg=WHITE)
btn_container.pack(pady=(0, 25))

def create_button(text, command, row, is_exit=False):
    bg = EXIT_RED if is_exit else CVSU_GREEN
    hover = EXIT_RED_DARK if is_exit else CVSU_GREEN_DARK

    btn = tk.Button(
        btn_container,
        text=text,
        font=button_font,
        bg=bg,
        fg=WHITE,
        activebackground=hover,
        relief=tk.FLAT,
        height=2,
        width=36,
        cursor="hand2",
        command=command
    )
    btn.grid(row=row, column=0, pady=8)

    btn.bind("<Enter>", lambda e: btn.config(bg=hover))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))

create_button("Enroll Student (Face Registration)", run_enrollment, 0)
create_button("Generate Facial Features Dataset", run_feature_extraction, 1)
create_button("Start Attendance Session", run_attendance, 2)
create_button("View Attendance Records", run_attendance_viewer, 3)
create_button("Exit Application", exit_app, 4, is_exit=True)

# ================= FOOTER ================= #
footer = tk.Frame(root, bg="#f1f3f5")
footer.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 12))

tk.Label(
    footer,
    text="© 2025 Cavite State University | For Academic Use Only",
    font=footer_font,
    fg=TEXT_MUTED,
    bg="#f1f3f5"
).pack()

root.eval('tk::PlaceWindow . center')
root.mainloop()
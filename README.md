# Face Recognition Based Attendance System

A **Python-based Face Recognition Attendance System** that uses **OpenCV, Dlib, and SQLite** to automatically record attendance through real-time face recognition. The system includes **face enrollment**, **anti-spoofing (blink detection)**, and a **web-based attendance viewer**.

---

## Features

- Real-time face detection and recognition  
- Dlib-based facial feature extraction  
- Anti-spoofing using blink detection (prevents photo attacks)  
- Automatic attendance logging (SQLite database)  
- GUI-based face enrollment and control panel (Tkinter)  
- Web interface to view attendance records (Flask)  

---

## Technologies Used

- **Python 3.11+**
- **OpenCV**
- **Dlib**
- **NumPy / Pandas**
- **SQLite**
- **Tkinter**
- **Flask**

---

## Project Structure (Simplified)

Face-Recognition-Based-Attendance-System-main/
│
├── app.py                              # Flask attendance viewer
├── main.py                             # Main control panel
├── attendance_taker.py                 # Face recognition & attendance logic
├── get_faces_from_camera_tkinter.py
├── features_extraction_to_csv.py
├── attendance.db # SQLite database
├── data/
│ ├── data_dlib/ # Dlib models
│ └── features_all.csv # Face features dataset
├── anti_spoofing/
│ └── blink_detector.py
│ └── liveness_detector.py
├── templates/
│ └── index.html # Attendance viewer UI
└── requirements.txt

---

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Face-Recognition-Based-Attendance-System-main

2. Install Python

Ensure Python 3.11 or later is installed.

3. Install dependencies
    ```pip install -r requirements.txt

---

## Usage Guide

1. Launch the main application
    ```python main.py

2. Enroll a student
    - Click “Enroll Student (Face Registration)”
    - Follow on-screen instructions to capture facial data

3. Generate facial features dataset
    - Click “Generate Facial Features Dataset”
    - This creates the feature embeddings required for recognition

4. Start attendance session
    - Click “Start Attendance Session”
    - The system will:
        - Detect faces
        - Verify liveness (blink detection)
        - Recognize registered individuals
        - Mark attendance automatically

5. View attendance records
    - Click “View Attendance Records”
    - Select date and time
    - Click “Show Attendance”
    - The result shows the total, on-time, late, and absent individuals.
    - Users are given the option to export the result via PDF or Spreadsheet format.

---

## Anti-Spoofing Note
The system uses blink detection to verify liveness.
Faces that do not exhibit real eye-blinking behavior are marked as SPOOF, preventing attendance from printed images or screens.

---

## Contributing

Contributions are welcome!
- Fork the repository
- Create a feature branch
- Submit a pull request
If you find bugs or have feature suggestions, feel free to open an issue.
import dlib
import numpy as np
import cv2
import os
import pandas as pd
import time
import logging
import sqlite3
import datetime
import math

from anti_spoofing.blink_detector import BlinkDetector

# ===================== MODELS =====================
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(
    "data/data_dlib/shape_predictor_68_face_landmarks.dat"
)
face_reco_model = dlib.face_recognition_model_v1(
    "data/data_dlib/dlib_face_recognition_resnet_model_v1.dat"
)

FEATURES_CSV = "data/features_all.csv"
DB_PATH = "attendance.db"

RECO_THRESHOLD = 0.4
CENTROID_DIST_THRESH = 60
LOCK_TIMEOUT = 1.2  # seconds

# ===================== DATABASE =====================
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    name TEXT,
    time TEXT,
    date DATE,
    UNIQUE(name, date)
)
""")
conn.commit()
conn.close()


class Face_Recognizer:
    def __init__(self):
        self.font = cv2.FONT_ITALIC

        self.last_time = time.time()
        self.fps = 0

        self.face_features_known_list = []
        self.face_name_known_list = []

        self.face_locks = {}
        self.next_face_id = 0

    # ===================== LOAD DATABASE =====================
    def get_face_database(self):
        if not os.path.exists(FEATURES_CSV):
            logging.error("features_all.csv not found")
            return False

        csv_rd = pd.read_csv(FEATURES_CSV, header=None)
        for i in range(csv_rd.shape[0]):
            self.face_name_known_list.append(csv_rd.iloc[i][0])
            self.face_features_known_list.append(
                np.array(csv_rd.iloc[i][1:], dtype=float)
            )

        logging.info("Loaded %d faces", len(self.face_name_known_list))
        return True

    # ===================== UTILS =====================
    @staticmethod
    def euclidean(p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def cleanup_locks(self):
        now = time.time()
        expired = [
            fid for fid, data in self.face_locks.items()
            if now - data["last_seen"] > LOCK_TIMEOUT
        ]
        for fid in expired:
            del self.face_locks[fid]

    def match_locked_face(self, centroid):
        for fid, data in self.face_locks.items():
            if self.euclidean(centroid, data["centroid"]) < CENTROID_DIST_THRESH:
                data["centroid"] = centroid
                data["last_seen"] = time.time()
                return fid
        return None

    # ===================== ATTENDANCE =====================
    def attendance(self, name):
        today = datetime.date.today().isoformat()
        now_time = datetime.datetime.now().strftime("%H:%M:%S")

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO attendance VALUES (?, ?, ?)",
            (name, now_time, today)
        )
        conn.commit()
        conn.close()

        logging.info("Attendance marked: %s", name)

    # ===================== FPS =====================
    def update_fps(self):
        now = time.time()
        self.fps = 1 / max(now - self.last_time, 1e-6)
        self.last_time = now

    # ===================== INFO PANEL =====================
    def draw_info_panel(self, frame, face_count):
        h, w, _ = frame.shape
        panel_width = 320
        panel = np.zeros((h, panel_width, 3), dtype=np.uint8)

        y = 40
        gap = 35

        def put(text, y, color=(0, 255, 0)):
            cv2.putText(panel, text, (15, y),
                        self.font, 0.7, color, 2, cv2.LINE_AA)

        put("ATTENDANCE SYSTEM", y); y += gap * 2
        put(f"FPS: {int(self.fps)}", y); y += gap
        put(f"Faces Detected: {face_count}", y); y += gap
        put(f"Faces Locked: {len(self.face_locks)}", y); y += gap * 2

        put("STATUS:", y); y += gap
        put("REAL / MARKED", y, (0, 255, 0)); y += gap
        put("UNKNOWN", y, (255, 255, 0)); y += gap
        put("SPOOF", y, (0, 0, 255)); y += gap * 2

        put("Press 'Q' to Quit", y, (200, 200, 200))

        return np.hstack((frame, panel))

    # ===================== MAIN LOOP =====================
    def process(self, stream):
        if not self.get_face_database():
            return

        while stream.isOpened():
            ret, img = stream.read()
            if not ret:
                break

            self.cleanup_locks()
            faces = detector(img, 0)

            for face in faces:
                l, t, r, b = face.left(), face.top(), face.right(), face.bottom()
                centroid = (int((l + r) / 2), int((t + b) / 2))

                lock_id = self.match_locked_face(centroid)

                # ================= LOCKED FACE =================
                if lock_id is not None:
                    lock = self.face_locks[lock_id]
                    shape = predictor(img, face)

                    if not lock["verified"]:
                        if lock["blink"].update(shape):
                            lock["verified"] = True
                        else:
                            name = "SPOOF"
                            color = (0, 0, 255)
                            cv2.rectangle(img, (l, t), (r, b), color, 2)
                            cv2.putText(img, name, (l, t - 10),
                                        self.font, 0.8, color, 2)
                            continue

                    if lock["name"] is None:
                        feature = np.array(
                            face_reco_model.compute_face_descriptor(img, shape)
                        )

                        distances = [
                            np.linalg.norm(feature - known)
                            for known in self.face_features_known_list
                        ]

                        if min(distances) < RECO_THRESHOLD:
                            idx = distances.index(min(distances))
                            lock["name"] = self.face_name_known_list[idx]
                            self.attendance(lock["name"])
                        else:
                            lock["name"] = "UNKNOWN"

                    name = lock["name"]
                    color = (0, 255, 0) if name != "UNKNOWN" else (255, 255, 0)

                # ================= NEW FACE =================
                else:
                    self.face_locks[self.next_face_id] = {
                        "name": None,
                        "centroid": centroid,
                        "last_seen": time.time(),
                        "blink": BlinkDetector(),
                        "verified": False
                    }
                    self.next_face_id += 1
                    continue

                cv2.rectangle(img, (l, t), (r, b), color, 2)
                cv2.putText(img, name, (l, t - 10),
                            self.font, 0.8, color, 2)

            self.update_fps()
            img = self.draw_info_panel(img, len(faces))
            cv2.imshow("CvSU | Attendance System", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        stream.release()
        cv2.destroyAllWindows()

    def run(self):
        cap = cv2.VideoCapture(0)
        self.process(cap)


def main():
    logging.basicConfig(level=logging.INFO)
    Face_Recognizer().run()


if __name__ == "__main__":
    main()
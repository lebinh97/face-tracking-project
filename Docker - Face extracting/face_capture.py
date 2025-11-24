import cv2
import time
import mediapipe as mp
import numpy as np
import os
import re
import asyncio
import httpx
import threading
from datetime import datetime

# ======================
# Async API Sender
# ======================

async def send_to_encoder(image_path, encoder_url):
    async with httpx.AsyncClient() as client:
        try:
            with open(image_path, "rb") as f:
                files = {"file": (os.path.basename(image_path), f, "image/jpeg")}
                response = await client.post(encoder_url, files=files, timeout=5)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Sent {os.path.basename(image_path)} to encoder: {response.status_code}", flush=True)
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Failed to send {os.path.basename(image_path)}: {e}", flush=True)


def send_to_encoder_background(image_path, encoder_url):
    """Runs the async function in a background event loop safely."""
    def run():
        asyncio.run(send_to_encoder(image_path, encoder_url))
    threading.Thread(target=run, daemon=True).start()

# ======================
# Face Capture Logic
# ======================

def capture_stable_faces(
    use_camera=True,
    video_path=None,
    image_dir="Face image",
    stable_sec=1.25,
    min_detection_confidence=0.9,
    brightness_threshold=40,
    max_pitch=10,
    max_yaw=20,
    max_num_faces=1,
    encoder_url="http://localhost:8001/encode",  # 🔹 new configurable parameter
):
    if not use_camera and (video_path is None or not os.path.exists(video_path)):
        raise ValueError("video_path must be provided and valid when use_camera=False")

    os.makedirs(image_dir, exist_ok=True)

    cap = cv2.VideoCapture(0 if use_camera else video_path)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera or video")

    mp_face_detection = mp.solutions.face_detection
    mp_face_mesh = mp.solutions.face_mesh
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=min_detection_confidence)
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=max_num_faces,
        refine_landmarks=True
    )

    def estimate_head_pose(image, landmarks, image_w, image_h):
        indices = [1, 33, 263, 61, 291, 199]
        image_points = np.array([
            (int(landmarks[idx].x * image_w), int(landmarks[idx].y * image_h)) for idx in indices
        ], dtype="double")

        model_points = np.array([
            (0.0, 0.0, 0.0),
            (-30.0, -30.0, -30.0),
            (30.0, -30.0, -30.0),
            (-30.0, 30.0, -30.0),
            (30.0, 30.0, -30.0),
            (0.0, 50.0, -10.0)
        ])

        focal_length = image_w
        center = (image_w / 2, image_h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")

        success, rotation_vector, _ = cv2.solvePnP(
            model_points, image_points, camera_matrix, np.zeros((4, 1))
        )

        if not success:
            return None, None, None

        rmat, _ = cv2.Rodrigues(rotation_vector)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
        return angles[0], angles[1], angles[2]

    face_valid_since = None
    face_saved_this_streak = False

    try:
        img_count = 0  

        while cap.isOpened():
            current_time = (
                cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                if not use_camera else time.time()
            )
            if current_time < 0:
                current_time = time.time()

            success, image = cap.read()
            if not success:
                print("End of video or failed to read frame.")
                break

            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_detection.process(rgb_image)
            face_is_valid = False

            if results.detections:
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    h, w, _ = image.shape
                    xmin, ymin = max(0, int(bbox.xmin * w)), max(0, int(bbox.ymin * h))
                    xmax, ymax = min(w, int((bbox.xmin + bbox.width) * w)), min(h, int((bbox.ymin + bbox.height) * h))
                    face_roi = image[ymin:ymax, xmin:xmax]

                    hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
                    if np.mean(hsv[:, :, 2]) < brightness_threshold:
                        continue

                    mesh_results = face_mesh.process(rgb_image)
                    if not mesh_results.multi_face_landmarks:
                        continue

                    face_landmarks = mesh_results.multi_face_landmarks[0]
                    pitch, yaw, roll = estimate_head_pose(image, face_landmarks.landmark, w, h)
                    if pitch is None or abs(pitch) > max_pitch or abs(yaw) > max_yaw:
                        continue

                    face_is_valid = True

                    if face_valid_since is None:
                        face_valid_since = current_time
                        face_saved_this_streak = False

                    # Saved the face
                    if not face_saved_this_streak and (current_time - face_valid_since) >= stable_sec:                    

                        # Get video name
                        if video_path:
                            video_name = os.path.splitext(os.path.basename(video_path))[0]
                        else:
                            video_name = "camera"

                        # Build the filename
                        face_filename_base = f"{video_name}_img{img_count}"

                        # Ensure directory exists
                        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                        image_dir_root = os.path.join(BASE_DIR, image_dir)
                        os.makedirs(image_dir_root, exist_ok=True)

                        # Save image
                        face_image_path = os.path.join(image_dir_root, f"{face_filename_base.strip()}.jpg")
                        cv2.imwrite(face_image_path, face_roi)
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📸 Saved after {stable_sec}s stable: {face_image_path}", flush=True)

                        # Send to encoder asynchronously
                        send_to_encoder_background(face_image_path, encoder_url)

                        img_count += 1  # increment for each saved image
                        face_saved_this_streak = True
                    break

            if not face_is_valid:
                face_valid_since = None
                face_saved_this_streak = False

    finally:
        cap.release()
        face_detection.close()
        face_mesh.close()

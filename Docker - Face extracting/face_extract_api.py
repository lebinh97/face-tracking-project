import os
import shutil
from datetime import datetime
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
from face_capture import capture_stable_faces  # import your existing function

# ======================
# 🌍 Load environment variables
# ======================
load_dotenv()  # Reads values from .env file

# Extract API configuration
EXTRACT_URL = os.getenv("EXTRACT_URL", "http://localhost:8000")
EXTRACT_API_PORT = int(os.getenv("EXTRACT_API_PORT", 8000))

# Encoder service configuration
ENCODER_URL = os.getenv("ENCODER_URL", "http://localhost:8001/encode")
ENCODER_API_PORT = int(os.getenv("ENCODER_API_PORT", 8001))

# Extract API Image
IMAGE_DIR = os.getenv("IMAGE_DIR", "Face Image")

# ======================
# 🚀 FastAPI Setup
# ======================
app = FastAPI(title="Face Capture API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# ⏰ Helper for timestamp logging
# ======================
def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

# ======================
# 🎥 API Endpoint
# ======================
@app.get("/metrics")
def metrics():
    return {"status": "ok"}


@app.post("/capture_faces")
async def capture_faces(video: UploadFile = File(...)):
    """Takes a video input, runs face capture, and returns status."""
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(BASE_DIR, "uploaded_videos")
        os.makedirs(upload_dir, exist_ok=True)

        temp_video_path = os.path.join(upload_dir, video.filename)
        log(f"📂 Temp video path: {temp_video_path}")

        with open(temp_video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        log(f"✅ Uploaded video saved: {video.filename}")

        # Pass encoder URL into your face capture function
        log(f"🎬 Starting face capture for {video.filename}")
        capture_stable_faces(
            use_camera=False,
            video_path=temp_video_path,
            image_dir=IMAGE_DIR,
            stable_sec=1.25,
            min_detection_confidence=0.9,
            brightness_threshold=40,
            max_pitch=10,
            max_yaw=20,
            encoder_url=ENCODER_URL
        )
        log(f"✅ Finished processing: {video.filename}")

        return JSONResponse({
            "status": "success",
            "message": f"Processed {video.filename}",
            "saved_dir": IMAGE_DIR
        })

    except Exception as e:
        log(f"❌ Error processing {video.filename}: {e}")
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)

    finally:
        try:
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
                log(f"🗑️ Temp file removed: {temp_video_path}")
        except Exception as cleanup_err:
            log(f"⚠️ Cleanup failed: {cleanup_err}")


# ======================
# 🟢 Run the API
# ======================
if __name__ == "__main__":
    log(f"🚀 Starting Extract API on port {EXTRACT_API_PORT}")
    log(f"📡 Using encoder endpoint: {ENCODER_URL}")
    uvicorn.run(app, host="0.0.0.0", port=EXTRACT_API_PORT)

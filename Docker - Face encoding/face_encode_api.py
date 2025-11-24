from fastapi import FastAPI, UploadFile, File, HTTPException
import io
import uvicorn
import numpy as np
from deepface import DeepFace
import os
import tempfile

app = FastAPI()

ENCODER_URL = os.getenv("ENCODER_URL", "http://localhost:8001/encode")
ENCODER_API_PORT = int(os.getenv("ENCODER_API_PORT", 8001))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_ENCODE_DIR = os.getenv("OUTPUT_ENCODE_DIR", "embeddings")
OUTPUT_IMAGE_DIR = os.getenv("OUTPUT_IMAGE_DIR", "face_images")

# Embedding folder
EMB_DIR = os.path.join(BASE_DIR, OUTPUT_ENCODE_DIR)
os.makedirs(EMB_DIR, exist_ok=True)

# 👉 NEW: Image folder
IMG_DIR = os.path.join(BASE_DIR, OUTPUT_IMAGE_DIR)
os.makedirs(IMG_DIR, exist_ok=True)

@app.post("/encode")
async def encode_image(file: UploadFile = File(...)):
    print(f"✅ Received: {file.filename} ({file.content_type})")

    contents = await file.read()

    # Validate image
    try:
        from PIL import Image
        image = Image.open(io.BytesIO(contents))
        image.verify()
    except Exception:
        raise HTTPException(status_code=400, detail="❌ Not a valid image file")

    if image.format != "JPEG":
        raise HTTPException(status_code=400, detail=f"❌ Expected JPEG, got {image.format}")

    print(f"✅ Valid JPEG image: {file.filename}")

    # Save temp file for DeepFace
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(contents)
            temp_file_path = temp_file.name

        emb = DeepFace.represent(
            img_path=temp_file_path,
            model_name="Facenet512",
            enforce_detection=False
        )[0]["embedding"]

        emb = np.array(emb)
        print(f"✅ Embedding generated, shape: {emb.shape}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ DeepFace error: {str(e)}")

    # Save embedding
    emb_path = os.path.join(EMB_DIR, f"{os.path.splitext(file.filename)[0]}.npy")
    np.save(emb_path, emb)
    print(f"✅ Embedding saved to {emb_path}")

    # 👉 NEW: Save the uploaded JPEG image
    img_path = os.path.join(IMG_DIR, file.filename)
    with open(img_path, "wb") as img_file:
        img_file.write(contents)
    print(f"📸 Image saved to {img_path}")

    return {
        "status": "embedding created",
        "file": file.filename,
        "vector_path": emb_path,
        "image_path": img_path
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=ENCODER_API_PORT)

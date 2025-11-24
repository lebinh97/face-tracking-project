from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from scipy.spatial.distance import cosine
from typing import List, Dict
from PIL import Image
import numpy as np
import base64
import os
import io
import uvicorn

app = FastAPI()

EMBEDDINGS_FOLDER = "/home/bngl1/projects/cs5939/embeddings"
IMAGES_FOLDER = "/home/bngl1/projects/cs5939/face_images"


def encode_image_to_base64(image_path: str):
    """Convert image to base64 so it can be returned in JSON."""
    try:
        img = Image.open(image_path)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode()
    except FileNotFoundError:
        return None


@app.get("/cluster_video_faces")
def cluster_video_faces(
    video_name: str = Query(...),
    threshold: float = Query(0.3)
):
    # Find all .npy files matching video_name
    files = [
        f for f in os.listdir(EMBEDDINGS_FOLDER)
        if f.endswith(".npy") and video_name in f
    ]

    if not files:
        raise HTTPException(
            status_code=404,
            detail=f"Video '{video_name}' not found in embeddings folder"
        )

    # Load all embeddings
    embeddings = {
        f[:-4]: np.load(f"{EMBEDDINGS_FOLDER}/{f}")
        for f in files
    }

    # Clustering logic
    groups = []
    used = set()

    for name1, emb1 in embeddings.items():
        if name1 in used:
            continue

        group = [name1]
        used.add(name1)

        for name2, emb2 in embeddings.items():
            if name2 not in used:
                dist = cosine(emb1, emb2)
                if dist < threshold:
                    group.append(name2)
                    used.add(name2)

        groups.append(group)

    # Build JSON response
    response = {
        "video_name": video_name,
        "threshold": threshold,
        "num_persons": len(groups),
        "groups": []
    }

    for i, group in enumerate(groups, 1):
        group_data = {
            "person_id": i,
            "faces": []
        }

        for name in group:
            img_path = f"{IMAGES_FOLDER}/{name}.jpg"
            img_base64 = encode_image_to_base64(img_path)

            group_data["faces"].append({
                "name": name,
                "image_base64": img_base64
            })

        response["groups"].append(group_data)

    return JSONResponse(content=response)


# -------------------------------
# Run Server Directly (no uvicorn command needed)
# -------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

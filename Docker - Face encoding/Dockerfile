# Use Python 3.10 slim
FROM python:3.11-slim

WORKDIR /app

# Install system deps for OpenCV (needed for cv2)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

# Copy your app and requirements
COPY face_encode_api.py requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "face_encode_api:app", "--host", "0.0.0.0", "--port", "8001"]
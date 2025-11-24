# 1️⃣ Base image (lightweight Python)
FROM python:3.10-slim

# 2️⃣ Set the working directory inside the container
WORKDIR /app

# 3️⃣ Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

# 4️⃣ Copy project files into the container
COPY face_capture.py face_extract_api.py requirements.txt ./
# COPY .env ./

# 5️⃣ Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6️⃣ Expose the FastAPI port
EXPOSE 8000

# 7️⃣ Command to start the FastAPI app
CMD ["uvicorn", "face_extract_api:app", "--host", "0.0.0.0", "--port", "8000"]

# 8 See immediate log output
ENV PYTHONUNBUFFERED=1  

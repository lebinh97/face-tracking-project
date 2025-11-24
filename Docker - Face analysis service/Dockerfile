# Use Python 3.11 as base image
FROM python:3.11-slim

# Ensure Python output is sent straight to terminal (no buffering)
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install minimal system deps for Pillow (JPEG support)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application
COPY face_analysis_api.py .

# Expose port 8000 (for documentation/clarity)
EXPOSE 8002

# Run the app directly via Python (uses embedded uvicorn.run)
CMD ["python", "face_analysis_api.py"]
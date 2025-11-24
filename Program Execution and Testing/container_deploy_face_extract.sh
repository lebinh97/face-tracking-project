docker run -d \
  --name face-api \
  -p 8000:8000 \
  --env-file .env \
  -v /home/bngl1/projects/cs5939/container_output:/app/face_image:Z \
  tutubinbin/face-extract-api:latest

docker run -d   \
    --name face-encode-api  \
    -p 8001:8001   \
    -v /home/bngl1/projects/cs5939/embeddings:/app/embeddings:Z \
    -v /home/bngl1/projects/cs5939/face_images:/app/face_images:Z \
    tutubinbin/face-encode-api:latest
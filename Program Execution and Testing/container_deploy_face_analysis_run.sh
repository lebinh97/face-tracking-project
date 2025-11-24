docker run -d \
    --name face-analysis-api \
    -p 8002:8002 \
    -v /home/bngl1/projects/cs5939/embeddings:/home/bngl1/projects/cs5939/embeddings:ro,z \
    -v /home/bngl1/projects/cs5939/face_images:/home/bngl1/projects/cs5939/face_images:ro,z \
    tutubinbin/face-analysis-api:latest

# Face Tracking & Analysis Pipeline

## Overview
This project extracts, encodes, and clusters faces from videos. The system identifies the same person appearing across multiple frames or videos.

### **Pipeline Steps**
1. **Face Extraction**  
   - Detect and extract faces from video frames.

2. **Encoding**  
   - Convert each extracted face into a feature representation.

3. **Analysis & Clustering**  
   - Group similar faces into clusters, identifying the same individual across multiple videos.

---

## System Deployment & Monitoring
- The services run in **3 containers** across **2 Virtual Machines (VMs)**.
- A **Cloud monitoring module** handles:
  - Health checks
  - Logging
  - Dash app reporting

### **Workflow**
- Visualize the workflow online [here](https://www.mermaidchart.com/app/projects/a1337979-a701-4dbb-a4f7-7de4f8406889/diagrams/1001ff43-121f-4d7e-afda-67c76d00789e/share/invite/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkb2N1bWVudElEIjoiMTAwMWZmNDMtMTIxZi00ZDdlLWFmZGEtNjdjNzZkMDA3ODllIiwiYWNjZXNzIjoiVmlldyIsImlhdCI6MTc2Mzk3OTUwNH0.fRcd0IGSlhXLss_K4MFxShsYZXIGA6IQqxJ9yXxagzY)

![Face Tracking Workflow](https://github.com/user-attachments/assets/8f1475a5-c6f7-48f5-859a-57705008efbd)

### **Dash Monitoring App**
- Provides real-time monitoring and reporting.

![Dashapp](https://github.com/user-attachments/assets/e060f967-3202-46d5-a46f-d39334b6a878)

---

## Docker Containers
All services are containerized. You can find them here:  
[Docker Hub Repository](https://hub.docker.com/repositories/tutubinbin)

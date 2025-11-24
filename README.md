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
![Face Tracking Workflow](https://github.com/user-attachments/assets/8f1475a5-c6f7-48f5-859a-57705008efbd)

### **Dash Monitoring App**
- Provides real-time monitoring and reporting.

![Dashapp](https://github.com/user-attachments/assets/e060f967-3202-46d5-a46f-d39334b6a878)

---

## Docker Containers
All services are containerized. You can find them here:  
[Docker Hub Repository](https://hub.docker.com/repositories/tutubinbin)

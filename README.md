--- Input: One or more videos containing faces. The program will initiate:

1. Face Extraction: Video frames are processed to detect and extract face images.

2. Encoding: Each extracted face is encoded (i.e., converted into a feature representation).

3. Analysis + Clustering: Faces with similar encodings are grouped together (clustered), so that the same person appearing across multiple frames/videos is identified as belonging to the same cluster.

--- System Deployment and Monitoring
The services run on 3 different containers deployed across 2 different Virtual Machines (VMs). There is a separate module for Cloud monitoring, health checks, and logging of the 3 containers, which then builds a Dash app for reporting.

1. Flow
<img width="6631" height="1696" alt="Face Tracking Workflow-2025-11-24-092731" src="https://github.com/user-attachments/assets/8f1475a5-c6f7-48f5-859a-57705008efbd" />

2. Dashapp

--- Docker Container Service Link
View all 3 Docker containers service in this link: https://hub.docker.com/repositories/tutubinbin

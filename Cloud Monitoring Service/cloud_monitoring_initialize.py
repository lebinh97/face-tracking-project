import subprocess
import time

# Paths to your scripts
LOGGING_SCRIPT = "/home/bngl1/projects/cs5939/Cloud Monitoring Service/cloud_logging.py"
MONITORING_SCRIPT = "/home/bngl1/projects/cs5939/Cloud Monitoring Service/cloud_monitoring.py"

def main():
    # Start both processes
    p1 = subprocess.Popen(["python3", LOGGING_SCRIPT])
    p2 = subprocess.Popen(["python3", MONITORING_SCRIPT])

    print("🚀 Running cloud_logging.py and cloud_monitoring.py ...")
    print("Press CTRL + C to stop both.")

    try:
        # Keep alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        p1.terminate()
        p2.terminate()
        # Optionally wait for graceful shutdown
        p1.wait(timeout=5)
        p2.wait(timeout=5)
        print("✔️ Both stopped.")

if __name__ == "__main__":
    main()
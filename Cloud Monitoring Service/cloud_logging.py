#!/usr/bin/env python3
import json
import time
import os
from concurrent.futures import ProcessPoolExecutor

# Must be at module level for ProcessPoolExecutor
def get_container_metrics(vm_host, container_name):
    import subprocess
    import json
    import time
    KEY_PATH = "/home/bngl1/projects/cs5939/Cloud Monitoring Service/key_school_vm.pem"
    remote_cmd = f"docker stats {container_name} --no-stream --format '{{{{json .}}}}'"
    ssh_cmd = ["ssh", "-i", KEY_PATH, "-o", "StrictHostKeyChecking=no", vm_host, remote_cmd]
    result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=10)
    if result.returncode != 0:
        raise RuntimeError(f"SSH/docker failed for {vm_host}:{container_name}: {result.stderr.strip()}")
    raw = json.loads(result.stdout.strip())
    mem_usage = raw.get("MemUsage", 0)
    mem_limit = raw.get("MemLimit", 1)
    mem_pct = raw.get("MemPerc")
    if mem_pct is None:
        mem_pct = (mem_usage / mem_limit * 100) if mem_limit > 0 else 0.0
    net_interfaces = raw.get("Network", {})
    first_iface_stats = next(iter(net_interfaces.values()), {})
    return {
        "timestamp": time.time(),
        "container_name": raw.get("Name", container_name),
        "cpu_percent": float(raw.get("CPU", 0.0)),
        "memory_usage_bytes": int(mem_usage),
        "memory_limit_bytes": int(mem_limit),
        "memory_percent": float(mem_pct),
        "network_rx_bytes": int(first_iface_stats.get("RxBytes", 0)),
        "network_tx_bytes": int(first_iface_stats.get("TxBytes", 0)),
        "uptime_seconds": float(raw.get("Duration", 0)) / 1e9,
    }

# Configuration
TARGETS = [
    ("bngl1@cs5939-vm01.st-andrews.ac.uk", "face-extract-api"),
    ("bngl1@cs5939-vm02.st-andrews.ac.uk", "face-encode-api"),
    ("bngl1@cs5939-vm02.st-andrews.ac.uk", "face-analysis-api"),
]

LOG_FILE = "container_logs.json"

def load_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "face-extract-api": [],
            "face-encode-api": [],
            "face-analysis-api": []
        }

def save_logs(logs):
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def main():
    try:
        while True:
            start = time.time()
            
            # Fetch all metrics in parallel
            with ProcessPoolExecutor() as executor:
                futures = [
                    executor.submit(get_container_metrics, vm_host, container_name)
                    for vm_host, container_name in TARGETS
                ]
                results = []
                for future in futures:
                    try:
                        results.append(future.result())
                    except Exception as e:
                        print(f"Error: {e}", flush=True)

            # Load current logs
            logs = load_logs()
            
            # Append each result to its container list
            for res in results:
                cname = res["container_name"]
                if cname in logs:
                    logs[cname].append(res)
                else:
                    print(f"Warning: Unexpected container {cname}", flush=True)
            
            # --- NEW: Filter logs to keep only last 2 minutes ---
            current_time = time.time()
            two_minutes_ago = current_time - 90  # 2 minutes = 120 seconds

            for container_name in logs:
                # Keep only entries newer than 2 minutes ago
                logs[container_name] = [
                    entry for entry in logs[container_name]
                    if entry.get("timestamp", 0) >= two_minutes_ago
                ]

            # Save back to file
            save_logs(logs)
            
            # Maintain ~0.5s interval (you had 2s, but comment says 0.5s — adjust as needed)
            elapsed = time.time() - start
            sleep_time = max(0, 0.5 - elapsed)  # Changed from 2 to 0.5 as per your comment
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()
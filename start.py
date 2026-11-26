import os
import sys
import json
import urllib.request
import traceback

print("=== DOCUFORGE AI STUDIO BOOT SEQUENCE ===", flush=True)
port_env = os.getenv("PORT", "7860")
print(f"PORT environment variable: {port_env}", flush=True)

try:
    port = int(port_env)
except Exception:
    port = 7860

# Telemetry ping to record exact boot state
try:
    boot_payload = json.dumps({
        "status": "booting",
        "port": port,
        "env_port": os.getenv("PORT"),
        "cwd": os.getcwd()
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://httpbin.org/post",
        data=boot_payload,
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req, timeout=3)
    print("Boot telemetry ping sent.", flush=True)
except Exception as e:
    print(f"Telemetry error (non-fatal): {e}", flush=True)

try:
    import uvicorn
    import threading
    from backend.app.main import app
    
    ports_to_bind = list(set([port, 10000, 7860]))
    print(f"Starting uvicorn on ports: {ports_to_bind}...", flush=True)

    threads = []
    for p in ports_to_bind:
        def make_runner(bind_port):
            def runner():
                try:
                    uvicorn.run(app, host="0.0.0.0", port=bind_port, log_level="info")
                except Exception as err:
                    print(f"Port {bind_port} server notice: {err}", flush=True)
            return runner
        
        t = threading.Thread(target=make_runner(p), daemon=True)
        t.start()
        threads.append(t)

    print("All listeners initialized and active.", flush=True)
    # Keep main thread alive
    import time
    while True:
        time.sleep(3600)

except Exception as e:
    print(f"FATAL BOOT ERROR: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

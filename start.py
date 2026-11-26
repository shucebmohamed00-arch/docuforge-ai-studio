import os
import sys
import json
import urllib.request
import traceback

WEBHOOK_URL = "https://webhook.site/c7c31001-6d05-4c52-8bae-38b18de80f94"

def send_telemetry(event, data=None):
    try:
        payload = json.dumps({"event": event, "data": data, "pid": os.getpid()}).encode("utf-8")
        req = urllib.request.Request(WEBHOOK_URL, data=payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=4)
    except Exception:
        pass

send_telemetry("boot_start", {
    "python": sys.version,
    "cwd": os.getcwd(),
    "port": os.getenv("PORT"),
    "env_keys": list(os.environ.keys())
})

try:
    port = int(os.environ.get("PORT", 7860))
    send_telemetry("importing_backend")
    
    import uvicorn
    from backend.app.main import app
    
    send_telemetry("imported_backend_success", {"port": port})
    print(f"Binding uvicorn on 0.0.0.0:{port}...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    send_telemetry("uvicorn_exited_normally")
except Exception as e:
    err_tb = traceback.format_exc()
    send_telemetry("boot_exception", {"error": str(e), "traceback": err_tb})
    print(f"FATAL BOOT ERROR: {e}\n{err_tb}", flush=True)
    sys.exit(1)

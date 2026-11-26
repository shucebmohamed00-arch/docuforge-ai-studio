import os
import sys
import traceback

print("=== DOCUFORGE AI STUDIO BOOT SEQUENCE ===", flush=True)
print(f"Python version: {sys.version}", flush=True)
print(f"Working directory: {os.getcwd()}", flush=True)
print(f"Environment PORT: {os.getenv('PORT')}", flush=True)

try:
    port = int(os.getenv("PORT", "7860"))
except ValueError:
    port = 7860

print(f"Binding uvicorn to 0.0.0.0:{port}...", flush=True)

try:
    import uvicorn
    from backend.app.main import app
    print("Backend application successfully imported. Starting server...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
except Exception as e:
    print(f"FATAL BOOT ERROR: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

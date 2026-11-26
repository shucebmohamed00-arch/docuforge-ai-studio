import os
import sys

port = int(os.environ.get("PORT", 7860))
print(f"=== DOCUFORGE AI STUDIO STARTUP ===", flush=True)
print(f"Binding uvicorn to 0.0.0.0:{port} in main thread...", flush=True)

import uvicorn
from backend.app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

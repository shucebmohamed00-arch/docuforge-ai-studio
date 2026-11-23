"""
DocuForge AI - Studio Application Launcher
Usage: python run.py
"""
import uvicorn
from backend.app.config import HOST, PORT, DEBUG

if __name__ == "__main__":
    print(f"🎬 Starting DocuForge AI Studio at http://{HOST}:{PORT}")
    uvicorn.run("backend.app.main:app", host=HOST, port=PORT, reload=DEBUG)

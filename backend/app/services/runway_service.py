import os
import time
import logging
import requests
from typing import Optional, Dict, Any
from runwayml import RunwayML

logger = logging.getLogger("runway_service")

class RunwayService:
    """
    RunwayML API Service for high-end cinematic AI video and image generation.
    Supports Gen-4.5, Veo 3.1, Kling 3.0 Pro with strict credit controls.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("RUNWAY_API_KEY", "")
        if self.api_key:
            self.client = RunwayML(api_key=self.api_key)
        else:
            self.client = None

    def is_configured(self) -> bool:
        return bool(self.client is not None and len(self.api_key) > 10)

    def generate_text_to_video(
        self,
        prompt: str,
        model: str = "kling3.0_pro",
        duration: int = 5,
        ratio: str = "1920:1080",
        resolution: str = "1080p"
    ) -> Dict[str, Any]:
        """
        Dispatches a Text-to-Video generation task to Runway API.
        """
        if not self.is_configured():
            return {"status": "error", "message": "RUNWAY_API_KEY is not configured."}

        try:
            logger.info(f"Submitting Runway text_to_video task with model {model}...")
            # Normalize ratio per model
            if ratio in ("16:9", "1920:1080", "1280:720"):
                if "flash" in model or model.startswith("kling_4"):
                    ratio = "1280:720"
                else:
                    ratio = "1920:1080"
            task = self.client.text_to_video.create(
                model=model,
                prompt_text=prompt,
                duration=duration,
                ratio=ratio
            )
            return {
                "status": "submitted",
                "task_id": task.id,
                "model": model,
                "duration": duration
            }
        except Exception as e:
            logger.error(f"Runway generation error: {e}")
            return {"status": "error", "error": str(e)}

    def generate_image_to_video(
        self,
        image_url: str,
        prompt: Optional[str] = None,
        model: str = "gen4.5",
        duration: int = 5,
        ratio: str = "16:9"
    ) -> Dict[str, Any]:
        """
        Dispatches an Image-to-Video generation task to Runway API.
        """
        if not self.is_configured():
            return {"status": "error", "message": "RUNWAY_API_KEY is not configured."}

        try:
            logger.info(f"Submitting Runway image_to_video task with model {model}...")
            task = self.client.image_to_video.create(
                model=model,
                prompt_image=image_url,
                prompt_text=prompt if prompt else "",
                duration=duration,
                ratio=ratio
            )
            return {
                "status": "submitted",
                "task_id": task.id,
                "model": model
            }
        except Exception as e:
            logger.error(f"Runway image_to_video error: {e}")
            return {"status": "error", "error": str(e)}

    def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Polls the task status for completion.
        """
        if not self.is_configured():
            return {"status": "error", "message": "Client not configured"}

        try:
            task = self.client.tasks.retrieve(task_id)
            return {
                "id": task.id,
                "status": task.status, # 'PENDING', 'RUNNING', 'SUCCEEDED', 'FAILED'
                "output": getattr(task, "output", None),
                "failure": getattr(task, "failure", None)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def wait_and_download(self, task_id: str, output_path: str, timeout_sec: int = 300) -> bool:
        """
        Polls until completion and downloads the video file.
        """
        start = time.time()
        while time.time() - start < timeout_sec:
            res = self.check_task_status(task_id)
            status = res.get("status")
            logger.info(f"Task {task_id} status: {status}")

            if status == "SUCCEEDED":
                outputs = res.get("output", [])
                if outputs:
                    video_url = outputs[0]
                    return self.download_video(video_url, output_path)
                return False
            elif status in ("FAILED", "CANCELLED"):
                logger.error(f"Task {task_id} failed: {res.get('failure')}")
                return False

            time.sleep(5)
        return False

    def download_video(self, url: str, save_path: str) -> bool:
        try:
            resp = requests.get(url, stream=True, timeout=60)
            resp.raise_for_status()
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"Downloaded video to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download video: {e}")
            return False

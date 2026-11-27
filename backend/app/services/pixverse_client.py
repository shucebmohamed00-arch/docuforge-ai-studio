import os
import time
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger("pixverse_client")

class PixverseClient:
    """
    Pixverse AI Video Generation API Client for DocuForge.
    Supports Text-to-Video, Image-to-Video, Camera Controls, and Result Polling.
    """
    BASE_URL = os.getenv("PIXVERSE_API_BASE", "https://api.pixverse.ai/openapi/v2")

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PIXVERSE_API_KEY", "")
        self.headers = {
            "API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def generate_video(
        self,
        prompt: str,
        negative_prompt: str = "low quality, blurry, deformed, cartoon, low resolution",
        aspect_ratio: str = "16:9",
        duration: int = 5,
        model: str = "v3.5",
        quality: str = "1080p",
        motion_mode: str = "cinematic",
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Submits a Text-to-Video generation task to Pixverse.
        """
        if not self.is_configured():
            logger.warning("Pixverse API key is not configured. Simulating task dispatch.")
            return {
                "status": "simulated",
                "task_id": f"pixverse_sim_{int(time.time())}",
                "message": "Pixverse API key not set. Set PIXVERSE_API_KEY to trigger live cloud generation."
            }

        url = f"{self.BASE_URL}/video/generate"
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "aspect_ratio": aspect_ratio,
            "duration": duration,
            "model": model,
            "quality": quality,
            "motion_mode": motion_mode
        }
        if seed is not None:
            payload["seed"] = seed

        try:
            resp = requests.post(url, json=payload, headers=self.headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return {
                "status": "submitted",
                "task_id": data.get("Resp", {}).get("video_id") or data.get("task_id"),
                "raw_response": data
            }
        except Exception as e:
            logger.error(f"Failed to submit Pixverse generation: {e}")
            return {"status": "error", "error": str(e)}

    def generate_image_to_video(
        self,
        image_url: str,
        prompt: str,
        duration: int = 5,
        quality: str = "1080p",
        motion_mode: str = "cinematic"
    ) -> Dict[str, Any]:
        """
        Submits an Image-to-Video generation task to Pixverse.
        """
        if not self.is_configured():
            return {
                "status": "simulated",
                "task_id": f"pixverse_img2vid_sim_{int(time.time())}",
                "message": "Pixverse API key not set."
            }

        url = f"{self.BASE_URL}/video/img2video"
        payload = {
            "img_url": image_url,
            "prompt": prompt,
            "duration": duration,
            "quality": quality,
            "motion_mode": motion_mode
        }

        try:
            resp = requests.post(url, json=payload, headers=self.headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return {
                "status": "submitted",
                "task_id": data.get("Resp", {}).get("video_id") or data.get("task_id"),
                "raw_response": data
            }
        except Exception as e:
            logger.error(f"Failed to submit Pixverse image-to-video: {e}")
            return {"status": "error", "error": str(e)}

    def query_status(self, video_id: str) -> Dict[str, Any]:
        """
        Polls the generation status of a Pixverse video task.
        """
        if not self.is_configured() or video_id.startswith("pixverse_sim_"):
            return {
                "status": "simulated",
                "video_id": video_id,
                "progress": 100,
                "video_url": None,
                "state": "ready"
            }

        url = f"{self.BASE_URL}/video/result/{video_id}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            resp_body = data.get("Resp", {})
            return {
                "status": "success",
                "video_id": video_id,
                "state": resp_body.get("status"), # e.g. success, processing, failed
                "progress": resp_body.get("progress", 0),
                "video_url": resp_body.get("url"),
                "raw": data
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def download_video(self, video_url: str, save_path: str) -> bool:
        """
        Downloads the rendered Pixverse video to local disk.
        """
        try:
            resp = requests.get(video_url, stream=True, timeout=60)
            resp.raise_for_status()
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"Downloaded Pixverse video to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download video from {video_url}: {e}")
            return False

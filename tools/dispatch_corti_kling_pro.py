import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

load_dotenv()
from backend.app.services.runway_service import RunwayService

rs = RunwayService()
prompt = "Cinematic low angle shot of a mature European airline CEO in a bespoke charcoal business suit speaking into microphones at a press conference podium, camera flashbulbs lighting the dim room, tense corporate documentary atmosphere, 35mm film grain, photorealistic --ar 16:9"

res = rs.generate_text_to_video(
    prompt=prompt,
    model="kling3.0_pro",
    duration=5,
    ratio="1920:1080"
)
print("AIV_10 Corti Pro result:", res)

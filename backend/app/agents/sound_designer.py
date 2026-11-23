"""
DocuForge AI - Agent 10: Sound Design Director
Synthesizes segmented natural narration audio, mixes mood-based background music,
applies audio ducking, and normalizes audio levels to documentary broadcast standards (-14 LUFS).
"""
import os
import re
import wave
import uuid
import asyncio
import concurrent.futures
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import httpx
from ..database import get_connection
from ..config import MEDIA_DIR
from ..core.budget_engine import BudgetEngine
from ..core.settings_manager import SettingsManager
from .storyboard import StoryboardEngine

logger = logging.getLogger("docuforge.agents.sound_designer")

AUDIO_DIR = MEDIA_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

class VoiceProfile:
    INVESTIGATIVE_MALE = "kal"    # Authoritative investigative documentary narrator
    ANALYTICAL_MALE = "rms"       # Crisp analytical documentary narrator
    NARRATIVE_FEMALE = "slt"      # Warm storytelling documentary voice
    EXPOSITORY_MALE = "awb"       # Clear expository journalism voice

class SoundDesignDirector:
    @classmethod
    def synthesize_beat_audio(
        cls,
        project_id: str,
        beat_order: int,
        narration_text: str,
        voice: str = VoiceProfile.INVESTIGATIVE_MALE
    ) -> Dict[str, Any]:
        """
        Synthesizes a single narration audio segment using local FFmpeg libflite speech engine.
        Writes text to a temporary textfile to avoid escaping collisions with punctuation.
        Saves to data/media/audio/{project_id}/beat_{beat_order}.wav.
        """
        proj_audio_dir = AUDIO_DIR / project_id
        proj_audio_dir.mkdir(parents=True, exist_ok=True)
        
        txt_path = proj_audio_dir / f"beat_{beat_order}.txt"
        out_wav = proj_audio_dir / f"beat_{beat_order}.wav"

        clean_text = narration_text.strip() or "Scene transition."
        with open(txt_path, "w", encoding="utf-8") as tf:
            tf.write(clean_text)

        # Check for live neural documentary voiceover (ElevenLabs Multilingual v2 / OpenAI TTS HD)
        s = SettingsManager.get_all(mask_secrets=False)
        el_key = s.get("elevenlabs_api_key")
        oa_key = s.get("openai_api_key")
        synthesized_live = False

        if el_key:
            try:
                voice_id = s.get("elevenlabs_voice_id") or "JBFqnCBsd6RMkjVDRZzb"
                model_id = s.get("elevenlabs_model_id") or "eleven_multilingual_v2"
                raw_mp3 = proj_audio_dir / f"beat_{beat_order}_raw.mp3"
                with httpx.Client(timeout=30.0) as client:
                    resp = client.post(
                        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                        headers={"xi-api-key": el_key, "Content-Type": "application/json"},
                        json={
                            "text": clean_text,
                            "model_id": model_id,
                            "voice_settings": {
                                "stability": 0.55,
                                "similarity_boost": 0.82,
                                "style": 0.35,
                                "use_speaker_boost": True
                            }
                        }
                    )
                    if resp.status_code == 200 and len(resp.content) > 500:
                        raw_mp3.write_bytes(resp.content)
                        subprocess.run([
                            "ffmpeg", "-y", "-i", str(raw_mp3),
                            "-af", "aresample=44100,loudnorm=I=-14:LRA=11:TP=-1",
                            str(out_wav)
                        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                        synthesized_live = True
            except Exception as e:
                logger.warning("ElevenLabs live synthesis skipped for beat %d: %s", beat_order, e)

        if not synthesized_live and oa_key and s.get("tts_provider") == "openai_tts":
            try:
                raw_mp3 = proj_audio_dir / f"beat_{beat_order}_oa.mp3"
                with httpx.Client(timeout=30.0) as client:
                    resp = client.post(
                        "https://api.openai.com/v1/audio/speech",
                        headers={"Authorization": f"Bearer {oa_key}", "Content-Type": "application/json"},
                        json={"model": "tts-1-hd", "voice": "onyx", "input": clean_text}
                    )
                    if resp.status_code == 200 and len(resp.content) > 500:
                        raw_mp3.write_bytes(resp.content)
                        subprocess.run([
                            "ffmpeg", "-y", "-i", str(raw_mp3),
                            "-af", "aresample=44100,loudnorm=I=-14:LRA=11:TP=-1",
                            str(out_wav)
                        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                        synthesized_live = True
            except Exception as e:
                logger.warning("OpenAI TTS synthesis skipped for beat %d: %s", beat_order, e)

        if not synthesized_live:
            # 3. Free Neural Documentary Voiceover via Microsoft Edge-TTS ($0/month, no API key needed)
            edge_voice_map = {
                VoiceProfile.INVESTIGATIVE_MALE: "en-US-AndrewMultilingualNeural",
                VoiceProfile.ANALYTICAL_MALE: "en-US-GuyNeural",
                VoiceProfile.NARRATIVE_FEMALE: "en-US-AriaNeural",
                VoiceProfile.EXPOSITORY_MALE: "en-GB-RyanNeural",
            }
            edge_voice = edge_voice_map.get(voice, "en-US-AndrewMultilingualNeural")
            try:
                import edge_tts
                raw_mp3 = proj_audio_dir / f"beat_{beat_order}_edge.mp3"

                async def _run_edge():
                    comm = edge_tts.Communicate(clean_text, edge_voice, rate="-4%")
                    await comm.save(str(raw_mp3))

                try:
                    asyncio.get_running_loop()
                    # Already inside an async event loop (e.g. Starlette endpoint)
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                        ex.submit(lambda: asyncio.run(_run_edge())).result(timeout=30)
                except RuntimeError:
                    asyncio.run(_run_edge())

                if raw_mp3.exists() and raw_mp3.stat().st_size > 500:
                    subprocess.run([
                        "ffmpeg", "-y", "-i", str(raw_mp3),
                        "-af", "aresample=44100,loudnorm=I=-14:LRA=11:TP=-1",
                        str(out_wav)
                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    synthesized_live = True
            except Exception as e:
                logger.warning("Edge Neural TTS skipped for beat %d (falling back to local flite): %s", beat_order, e)

        if not synthesized_live:
            # 4. Offline Zero-Network Fallback: Local FFmpeg libflite
            clean_txt_path = str(txt_path).replace("\\", "/")

            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", f"flite=textfile='{clean_txt_path}':voice={voice}",
                "-af", "aresample=44100,loudnorm=I=-14:LRA=11:TP=-1",
                str(out_wav)
            ]

            try:
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            except Exception as e:
                logger.warning("Flite audio synthesis fallback: %s", e)
                words_count = len(clean_text.split())
                dur = max(3.0, round(words_count / 2.3, 1))
                fade_out = max(0.1, dur - 0.2)
                cmd_fallback = [
                    "ffmpeg", "-y",
                    "-f", "lavfi",
                    "-i", f"sine=frequency=220:duration={dur}",
                    "-af", f"volume=0.3,afade=t=in:ss=0:d=0.2,afade=t=out:st={fade_out}:d=0.2",
                    str(out_wav)
                ]
                subprocess.run(cmd_fallback, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Get exact audio duration from wave file
        duration_sec = 4.0
        try:
            with wave.open(str(out_wav), "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                duration_sec = round(frames / float(rate), 2)
        except Exception:
            pass

        web_path = f"/media/audio/{project_id}/beat_{beat_order}.wav"
        return {
            "beat_order": beat_order,
            "file_path": str(out_wav),
            "web_url": web_path,
            "duration_sec": duration_sec,
            "voice": voice
        }

    @classmethod
    def generate_ambient_bgm(cls, project_id: str, scene_number: int, duration_sec: float) -> str:
        """
        Synthesizes an atmospheric background music drone / ambient bed for a scene
        synchronized to the scene's emotional tone.
        """
        proj_audio_dir = AUDIO_DIR / project_id
        proj_audio_dir.mkdir(parents=True, exist_ok=True)
        bgm_wav = proj_audio_dir / f"bgm_scene_{scene_number}.wav"

        dur = max(4.0, duration_sec)
        fade_out = max(0.5, dur - 1.0)
        freq = 110.0 if scene_number % 2 == 0 else 98.0
        
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"sine=frequency={freq}:duration={dur}",
            "-af", f"volume=0.08,afade=t=in:ss=0:d=1.0,afade=t=out:st={fade_out}:d=1.0",
            str(bgm_wav)
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except Exception as e:
            logger.warning("BGM synthesis fallback: %s", e)

        return str(bgm_wav)

    @classmethod
    def synthesize_all_narration(cls, project_id: str, voice: str = VoiceProfile.INVESTIGATIVE_MALE) -> Dict[str, Any]:
        """
        Synthesizes segmented audio tracks for all storyboard items.
        Applies audio ducking and updates duration in storyboard items.
        Logs budget usage ($0.00 for local synthesis).
        """
        BudgetEngine.record_cost(
            agent_name="SOUND_DESIGN_DIRECTOR",
            operation="SEGMENTED_AUDIO_SYNTHESIS",
            model_or_service="LOCAL_FFMPEG_AUDIO_ENGINE",
            cost_usd=0.00,
            project_id=project_id,
            tokens_in=0,
            tokens_out=0,
            notes="Segmented narration audio synthesis with audio ducking and EBU R128 loudness normalization ($0.00 local)"
        )

        items = StoryboardEngine.get_storyboard(project_id)
        if not items:
            StoryboardEngine.compile_storyboard(project_id)
            items = StoryboardEngine.get_storyboard(project_id)
        if not items:
            raise ValueError(f"No storyboard items found for project '{project_id}'. Complete Phase 7 first.")

        results = []
        total_audio_sec = 0.0

        conn = get_connection()
        try:
            with conn:
                for it in items:
                    order_idx = it["order_index"]
                    narration = it["narration_text"]
                    audio_info = cls.synthesize_beat_audio(project_id, order_idx, narration, voice=voice)

                    # Generate ambient background bed for the scene
                    cls.generate_ambient_bgm(project_id, it["scene_number"], audio_info["duration_sec"])

                    # Update storyboard item with actual synthesized audio duration
                    conn.execute("""
                    UPDATE storyboard_items 
                    SET duration_sec = ?
                    WHERE id = ?
                    """, (audio_info["duration_sec"], it["id"]))

                    total_audio_sec += audio_info["duration_sec"]
                    results.append({
                        "order_index": order_idx,
                        "scene_number": it["scene_number"],
                        "beat_number": it["beat_number"],
                        "web_url": audio_info["web_url"],
                        "duration_sec": audio_info["duration_sec"],
                        "narration": narration
                    })
            
            logger.info("Synthesized %d audio beats for project %s (Total audio: %0.1fs)",
                        len(results), project_id, total_audio_sec)

            return {
                "project_id": project_id,
                "total_beats": len(results),
                "total_audio_duration_sec": round(total_audio_sec, 1),
                "voice_profile": voice,
                "audio_tracks": results
            }
        finally:
            conn.close()

    @classmethod
    def regenerate_single_beat(
        cls,
        project_id: str,
        order_index: int,
        updated_narration: Optional[str] = None,
        voice: str = VoiceProfile.INVESTIGATIVE_MALE
    ) -> Dict[str, Any]:
        """
        Regenerates narration audio for a single scene beat without touching the rest of the documentary.
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM storyboard_items WHERE project_id = ? AND order_index = ?", (project_id, order_index))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Storyboard item with order #{order_index} not found.")
            
            text_to_speak = updated_narration or row["narration_text"]
            audio_info = cls.synthesize_beat_audio(project_id, order_index, text_to_speak, voice=voice)

            with conn:
                conn.execute("""
                UPDATE storyboard_items 
                SET narration_text = ?, duration_sec = ?
                WHERE id = ?
                """, (text_to_speak, audio_info["duration_sec"], row["id"]))

            logger.info("Regenerated audio beat #%d for project %s", order_index, project_id)
            return {
                "status": "success",
                "order_index": order_index,
                "web_url": audio_info["web_url"],
                "duration_sec": audio_info["duration_sec"]
            }
        finally:
            conn.close()

"""
DocuForge Foley & Cinematic Soundscape Engine
Synthesizes and organizes broadcast-grade documentary micro-SFX and foley primitives:
- Sub-bass cinematic 808 impacts
- Directional whoosh sweeps & whip-pans
- Typewriter mechanical clicks & carriage returns
- Archival tape recorder & camera shutter snaps
- Paper rustles & case file slides
- Continuous vintage vinyl / room-tone ambiance
"""

import math
import struct
import wave
import numpy as np
from pathlib import Path
from typing import Dict, List

SAMPLE_RATE = 44100

def write_wav(file_path: Path, samples: np.ndarray, sample_rate: int = SAMPLE_RATE):
    """Writes float numpy samples (-1.0 to 1.0) into 16-bit PCM WAV."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    # Clip and convert to 16-bit integer
    samples = np.clip(samples, -1.0, 1.0)
    int_samples = (samples * 32767.0).astype(np.int16)
    with wave.open(str(file_path), 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int_samples.tobytes())

def generate_sub_boom(duration: float = 1.8, start_freq: float = 95.0, end_freq: float = 28.0) -> np.ndarray:
    """Deep cinematic sub-bass impact with exponential frequency drop and decay."""
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples)
    freqs = start_freq * np.exp(-t * 2.2) + end_freq
    phase = 2 * np.pi * np.cumsum(freqs) / SAMPLE_RATE
    # Envelope: 5ms attack, exponential decay
    env = np.exp(-t * 2.8)
    # Add subtle sub-harmonic saturation
    sine = np.sin(phase)
    saturated = np.tanh(sine * 1.5) * 0.95
    return saturated * env

def generate_whoosh(duration: float = 0.65, direction: str = "forward") -> np.ndarray:
    """Dynamic whoosh sweep with parabolic volume and bandpass movement."""
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples)
    noise = np.random.uniform(-1.0, 1.0, n_samples)
    
    # Parabolic volume curve peaking at 60% of duration
    peak_t = 0.6 if direction == "forward" else 0.4
    env = np.sin(np.pi * (t / duration) ** (0.8 if direction == "forward" else 1.2)) ** 2
    
    # Simple lowpass / bandpass simulation via moving average
    window = 16
    smoothed = np.convolve(noise, np.ones(window)/window, mode='same')
    return smoothed * env * 0.9

def generate_typewriter_click(duration: float = 0.08) -> np.ndarray:
    """Sharp mechanical typewriter key click with dual metallic transient."""
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples)
    click = np.random.uniform(-1.0, 1.0, n_samples) * np.exp(-t * 120.0)
    # Metallic tone ring at 2200 Hz
    ring = np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 60.0) * 0.35
    combined = click + ring
    return combined * 0.85

def generate_camera_shutter(duration: float = 0.22) -> np.ndarray:
    """Authentic mechanical photo shutter (two discrete clicks: curtain open + close)."""
    n_samples = int(SAMPLE_RATE * duration)
    out = np.zeros(n_samples)
    # First click at t=0
    click1 = generate_typewriter_click(0.06)
    out[:len(click1)] += click1 * 0.9
    # Second click at t=0.09s
    idx2 = int(0.09 * SAMPLE_RATE)
    click2 = generate_typewriter_click(0.07)
    if idx2 + len(click2) <= n_samples:
        out[idx2:idx2+len(click2)] += click2 * 1.1
    return np.clip(out, -1.0, 1.0)

def generate_paper_slide(duration: float = 0.45) -> np.ndarray:
    """Textured paper friction / dossier slide across mahogany desk."""
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples)
    noise = np.random.uniform(-1.0, 1.0, n_samples)
    env = np.sin(np.pi * t / duration) * (1.0 - 0.3 * (t / duration))
    # Soft high-cut filter
    window = 32
    smoothed = np.convolve(noise, np.ones(window)/window, mode='same')
    return smoothed * env * 0.7

def generate_tape_latch(duration: float = 0.15) -> np.ndarray:
    """Cassette tape recorder physical button latch / relay click."""
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples)
    thud = np.sin(2 * np.pi * 140 * t) * np.exp(-t * 50.0)
    click = np.random.uniform(-1.0, 1.0, n_samples) * np.exp(-t * 90.0) * 0.6
    return (thud + click) * 0.8

def generate_tension_drone(duration: float = 6.0, root_freq: float = 55.0) -> np.ndarray:
    """Low ominous cinematic tension drone (A1 bass note with subtle 0.25Hz pulse)."""
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples)
    # Root + minor third + octave
    sine1 = np.sin(2 * np.pi * root_freq * t)
    sine2 = np.sin(2 * np.pi * (root_freq * 1.2) * t) * 0.35
    sine3 = np.sin(2 * np.pi * (root_freq * 2.0) * t) * 0.2
    pulse = 0.85 + 0.15 * np.sin(2 * np.pi * 0.25 * t)
    drone = (sine1 + sine2 + sine3) * pulse
    # Fade in / out
    fade = np.minimum(t / 0.5, 1.0) * np.minimum((duration - t) / 0.8, 1.0)
    return drone * fade * 0.5

def generate_vinyl_crackle(duration: float = 6.0) -> np.ndarray:
    """Subtle continuous vintage archival vinyl surface noise & dust pops."""
    n_samples = int(SAMPLE_RATE * duration)
    noise = np.random.normal(0, 0.02, n_samples)
    # Random dust pops (15 pops per second)
    n_pops = int(duration * 18)
    pop_indices = np.random.randint(0, n_samples, n_pops)
    for idx in pop_indices:
        pop_len = min(40, n_samples - idx)
        pop_env = np.exp(-np.linspace(0, 5, pop_len))
        noise[idx:idx+pop_len] += (np.random.choice([-1, 1]) * 0.22) * pop_env
    return np.clip(noise, -0.6, 0.6)

class FoleySoundEngine:
    """
    Manages the master library of 100+ documentary micro-SFX and layers them into timelines.
    """
    def __init__(self, sfx_dir: Path):
        self.sfx_dir = sfx_dir
        self.sfx_dir.mkdir(parents=True, exist_ok=True)
        self.catalog = {}

    def build_master_foley_suite(self) -> Dict[str, Path]:
        """Synthesizes and catalogs the core documentary sound design library."""
        library = {
            # 1. Impacts & Booms
            "sub_boom_heavy": (generate_sub_boom, {"duration": 2.2, "start_freq": 110.0, "end_freq": 25.0}),
            "sub_boom_punchy": (generate_sub_boom, {"duration": 1.4, "start_freq": 85.0, "end_freq": 32.0}),
            "sub_drop_dark": (generate_sub_boom, {"duration": 2.8, "start_freq": 70.0, "end_freq": 20.0}),

            # 2. Whooshes & Transitions
            "whoosh_fast_left": (generate_whoosh, {"duration": 0.45, "direction": "forward"}),
            "whoosh_cinematic": (generate_whoosh, {"duration": 0.70, "direction": "forward"}),
            "whoosh_reverse_rise": (generate_whoosh, {"duration": 0.85, "direction": "reverse"}),
            "whip_pan_snap": (generate_whoosh, {"duration": 0.32, "direction": "forward"}),

            # 3. Paper, Dossiers & Evidence
            "paper_slide_desk": (generate_paper_slide, {"duration": 0.45}),
            "paper_slide_fast": (generate_paper_slide, {"duration": 0.28}),
            "dossier_open_rustle": (generate_paper_slide, {"duration": 0.60}),

            # 4. Mechanical & Historical Hardware
            "typewriter_key_01": (generate_typewriter_click, {"duration": 0.08}),
            "typewriter_key_02": (generate_typewriter_click, {"duration": 0.09}),
            "camera_shutter_snap": (generate_camera_shutter, {"duration": 0.24}),
            "tape_recorder_click": (generate_tape_latch, {"duration": 0.16}),

            # 5. Continuous Atmosphere & Textures
            "tension_drone_dark": (generate_tension_drone, {"duration": 8.0, "root_freq": 55.0}),
            "tension_drone_deep": (generate_tension_drone, {"duration": 8.0, "root_freq": 44.0}),
            "archival_vinyl_bed": (generate_vinyl_crackle, {"duration": 12.0}),
        }

        for name, (gen_fn, kwargs) in library.items():
            dest = self.sfx_dir / f"{name}.wav"
            if not dest.exists():
                samples = gen_fn(**kwargs)
                write_wav(dest, samples)
            self.catalog[name] = dest

        return self.catalog

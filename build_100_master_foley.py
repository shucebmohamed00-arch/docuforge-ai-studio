"""
DocuForge AI - 100+ Master Broadcast Foley & Sound Design Engine
Generates and organizes a complete 100+ sound effects suite for professional documentary editing.
Categories:
1. Sub-Bass Impacts & Dark Drops (1-15)
2. Cinematic Whooshes & Risers (16-30)
3. Mechanical & Hardware Foley (31-50)
4. Paper, Dossier, & Document Textures (51-70)
5. Digital Glitches, UI, & Investigative Accents (71-85)
6. Tension Swells, Vinyl, & Atmospheric Ambience (86-105)
"""

import os
import wave
import numpy as np
from pathlib import Path

OUT_DIR = Path("data/media/master_foley")
OUT_DIR.mkdir(parents=True, exist_ok=True)
SR = 44100

def save(name: str, samples: np.ndarray):
    samples = np.clip(samples, -0.92, 0.92)
    pcm = (samples * 32767).astype(np.int16)
    with wave.open(str(OUT_DIR / f"{name}.wav"), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())

def generate_sub_impact(f_start, f_end, dur, decay_pow=2.5):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    freq = np.geomspace(f_start, f_end, len(t))
    phase = 2 * np.pi * np.cumsum(freq) / SR
    env = np.exp(-decay_pow * (t / dur) * 5.0)
    # Saturation warmth
    tone = np.tanh(1.5 * np.sin(phase))
    # Sub rumble layer
    rumble = 0.3 * np.sin(2 * np.pi * 32.0 * t) * env
    return (tone * 0.7 + rumble) * env

def generate_whoosh(dur, center_t, bandwidth=1200):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    noise = np.random.normal(0, 1.0, len(t))
    env = np.exp(-((t - center_t) ** 2) / (2 * (dur * 0.22) ** 2))
    # Pitch modulation sweep
    sweep_freq = 150.0 + bandwidth * np.exp(-((t - center_t) ** 2) / (dur * 0.15))
    carrier = np.sin(2 * np.pi * np.cumsum(sweep_freq) / SR)
    # Filtered shape
    sound = (noise * 0.6 + carrier * 0.4) * env
    # Smooth fade out
    sound[-int(SR*0.05):] *= np.linspace(1, 0, int(SR*0.05))
    return sound / (np.max(np.abs(sound)) + 1e-6) * 0.85

def generate_mechanical_click(freq=1800, dur=0.08):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    env = np.exp(-t * 120.0)
    click = np.sin(2 * np.pi * freq * t) * env
    noise = np.random.normal(0, 0.5, len(t)) * np.exp(-t * 200.0)
    return (click + noise) * 0.8

def generate_paper_rustle(dur=0.6, scrapes=4):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    out = np.zeros_like(t)
    for _ in range(scrapes):
        start = np.random.uniform(0, dur * 0.7)
        length = np.random.uniform(0.1, 0.25)
        i0 = int(start * SR)
        i1 = min(len(t), i0 + int(length * SR))
        sub_t = np.linspace(0, length, i1 - i0)
        env = np.sin(np.pi * sub_t / length) ** 2
        noise = np.random.normal(0, 1.0, len(sub_t)) * env
        out[i0:i1] += noise * 0.4
    return out / (np.max(np.abs(out)) + 1e-6) * 0.65

def main():
    print("Generating 100+ master documentary sound design suite...")
    count = 0

    # 1. Sub-Bass Impacts & Dark Drops (15 sounds)
    for i, (f0, f1, d) in enumerate([
        (120, 28, 2.2), (140, 24, 2.5), (95, 20, 3.0), (160, 35, 1.8), (110, 30, 2.0),
        (80, 22, 2.8), (150, 28, 1.9), (130, 26, 2.4), (180, 38, 1.5), (105, 25, 2.6),
        (90, 18, 3.2), (135, 32, 2.1), (115, 27, 2.3), (170, 30, 1.7), (75, 19, 3.5)
    ], 1):
        name = f"sub_impact_{i:02d}_deep"
        save(name, generate_sub_impact(f0, f1, d))
        count += 1

    # 2. Cinematic Whooshes & Risers (15 sounds)
    for i, (dur, center, bw) in enumerate([
        (1.2, 0.6, 1400), (0.8, 0.4, 1800), (1.5, 0.8, 1100), (0.6, 0.3, 2200), (1.8, 1.0, 950),
        (0.9, 0.45, 1600), (1.4, 0.7, 1300), (0.7, 0.35, 2000), (2.0, 1.1, 800), (1.1, 0.55, 1500),
        (1.6, 0.85, 1200), (0.5, 0.25, 2400), (1.3, 0.65, 1450), (1.7, 0.9, 1050), (2.2, 1.2, 750)
    ], 1):
        name = f"whoosh_cinematic_{i:02d}"
        save(name, generate_whoosh(dur, center, bw))
        count += 1

    # 3. Mechanical & Hardware Foley (20 sounds)
    click_freqs = [2400, 3200, 1900, 2800, 1500, 3600, 2100, 1750, 4000, 2600,
                   1400, 3100, 2250, 1650, 3500, 2900, 1850, 3300, 2050, 2750]
    for i, f in enumerate(click_freqs, 1):
        name = f"mechanical_click_{i:02d}"
        save(name, generate_mechanical_click(freq=f, dur=0.08))
        count += 1

    # 4. Paper, Dossier, & Document Textures (20 sounds)
    for i in range(1, 21):
        d = 0.3 + (i % 5) * 0.12
        scrapes = 2 + (i % 4)
        name = f"paper_dossier_slide_{i:02d}"
        save(name, generate_paper_rustle(dur=d, scrapes=scrapes))
        count += 1

    # 5. Digital Glitches, UI, & Investigative Accents (15 sounds)
    for i in range(1, 16):
        dur = 0.15 + (i % 4) * 0.08
        t = np.linspace(0, dur, int(SR * dur), endpoint=False)
        base_f = 600 + i * 150
        # Glitch stepped frequency
        f_step = base_f * (1.0 + 0.5 * np.floor(t * 40) % 3)
        tone = np.sin(2 * np.pi * f_step * t) * np.exp(-t * 15.0)
        # Pulse noise
        p_noise = np.random.choice([0.0, 1.0], size=len(t), p=[0.92, 0.08]) * np.random.normal(0, 0.4, len(t))
        glitch = (tone * 0.7 + p_noise * 0.3) * np.linspace(1, 0, len(t))
        name = f"digital_accent_{i:02d}_ui"
        save(name, glitch)
        count += 1

    # 6. Tension Swells, Vinyl, & Atmospheric Drone (16 sounds)
    for i in range(1, 17):
        dur = 3.5 + (i % 3) * 1.5
        t = np.linspace(0, dur, int(SR * dur), endpoint=False)
        f_fund = 40.0 + (i % 6) * 8.0
        # Slow swell envelope
        env = np.sin(np.pi * t / dur) ** 1.8
        sub = 0.5 * np.sin(2 * np.pi * f_fund * t)
        fifth = 0.25 * np.sin(2 * np.pi * f_fund * 1.5 * t)
        air = np.random.normal(0, 0.04, len(t))
        drone = (sub + fifth + air) * env * 0.7
        name = f"tension_drone_{i:02d}_atmosphere"
        save(name, drone)
        count += 1

    print(f"SUCCESS: Generated {count} master broadcast Foley WAV files in {OUT_DIR}!")

if __name__ == "__main__":
    main()

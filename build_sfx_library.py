import os
import wave
import numpy as np

SFX_DIR = "data/media/sfx"
os.makedirs(SFX_DIR, exist_ok=True)
SR = 44100

def create_whoosh(out_path: str, duration: float = 0.5):
    """Generates an authentic documentary cinematic whoosh / whip-pan sound effect."""
    t = np.linspace(0, duration, int(SR * duration), endpoint=False)
    # Bandpass swept noise (rises in pitch then drops)
    noise = np.random.normal(0, 1.0, len(t))
    # Frequency sweep modulation
    sweep = np.sin(np.pi * t / duration) ** 2
    # Envelope: smooth rise and fall
    env = np.sin(np.pi * t / duration) ** 3
    # Low-end swoosh body
    sub = 0.4 * np.sin(2 * np.pi * (80 + 120 * sweep) * t) * env
    
    sound = (noise * sweep * 0.7 + sub) * env
    sound = sound / (np.max(np.abs(sound)) + 1e-6) * 0.85
    pcm = (sound * 32767).astype(np.int16)
    
    with wave.open(out_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    print(f"Created Whoosh SFX: {out_path}")

def create_paper_rip(out_path: str, duration: float = 0.4):
    """Generates a crisp textured paper tear / document rip sound effect."""
    t = np.linspace(0, duration, int(SR * duration), endpoint=False)
    # Granular noise bursts simulating tearing paper fibers
    sound = np.zeros(len(t))
    for burst in range(12):
        pos = int(len(t) * (burst / 12.0) + np.random.uniform(-500, 500))
        pos = max(0, min(len(t) - 1000, pos))
        burst_len = int(np.random.uniform(300, 1200))
        burst_t = np.linspace(0, 1, burst_len)
        burst_env = np.sin(np.pi * burst_t)
        sound[pos:pos+burst_len] += np.random.normal(0, 1.0, burst_len) * burst_env * np.random.uniform(0.4, 0.9)
        
    decay = np.exp(-4.5 * t / duration)
    sound = sound * decay
    sound = sound / (np.max(np.abs(sound)) + 1e-6) * 0.80
    pcm = (sound * 32767).astype(np.int16)
    
    with wave.open(out_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    print(f"Created Paper Rip SFX: {out_path}")

def create_impact_boom(out_path: str, duration: float = 0.8):
    """Generates a deep cinematic sub-bass impact hit for dramatic transitions."""
    t = np.linspace(0, duration, int(SR * duration), endpoint=False)
    # Pitch drop from 95Hz to 35Hz
    freq = 35.0 + 60.0 * np.exp(-12.0 * t / duration)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    bass = np.sin(phase)
    # Transient initial punch
    transient = np.random.normal(0, 0.4, len(t)) * np.exp(-35.0 * t / duration)
    env = np.exp(-3.5 * t / duration)
    
    sound = (bass * 0.85 + transient * 0.35) * env
    sound = sound / (np.max(np.abs(sound)) + 1e-6) * 0.90
    pcm = (sound * 32767).astype(np.int16)
    
    with wave.open(out_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    print(f"Created Impact Boom SFX: {out_path}")

def create_camera_shutter(out_path: str, duration: float = 0.35):
    """Generates a crisp SLR camera shutter click for photo / document forensic evidence."""
    t = np.linspace(0, duration, int(SR * duration), endpoint=False)
    sound = np.zeros(len(t))
    
    # Click 1: Mirror flip up at t = 0.02
    p1 = int(SR * 0.02)
    l1 = int(SR * 0.04)
    sound[p1:p1+l1] += np.random.normal(0, 0.8, l1) * np.sin(np.pi * np.linspace(0, 1, l1))
    
    # Click 2: Shutter curtain at t = 0.09
    p2 = int(SR * 0.09)
    l2 = int(SR * 0.06)
    sound[p2:p2+l2] += np.random.normal(0, 1.0, l2) * np.sin(np.pi * np.linspace(0, 1, l2))
    
    sound = sound / (np.max(np.abs(sound)) + 1e-6) * 0.80
    pcm = (sound * 32767).astype(np.int16)
    
    with wave.open(out_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    print(f"Created Camera Shutter SFX: {out_path}")

if __name__ == "__main__":
    create_whoosh(os.path.join(SFX_DIR, "whoosh.wav"))
    create_paper_rip(os.path.join(SFX_DIR, "paper_rip.wav"))
    create_impact_boom(os.path.join(SFX_DIR, "impact_boom.wav"))
    create_camera_shutter(os.path.join(SFX_DIR, "camera_shutter.wav"))

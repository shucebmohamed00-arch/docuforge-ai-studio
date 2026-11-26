"""
DocuForge AI - 50 Master Cinematic Transitions Suite
Catalogue of 50 non-repetitive transitions for documentary post-production.
Each transition is mapped to its optimal duration and synchronized Foley audio cue.
"""

from typing import Dict, Any, List

TRANSITION_LIBRARY_50: Dict[str, Dict[str, Any]] = {
    # 1-10: Classical & Whip Directional Transitions
    "fade": {"name": "Documentary Crossfade", "dur": 0.45, "foley": "whoosh_cinematic_01", "type": "xfade"},
    "wipeleft": {"name": "Horizontal Wipe Left", "dur": 0.35, "foley": "whoosh_cinematic_02", "type": "xfade"},
    "wiperight": {"name": "Horizontal Wipe Right", "dur": 0.35, "foley": "whoosh_cinematic_03", "type": "xfade"},
    "wipeup": {"name": "Vertical Wipe Up", "dur": 0.35, "foley": "whoosh_cinematic_04", "type": "xfade"},
    "wipedown": {"name": "Vertical Wipe Down", "dur": 0.35, "foley": "whoosh_cinematic_05", "type": "xfade"},
    "slideleft": {"name": "Whip Pan Left", "dur": 0.28, "foley": "whoosh_cinematic_06", "type": "xfade"},
    "slideright": {"name": "Whip Pan Right", "dur": 0.28, "foley": "whoosh_cinematic_07", "type": "xfade"},
    "slideup": {"name": "Push Up Transition", "dur": 0.30, "foley": "whoosh_cinematic_08", "type": "xfade"},
    "slidedown": {"name": "Drop Down Transition", "dur": 0.30, "foley": "whoosh_cinematic_09", "type": "xfade"},
    "smoothleft": {"name": "Nordic Soft Drift Left", "dur": 0.40, "foley": "whoosh_cinematic_10", "type": "xfade"},

    # 11-20: Soft Drifts & Aperture Unveils
    "smoothright": {"name": "Nordic Soft Drift Right", "dur": 0.40, "foley": "whoosh_cinematic_11", "type": "xfade"},
    "smoothup": {"name": "Nordic Soft Drift Up", "dur": 0.40, "foley": "whoosh_cinematic_12", "type": "xfade"},
    "smoothdown": {"name": "Nordic Soft Drift Down", "dur": 0.40, "foley": "whoosh_cinematic_13", "type": "xfade"},
    "circlecrop": {"name": "Camera Iris Push", "dur": 0.45, "foley": "camera_shutter_snap", "type": "xfade"},
    "rectcrop": {"name": "Viewfinder Aperture Crop", "dur": 0.40, "foley": "mechanical_click_01", "type": "xfade"},
    "distance": {"name": "3D Depth Dissolve", "dur": 0.50, "foley": "sub_impact_01_deep", "type": "xfade"},
    "fadeblack": {"name": "Dramatic Hard Black Dip", "dur": 0.40, "foley": "sub_impact_02_deep", "type": "xfade"},
    "fadewhite": {"name": "Paparazzi Flash White", "dur": 0.25, "foley": "camera_shutter_snap", "type": "xfade"},
    "radial": {"name": "Radar / Clock Dial Wipe", "dur": 0.50, "foley": "mechanical_click_02", "type": "xfade"},
    "circleopen": {"name": "Flashlight Spotlight Reveal", "dur": 0.45, "foley": "whoosh_cinematic_14", "type": "xfade"},

    # 21-30: Mechanical Shutters & Geometry
    "circleclose": {"name": "Vignette Dark Collapse", "dur": 0.45, "foley": "sub_impact_03_deep", "type": "xfade"},
    "vertopen": {"name": "Shutter Vertical Reveal", "dur": 0.35, "foley": "mechanical_click_03", "type": "xfade"},
    "vertclose": {"name": "Shutter Vertical Seal", "dur": 0.35, "foley": "mechanical_click_04", "type": "xfade"},
    "horzopen": {"name": "Curtain Horizontal Gate", "dur": 0.35, "foley": "paper_dossier_slide_01", "type": "xfade"},
    "horzclose": {"name": "Vault Door Lock", "dur": 0.35, "foley": "sub_impact_04_deep", "type": "xfade"},
    "dissolve": {"name": "Liquid Emulsion Crossfade", "dur": 0.50, "foley": "archival_vinyl_bed", "type": "xfade"},
    "pixelize": {"name": "Classified Redaction Pixelate", "dur": 0.30, "foley": "digital_accent_01_ui", "type": "xfade"},
    "diagtl": {"name": "Diagonal Cut Top-Left", "dur": 0.35, "foley": "whoosh_cinematic_15", "type": "xfade"},
    "diagtr": {"name": "Diagonal Cut Top-Right", "dur": 0.35, "foley": "whoosh_cinematic_01", "type": "xfade"},
    "diagbl": {"name": "Diagonal Cut Bottom-Left", "dur": 0.35, "foley": "whoosh_cinematic_02", "type": "xfade"},

    # 31-40: Slice, Blinds & Cinematic Blurs
    "diagbr": {"name": "Diagonal Cut Bottom-Right", "dur": 0.35, "foley": "whoosh_cinematic_03", "type": "xfade"},
    "hlslice": {"name": "Interlaced Horizontal Left", "dur": 0.30, "foley": "paper_dossier_slide_02", "type": "xfade"},
    "hrslice": {"name": "Interlaced Horizontal Right", "dur": 0.30, "foley": "paper_dossier_slide_03", "type": "xfade"},
    "vuslice": {"name": "Office Venetian Blinds Up", "dur": 0.35, "foley": "paper_dossier_slide_04", "type": "xfade"},
    "vdslice": {"name": "Office Venetian Blinds Down", "dur": 0.35, "foley": "paper_dossier_slide_05", "type": "xfade"},
    "hblur": {"name": "Fast Shutter Motion Blur", "dur": 0.25, "foley": "whip_pan_snap", "type": "xfade"},
    "fadegrays": {"name": "Archive Desaturation Fade", "dur": 0.45, "foley": "archival_vinyl_bed", "type": "xfade"},
    "wipetl": {"name": "Corner Peel Top-Left", "dur": 0.35, "foley": "paper_dossier_slide_06", "type": "xfade"},
    "wipetr": {"name": "Corner Peel Top-Right", "dur": 0.35, "foley": "paper_dossier_slide_07", "type": "xfade"},
    "wipebl": {"name": "Corner Peel Bottom-Left", "dur": 0.35, "foley": "paper_dossier_slide_08", "type": "xfade"},

    # 41-50: Advanced Lens, Scale & Sound-Driven Transitions
    "wipebr": {"name": "Corner Peel Bottom-Right", "dur": 0.35, "foley": "paper_dossier_slide_09", "type": "xfade"},
    "squeezeh": {"name": "Anamorphic Film Squeeze", "dur": 0.30, "foley": "whoosh_cinematic_04", "type": "xfade"},
    "squeezev": {"name": "Vertical Compress Transition", "dur": 0.30, "foley": "whoosh_cinematic_05", "type": "xfade"},
    "zoomin": {"name": "Crash Zoom Push-In", "dur": 0.28, "foley": "sub_impact_05_deep", "type": "xfade"},
    "fadefast": {"name": "Micro-Dissolve 6-Frame", "dur": 0.20, "foley": "mechanical_click_05", "type": "custom"},
    "glitch_cut": {"name": "Broadcast Glitch Interference", "dur": 0.18, "foley": "digital_accent_02_ui", "type": "custom"},
    "match_cut": {"name": "Narrative Form Match Cut", "dur": 0.00, "foley": "camera_shutter_snap", "type": "hard"},
    "sound_led_cut": {"name": "J-Cut Foley Lead In", "dur": 0.25, "foley": "paper_dossier_slide_10", "type": "j_cut"},
    "hard_cut_foley": {"name": "Hard Cut with Sub-Bass Thud", "dur": 0.00, "foley": "sub_impact_06_deep", "type": "hard"},
    "sub_drop_cut": {"name": "Dark Revelatory Sub Drop", "dur": 0.00, "foley": "sub_drop_dark", "type": "hard"}
}

def get_transition_list() -> List[str]:
    return list(TRANSITION_LIBRARY_50.keys())

if __name__ == "__main__":
    print(f"Loaded {len(TRANSITION_LIBRARY_50)} distinct master transitions.")
    for idx, (k, v) in enumerate(TRANSITION_LIBRARY_50.items(), 1):
        print(f"[{idx:02d}] {k.upper():<16} | {v['name']:<32} | {v['dur']}s | SFX: {v['foley']}")

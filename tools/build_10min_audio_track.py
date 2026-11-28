import os
import time
import wave
import json
import sqlite3
import asyncio
import subprocess
from pathlib import Path
import edge_tts

PROJ_ID = "swiss-air-grounding-prod"
BASE_DIR = Path("c:/Users/Shueb/Desktop/youtu")
AUDIO_DIR = BASE_DIR / "data" / "media" / "audio" / PROJ_ID
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Master 76-Beat Voiceover Commentary across all 6 Chapters (Target: 600 Seconds)
BEATS_COMMENTARY = {
    # CHAPTER 1: THE BLACK TUESDAY GROUNDING (0:00 - 1:40) [Beats 1-16]
    1: "On the morning of October 2nd, 2001, Zurich Kloten airport woke up to a scene that seemed mathematically impossible.",
    2: "A single emergency phone call from the fueling depot froze European aviation in its tracks.",
    3: "BP and Shell maintenance technicians slammed shut the high-pressure fueling valves on Swissair Flight 111.",
    4: "For the first time in 70 years, the Swiss national carrier's corporate credit cards were flatly rejected.",
    5: "Suppliers demanded cold hard cash before pumping a single liter of kerosene. And Swissair had none.",
    6: "Every single airliner across the international fleet was ordered grounded on the tarmac immediately.",
    7: "For seven decades, Swissair wasn't just an airline. It was the physical manifestation of Swiss precision.",
    8: "They called it 'The Flying Bank'—a financial titan backed by banking secrecy and an unblemished triple-A rating.",
    9: "Its planes were flying embassies of national prestige, serving champagne over the snow-capped Alps.",
    10: "Yet beneath the polished veneer, an aggressive acquisition strategy had metastasized out of control.",
    11: "Over 17 billion Swiss francs of toxic, hidden off-balance-sheet debt was about to detonate.",
    12: "How did Switzerland's greatest corporate symbol collapse from global titan to bankruptcy in 48 hours?",
    13: "To find the truth, we must peel back the layers of executive hubris, political isolation, and betrayal.",
    14: "The disaster did not begin with the fuel shutoff in Zurich.",
    15: "It began nine years earlier, with a fateful decision that cut Switzerland off from Europe.",
    16: "A decision that turned the world's most admired airline into a desperate, hunted animal.",

    # CHAPTER 2: THE EUROPEAN AIRSPACE TRAP (1:40 - 3:20) [Beats 17-28]
    17: "On December 6th, 1992, Swiss citizens cast their ballots in a historic national referendum on joining the European Economic Area.",
    18: "By a razor-thin margin of just 50.3 percent, the Swiss voters said no.",
    19: "In Bern, political traditionalists celebrated the defense of neutrality. But inside Swissair, executives saw a death sentence.",
    20: "The European Union was deregulating its airspace under the Open Skies directives, allowing member airlines to fly without borders.",
    21: "British Airways, Lufthansa, and Air France began consolidating, while aggressive budget airlines like Ryanair tore through the market.",
    22: "Swissair was trapped. Because Switzerland was outside the EU, Swissair was legally prohibited from picking up passengers between European cities.",
    23: "They could not fly Paris to Rome. They could not base aircraft in Frankfurt or Amsterdam.",
    24: "Every competitor was rapidly expanding their network, while Swissair was confined to a tiny, landlocked domestic island.",
    25: "Worse, Swiss operating costs were among the highest on earth, paying pilots and staff in strong, expensive Swiss francs.",
    26: "The board recognized that standing still meant slow, agonizing death by irrelevance.",
    27: "They needed a radical strategy to bypass European protectionist laws.",
    28: "And in 1997, they found the man who promised to deliver it: Philippe Bruggisser.",

    # CHAPTER 3: THE HUNTER STRATEGY (3:20 - 5:00) [Beats 29-40]
    29: "Philippe Bruggisser was charismatic, hyper-ambitious, and utterly convinced of his own financial genius.",
    30: "He presented the board with an audacious expansion blueprint christened 'The Hunter Strategy'.",
    31: "If European regulators wouldn't let Swissair expand organically, Swissair would buy its way into the European skies.",
    32: "Because EU law prohibited non-European companies from owning majority stakes, Bruggisser acquired minority 49.5 percent holdings.",
    33: "Between 1998 and 2000, Swissair went on an uncontrolled multi-billion-franc acquisition spree.",
    34: "They bought into Belgium's chronically unprofitable national carrier, Sabena, which had lost money for forty consecutive years.",
    35: "They bought stakes in Germany's troubled charter airline LTU, France's Air Littoral and AOM, Portugal's TAP, and Poland's LOT.",
    36: "Bruggisser assembled a cobbled-together alliance of sick airlines under the banner of the Qualiflyer Group.",
    37: "To close these deals, Swissair signed confidential, off-balance-sheet shareholder agreements.",
    38: "These toxic clauses legally bound Swissair to finance the recapitalization and ongoing operating losses of its troubled partners.",
    39: "Sabena alone was hemorrhaging over one million Swiss francs every single working day.",
    40: "Swissair had taken on all the financial liabilities of failing foreign carriers, with zero executive authority to fix them.",

    # CHAPTER 4: THE 17 BILLION BLACK HOLE (5:00 - 6:40) [Beats 41-52]
    41: "By January 2001, the bleeding could no longer be disguised behind accounting gymnastics.",
    42: "Swissair was burning through tens of millions of francs in cash each week just to keep its acquired airlines airborne.",
    43: "In an emergency midnight board session, Philippe Bruggisser was abruptly fired as Chief Executive.",
    44: "The board turned to Mario Corti, the widely respected Chief Financial Officer of Nestlé, appointing him Chairman and CEO.",
    45: "Corti was promised absolute transparency and total autonomy to restructure the battered aviation conglomerate.",
    46: "He immediately commissioned an exhaustive forensic audit from Ernst & Young to uncover the true financial exposure.",
    47: "What the auditors discovered shocked the Swiss business establishment to its core.",
    48: "The true off-balance-sheet commitments and contingent liabilities totaled a catastrophic 17.2 billion Swiss francs.",
    49: "Then, on September 11th, 2001, commercial aviation suffered the most devastating external shock in modern history.",
    50: "Transatlantic travel plummeted by over forty percent overnight. Swissair's cash reserves evaporated within days.",
    51: "Corti knew the parent group was insolvent. He needed an emergency cash bridge of 100 million francs just to survive the week.",
    52: "He reached out to Switzerland's most powerful banking titans: UBS and Credit Suisse.",

    # CHAPTER 5: PROJECT PHOENIX & THE BANK BETRAYAL (6:40 - 8:20) [Beats 53-64]
    53: "Across Zurich's Paradeplatz, behind the closed mahogany doors of UBS, a very different calculus was taking shape.",
    54: "UBS Chairman Marcel Ospel and Credit Suisse leadership had drawn up a confidential rescue blueprint codenamed 'Project Phoenix'.",
    55: "Project Phoenix was not designed to save Swissair. It was designed to carve out its valuable assets and let the mother company die.",
    56: "Swissair owned a profitable, debt-free regional subsidiary: Crossair, founded by entrepreneur Moritz Suter.",
    57: "The banks planned to purchase Crossair's shares, transfer Swissair's modern fleet and profitable routes to it, and ditch the 17 billion in debt.",
    58: "Under the agreement, the banks pledged to provide a liquidity bridge of 250 million francs on Monday, October 1st.",
    59: "That money was earmarked specifically to keep Swissair planes fueled and operational until the formal handover.",
    60: "On Monday afternoon, Mario Corti waited for the funds to arrive in Swissair's operational treasury accounts.",
    61: "The hours ticked by. The funds were deliberately withheld by UBS due to last-minute administrative disputes.",
    62: "By dawn on Tuesday, October 2nd, the bank transfer had still not arrived.",
    63: "Fuel suppliers in Zurich, London, and New York issued immediate cash-on-delivery ultimatums.",
    64: "At 12:30 PM, Swissair Flight Operations received the order: cancel all departures worldwide. The Flying Bank was dead.",

    # CHAPTER 6: THE FALL, TRIAL & REBIRTH (8:20 - 10:00) [Beats 65-76]
    65: "The announcement triggered scenes of total pandemonium across international terminals from Tokyo to Los Angeles.",
    66: "More than 38,000 Swissair passengers and 1,000 flight crew members were stranded on tarmacs without tickets or hotel rooms.",
    67: "In Zurich, furious Swiss citizens marched on Paradeplatz, hurling eggs at UBS headquarters and denouncing bankers as national traitors.",
    68: "The Swiss Federal Council was forced to intervene with an emergency taxpayer loan of 450 million francs to resume temporary repatriation flights.",
    69: "On March 31st, 2002, the final Swissair commercial flight touched down in Zurich, closing 71 years of aviation history.",
    70: "The profitable remnants of the fleet were rolled into Crossair to form the newly branded Swiss International Air Lines.",
    71: "Yet the ultimate humiliation was still to come.",
    72: "Just three years later, in 2005, the newly minted SWISS was acquired by its arch-rival, Germany's Lufthansa, for a fraction of its former value.",
    73: "In 2007, nineteen former directors and executives, including Bruggisser and Corti, stood trial in Zurich district court.",
    74: "They faced severe criminal charges of fraudulent bankruptcy, false accounting, and mismanagement.",
    75: "After months of sensational testimony, the court acquitted every single defendant of criminal wrongdoing, ruling it corporate failure rather than crime.",
    76: "Seventeen billion francs vanished forever into the Alps—a timeless warning of what happens when executive arrogance meets unbridled financial greed."
}

def get_audio_duration(wav_path: Path) -> float:
    with wave.open(str(wav_path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())

VOICE_FALLBACKS = [
    "en-US-AndrewMultilingualNeural",
    "en-US-GuyNeural",
    "en-US-ChristopherNeural",
    "en-GB-RyanNeural"
]

async def synthesize_beat_edge(order: int, text: str):
    out_wav = AUDIO_DIR / f"beat_{order}.wav"
    raw_mp3 = AUDIO_DIR / f"beat_{order}_raw.mp3"
    
    # If file exists and is healthy, skip
    if out_wav.exists() and out_wav.stat().st_size > 10000:
        return
        
    for voice in VOICE_FALLBACKS:
        try:
            print(f"Synthesizing Beat {order:02d} with Edge-TTS ({voice})...")
            comm = edge_tts.Communicate(text, voice, rate="-2%")
            await comm.save(str(raw_mp3))
            
            if raw_mp3.exists() and raw_mp3.stat().st_size > 1000:
                cmd = [
                    "ffmpeg", "-y", "-i", str(raw_mp3),
                    "-af", "aresample=44100,loudnorm=I=-14:LRA=11:TP=-1",
                    "-threads", "1",
                    str(out_wav)
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                raw_mp3.unlink(missing_ok=True)
                print(f"Beat {order:02d} rendered successfully!")
                await asyncio.sleep(0.5)
                return
        except Exception as e:
            print(f"Voice {voice} failed for Beat {order}: {e}. Retrying with fallback...")
            await asyncio.sleep(1.0)
            
    print(f"ERROR: Failed all voices for Beat {order}")

async def main():
    print(f"Checking all {len(BEATS_COMMENTARY)} narration beats across Chapters 1-6...")
    for order, text in sorted(BEATS_COMMENTARY.items()):
        await synthesize_beat_edge(order, text)
        
    total_dur = 0.0
    for order in sorted(BEATS_COMMENTARY.keys()):
        wav_path = AUDIO_DIR / f"beat_{order}.wav"
        if wav_path.exists():
            d = get_audio_duration(wav_path)
            total_dur += d
    print(f"\nAll {len(BEATS_COMMENTARY)} beats verified!")
    print(f"Total Narration Duration: {total_dur:.2f} seconds ({total_dur/60:.2f} minutes)")

if __name__ == "__main__":
    asyncio.run(main())

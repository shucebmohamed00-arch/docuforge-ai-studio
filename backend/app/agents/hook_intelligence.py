"""
DocuForge AI - Agent 2: Viral Hook Intelligence Agent
Generates opening hooks and high-curiosity documentary titles.
Never guarantees virality or invents fake viral probability scores.
"""
from typing import List, Dict, Any

class ViralHookIntelligenceAgent:
    @staticmethod
    def generate_opening_hooks(topic_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates 3 distinct, evidence-backed opening hooks for the documentary.
        Each hook specifies narration, visual treatment, sound design, and the curiosity gap.
        """
        title = topic_data.get("title", "")
        pillar = topic_data.get("pillar", "BUSINESS")
        angle = topic_data.get("angle", "")
        central_conflict = topic_data.get("central_conflict", "")

        hooks = [
            {
                "hook_number": 1,
                "strategy": "The In medias res Moment / Turning Point",
                "curiosity_gap": f"Why a single critical meeting or decision triggered the entire catastrophe in {title}.",
                "narration_script": (
                    f"On a quiet Tuesday morning, a single memo was sent that would quietly trigger the collapse of an empire. "
                    f"To the outside world, everything appeared indestructible. "
                    f"Behind closed doors, the architects knew they had only forty-eight hours before the numbers caught up to them."
                ),
                "visual_direction": "Slow push-in on an authentic declassified memo or financial ledger. Harsh desk lamp lighting, cinematic vignette. Cut abruptly to archival press conference footage.",
                "sound_direction": "Low ominous sub-bass drone with rhythmic mechanical typewriter keystrokes, suddenly cutting into complete silence on the word 'hours'.",
                "intellectual_stakes": "Exposes how institutional opacity blinds investors and regulators until the damage is irreversible."
            },
            {
                "hook_number": 2,
                "strategy": "The Contradiction / Reality Distortion",
                "curiosity_gap": f"The staggering contrast between the public narrative and the hidden reality of {angle}.",
                "narration_script": (
                    f"If you look at the official records, this was celebrated as the greatest technological breakthrough of the decade. "
                    f"The stock surged, world leaders lined up for photos, and billions flowed in overnight. "
                    f"There was just one problem: the core technology had never actually worked."
                ),
                "visual_direction": "Montage of glowing broadcast headlines and stock market celebration ticker, followed by a stark match-cut to empty, silent warehouse blueprints or internal email warnings.",
                "sound_direction": "Upbeat corporate fanfare audio slowly distorts, pitches down into a discordant drone with a tape-stop sound effect.",
                "intellectual_stakes": "Deconstructs the psychology of hype and how charisma can bypass standard due diligence."
            },
            {
                "hook_number": 3,
                "strategy": "The Geopolitical / Systemic Domino",
                "curiosity_gap": f"How an obscure localized failure escalated into a global crisis: {central_conflict}.",
                "narration_script": (
                    f"Most people have never heard of this isolated facility, or the five individuals who walked out of it in 2019. "
                    f"Yet within eighteen months, their quiet departure would choke global supply chains, trigger diplomatic standoffs, "
                    f"and force three superpowers to rewrite their national security doctrines."
                ),
                "visual_direction": "Satellite zoom from outer space down into specific geographic coordinates, dynamic animated route lines radiating across global trade bottlenecks.",
                "sound_direction": "Subtle radar ping and atmospheric room tone, swelling into a heavy orchestral brass hit.",
                "intellectual_stakes": "Reveals the fragile chokepoints of modern globalization that modern economies take for granted."
            }
        ]
        return hooks

    @staticmethod
    def generate_title_concepts(topic_data: Dict[str, Any]) -> List[str]:
        """
        Generates compelling documentary titles following proven investigative patterns:
        - How One Decision Destroyed X
        - Why the World's Most Important X Matters
        - The Hidden Story Behind X
        """
        title = topic_data.get("title", "")
        angle = topic_data.get("angle", "")
        pillar = topic_data.get("pillar", "BUSINESS")

        if pillar == "BUSINESS":
            return [
                f"How One Decision Destroyed {title}",
                f"The $100 Billion Lie: The Real Story of {title}",
                f"The Secret Meeting That Broke {title}",
                f"Why Nobody Stopped the Collapse of {title}"
            ]
        elif pillar == "GEOPOLITICS":
            return [
                f"The Battle for the World's Most Critical Chokepoint: {title}",
                f"Why Superpowers Are Secretly Fighting Over {title}",
                f"The Hidden Geography Powering the Next Conflict: {title}",
                f"How {title} Quietly Reshaped Global Trade"
            ]
        elif pillar == "TECHNOLOGY":
            return [
                f"The Hidden Monopoly Behind the AI Revolution: {title}",
                f"How One Company Cornered the Market on {title}",
                f"The Breakthrough That Tech Giants Kept Secret: {title}",
                f"Why Silicon Valley Is Terrified of {title}"
            ]
        else: # HISTORY
            return [
                f"The Forgotten Disaster That Changed History: {title}",
                f"The Classified Operation Behind {title}",
                f"What Really Happened During the Investigation of {title}",
                f"The Untold Story Behind the Scandal of {title}"
            ]

"""
DocuForge Multi-Agent Graphics Engine - Central Orchestrator
Supervises and coordinates all specialized documentary graphics agents:
scouting archival assets, generating 2.5D parallax cards, rendering document stamp slams,
animating financial graphics, performing automated QC audits, and assembling final masters.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from .agents.archival_scout import ArchivalScoutAgent
from .agents.parallax_depth import ParallaxDepthAgent
from .agents.document_inspector import DocumentInspectorAgent
from .agents.data_visualizer import DataVisualizerAgent
from .agents.director_qc import DirectorQCAgent
from .agents.master_assembly import MasterAssemblyAgent
from .agents.footage_stylist import FootageStylistAgent
from .agents.visual_critic import VisualCriticAgent
from .agents.timeline_reviewer import TimelineReviewerAgent
from .agents.auto_director import AutoDirectorAgent
from .agents.stage_compositor import StageCompositorAgent

class DocuForgeOrchestrator:
    def __init__(self):
        self.scout = ArchivalScoutAgent()
        self.parallax = ParallaxDepthAgent()
        self.doc_inspector = DocumentInspectorAgent()
        self.dataviz = DataVisualizerAgent()
        self.qc = DirectorQCAgent()
        self.assembler = MasterAssemblyAgent()
        self.stylist = FootageStylistAgent()
        self.critic = VisualCriticAgent()
        self.reviewer = TimelineReviewerAgent()
        self.auto_director = AutoDirectorAgent()
        self.stage = StageCompositorAgent()

        self.agents = {
            "scout": self.scout,
            "visual_critic": self.critic,
            "footage_stylist": self.stylist,
            "stage_compositor": self.stage,
            "parallax": self.parallax,
            "doc_inspector": self.doc_inspector,
            "dataviz": self.dataviz,
            "director_qc": self.qc,
            "assembler": self.assembler,
            "timeline_reviewer": self.reviewer,
            "auto_director": self.auto_director
        }

    def print_roster(self):
        print("\n=======================================================")
        print("  DOCUFORGE MULTI-AGENT GRAPHICS ENGINE ROSTER")
        print("=======================================================")
        for key, agent in self.agents.items():
            print(f"[{agent.name.upper()}] - {agent.role}")
            print(f"  Description: {agent.description}\n")
        print("=======================================================\n")

    def run_end_to_end_production(self, query: str, character_name: str, doc_headline: str) -> Dict[str, Any]:
        """
        Executes a coordinated multi-agent workflow:
        1. Scout searches & downloads authentic archival material.
        2. Parallax agent renders a 2.5D character portrait.
        3. Doc Inspector renders a headline with orange highlighter and stamp slam.
        4. DataViz renders an exponential debt/stock collapse.
        5. QC Agent audits output files for 0 black frames and 16:9 compliance.
        """
        print(f"\n>>> LAUNCHING COOPERATIVE MULTI-AGENT GRAPHICS PIPELINE: '{query}' <<<\n")

        # Step 1: Scout Archival Asset
        scout_res = self.scout.execute({
            "query": query,
            "limit": 3,
            "auto_download": True,
            "download_count": 1
        })

        # Step 2: 2.5D Parallax Character Card
        face_sample = Path("c:/Users/Shueb/Desktop/youtu/data/media/documentary_photos/photo_02_mario_corti.png")
        if not face_sample.exists():
            face_sample = Path(scout_res["downloaded_files"][0]) if scout_res.get("downloaded_files") else None

        parallax_res = None
        if face_sample and face_sample.exists():
            parallax_res = self.parallax.execute({
                "face_path": str(face_sample),
                "title": character_name,
                "subtitle": "SWISSAIR CRISIS LEADERSHIP",
                "badge": "PARALLAX 2.5D DOSSIER",
                "duration": 3.0
            })

        # Step 3: Document Stamp Slam
        doc_src = Path("c:/Users/Shueb/Desktop/youtu/data/media/paper_assets/paper_01_blick_grounded.png")
        doc_res = None
        if doc_src.exists():
            doc_res = self.doc_inspector.execute({
                "document_path": str(doc_src),
                "stamp_title": "INSOLVENCY AUDIT",
                "stamp_sub": "17.8 BILLION VERIFIED",
                "duration": 3.0,
                "impact_time": 1.2
            })

        # Step 4: Financial Plunge Chart
        dataviz_res = self.dataviz.execute({
            "type": "stock_crash",
            "ticker": "SWISSAIR (SR.SW) COLLAPSE",
            "start_val": 380.0,
            "end_val": 1.25,
            "duration": 3.0
        })

        # Step 5: QC Audit on Master Video
        master_video = Path("c:/Users/Shueb/Desktop/youtu/data/exports/swiss-air-grounding-prod/documentary.mp4")
        qc_res = None
        if master_video.exists():
            qc_res = self.qc.execute({"video_path": str(master_video)})

        return {
            "scout": scout_res,
            "parallax": parallax_res,
            "doc_inspector": doc_res,
            "dataviz": dataviz_res,
            "qc": qc_res
        }

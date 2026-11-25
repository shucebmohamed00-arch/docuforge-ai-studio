"""
DocuForge Multi-Agent Graphics Engine - Command Line Interface
Run full end-to-end pipelines or delegate specific tasks directly to specialized agents.
"""
import sys
import argparse
import json
from pathlib import Path
from .orchestrator import DocuForgeOrchestrator

def main():
    parser = argparse.ArgumentParser(description="DocuForge Multi-Agent Graphics Engine CLI")
    subparsers = parser.add_subparsers(dest="command", help="Agent command to execute")

    # Command: roster
    subparsers.add_parser("roster", help="List all specialized agents and roles")

    # Command: scout
    p_scout = subparsers.add_parser("scout", help="Delegate asset discovery to Archival Scout Agent")
    p_scout.add_argument("--query", "-q", required=True, help="Search query (e.g. 'Swissair MD-11 Zurich')")
    p_scout.add_argument("--limit", "-l", type=int, default=3, help="Max candidates to return")
    p_scout.add_argument("--download", "-d", action="store_true", help="Auto-download candidate asset")

    # Command: parallax
    p_par = subparsers.add_parser("parallax", help="Delegate 2.5D portrait card rendering to Parallax Agent")
    p_par.add_argument("--face", "-f", required=True, help="Path to character portrait image")
    p_par.add_argument("--title", "-t", default="Executive", help="Character name/title")
    p_par.add_argument("--sub", "-s", default="Swissair Authority", help="Subtitle/role")
    p_par.add_argument("--badge", "-b", default="ARCHIVE DOSSIER", help="Badge text")
    p_par.add_argument("--out", "-o", default="test_parallax.mp4", help="Output mp4 filename")

    # Command: stamp
    p_st = subparsers.add_parser("stamp", help="Delegate document inspection & rubber stamp slam")
    p_st.add_argument("--doc", "-d", required=True, help="Path to document image or video")
    p_st.add_argument("--stamp", required=True, help="Main rubber stamp text (e.g. 'FLEET GROUNDED')")
    p_st.add_argument("--sub", default="VERIFIED CRISIS", help="Sub-stamp text")
    p_st.add_argument("--out", "-o", default="test_doc_stamp.mp4", help="Output mp4 filename")

    # Command: chart
    p_ch = subparsers.add_parser("chart", help="Delegate financial chart animation")
    p_ch.add_argument("--ticker", "-t", default="SWISSAIR (SR.SW)", help="Ticker name")
    p_ch.add_argument("--out", "-o", default="test_stock_crash.mp4", help="Output mp4 filename")

    # Command: style
    p_style = subparsers.add_parser("style", help="Pre-process and animate raw footage with Footage Stylist Agent")
    p_style.add_argument("--clip", "-c", required=True, help="Path to raw video clip")
    p_style.add_argument("--motion", "-m", default="slow_push", choices=["slow_push", "drift_right", "archival_moody"], help="Motion animation style")
    p_style.add_argument("--dur", "-d", type=float, default=4.0, help="Target duration in seconds")
    p_style.add_argument("--out", "-o", default="styled_clip.mp4", help="Output filename")

    # Command: qc
    p_qc = subparsers.add_parser("qc", help="Delegate Quality Control audit to Director QC Agent")
    p_qc.add_argument("--video", "-v", required=True, help="Path to video file to audit")

    # Command: critique
    p_crit = subparsers.add_parser("critique", help="Visually inspect and score candidate footage with Visual Critic Agent")
    p_crit.add_argument("--clip", "-c", required=True, help="Path to video clip to evaluate")

    # Command: review
    p_rev = subparsers.add_parser("review", help="Visually audit entire documentary timeline with Timeline Reviewer Agent")
    p_rev.add_argument("--video", "-v", required=True, help="Path to documentary video")
    p_rev.add_argument("--interval", "-i", type=float, default=25.0, help="Sampling interval in seconds")

    # Command: autodirect
    p_ad = subparsers.add_parser("autodirect", help="Autonomous closed-loop review and self-healing with Auto-Director Agent")
    p_ad.add_argument("--video", "-v", default="data/exports/swiss-air-grounding-prod/documentary.mp4", help="Video path")
    p_ad.add_argument("--storyboard", "-s", default="storyboard_items.json", help="Storyboard path")

    # Command: pipeline
    p_pipe = subparsers.add_parser("pipeline", help="Run end-to-end multi-agent cooperative graphics pipeline")
    p_pipe.add_argument("--query", "-q", default="Swissair MD-11 Zurich", help="Search query for scout")
    p_pipe.add_argument("--character", "-c", default="MARIO CORTI", help="Character name")
    p_pipe.add_argument("--headline", default="17.8 BILLION DEBT", help="Document headline")

    args = parser.parse_args()
    orchestrator = DocuForgeOrchestrator()

    if not args.command or args.command == "roster":
        orchestrator.print_roster()
        return

    if args.command == "scout":
        res = orchestrator.scout.execute({
            "query": args.query,
            "limit": args.limit,
            "auto_download": args.download
        })
        print(json.dumps(res, indent=2))

    elif args.command == "parallax":
        res = orchestrator.parallax.execute({
            "face_path": args.face,
            "title": args.title,
            "subtitle": args.sub,
            "badge": args.badge,
            "out_name": args.out
        })
        print(json.dumps(res, indent=2))

    elif args.command == "stamp":
        res = orchestrator.doc_inspector.execute({
            "document_path": args.doc,
            "stamp_title": args.stamp,
            "stamp_sub": args.sub,
            "out_name": args.out
        })
        print(json.dumps(res, indent=2))

    elif args.command == "chart":
        res = orchestrator.dataviz.execute({
            "type": "stock_crash",
            "ticker": args.ticker,
            "out_name": args.out
        })
        print(json.dumps(res, indent=2))

    elif args.command == "style":
        res = orchestrator.stylist.execute({
            "src_path": args.clip,
            "motion_style": args.motion,
            "duration": args.dur,
            "out_name": args.out
        })
        print(json.dumps(res, indent=2))

    elif args.command == "qc":
        res = orchestrator.qc.execute({"video_path": args.video})
        print(json.dumps(res, indent=2))

    elif args.command == "critique":
        res = orchestrator.critic.execute({"video_path": args.clip})
        print(json.dumps(res, indent=2))

    elif args.command == "review":
        res = orchestrator.reviewer.execute({
            "video_path": args.video,
            "interval_sec": args.interval
        })
        print(json.dumps(res, indent=2))

    elif args.command == "autodirect":
        res = orchestrator.auto_director.execute({
            "video_path": args.video,
            "storyboard_path": args.storyboard
        })
        print(json.dumps(res, indent=2))

    elif args.command == "pipeline":
        res = orchestrator.run_end_to_end_production(
            query=args.query,
            character_name=args.character,
            doc_headline=args.headline
        )
        print("\nPipeline execution summary completed!")

if __name__ == "__main__":
    main()

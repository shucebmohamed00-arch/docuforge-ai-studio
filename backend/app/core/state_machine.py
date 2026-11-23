"""
DocuForge AI - Production State Machine
Enforces strict 20-step workflow, approval gates, and stage transitions.
"""
from enum import Enum
from typing import List, Dict, Optional, Tuple

class ProjectStatus(str, Enum):
    # Phase 2: Topic Selection
    TOPIC_SELECTION = "TOPIC_SELECTION"        # Step 1-2: 5 vetted topics presented, user selects 1
    
    # Phase 3: Research & Fact Checking
    RESEARCH_IN_PROGRESS = "RESEARCH_IN_PROGRESS" # Step 3: Deep Research agent builds dossier
    FACT_CHECKING = "FACT_CHECKING"              # Step 4: Fact-checking agent verifies claims
    
    # Phase 4: Scriptwriting
    SCRIPTING = "SCRIPTING"                      # Step 5: Master Storyteller crafts script
    SCRIPT_REVIEW = "SCRIPT_REVIEW"              # Step 6: User approves/edits script [CHECKPOINT 1]
    
    # Phase 5: Visual Planning
    VISUAL_PLANNING = "VISUAL_PLANNING"          # Step 7: Creative Director generates manifest
    
    # Phase 6: Footage Discovery & Asset Approval
    FOOTAGE_DISCOVERY = "FOOTAGE_DISCOVERY"      # Step 8-9: Free archive search & matching
    ASSETS_PENDING_APPROVAL = "ASSETS_PENDING_APPROVAL" # Step 10-11: Mandatory Visual Approval [CHECKPOINT 2]
    
    # Phase 7: Storyboard
    STORYBOARD_REVIEW = "STORYBOARD_REVIEW"      # Step 12-13: Storyboard flow review [CHECKPOINT 3]
    
    # Phase 8 & 9: Narration, Sound & Motion Graphics
    NARRATION_GENERATION = "NARRATION_GENERATION"# Step 14: Segmented TTS + Audio design
    ANIMATION_SYNTHESIS = "ANIMATION_SYNTHESIS"  # Step 15: Maps, charts, motion graphics
    
    # Phase 10: Assembly & Rendering
    EDITING_RENDERING = "EDITING_RENDERING"      # Step 16-17: FFmpeg multi-track compositing
    
    # Phase 12: Quality Control
    QUALITY_CONTROL = "QUALITY_CONTROL"          # Step 18: Automated QC analysis
    
    # Phase 11: Thumbnails
    THUMBNAIL_GENERATION = "THUMBNAIL_GENERATION"# Step 19: Dual 1280x720 thumbnail creation
    
    # Phase 13: Export
    EXPORT_READY = "EXPORT_READY"                # Step 20: Final package ready for download
    COMPLETED = "COMPLETED"                      # Final archived state
    FAILED = "FAILED"                            # Failed QC or critical error

# Permitted state transitions
ALLOWED_TRANSITIONS: Dict[ProjectStatus, List[ProjectStatus]] = {
    ProjectStatus.TOPIC_SELECTION: [ProjectStatus.RESEARCH_IN_PROGRESS],
    ProjectStatus.RESEARCH_IN_PROGRESS: [ProjectStatus.FACT_CHECKING, ProjectStatus.FAILED],
    ProjectStatus.FACT_CHECKING: [ProjectStatus.SCRIPTING, ProjectStatus.RESEARCH_IN_PROGRESS, ProjectStatus.FAILED],
    ProjectStatus.SCRIPTING: [ProjectStatus.SCRIPT_REVIEW, ProjectStatus.FAILED],
    ProjectStatus.SCRIPT_REVIEW: [ProjectStatus.VISUAL_PLANNING, ProjectStatus.SCRIPTING], # User can approve or request rewrite
    ProjectStatus.VISUAL_PLANNING: [ProjectStatus.FOOTAGE_DISCOVERY, ProjectStatus.FAILED],
    ProjectStatus.FOOTAGE_DISCOVERY: [ProjectStatus.ASSETS_PENDING_APPROVAL, ProjectStatus.FAILED],
    ProjectStatus.ASSETS_PENDING_APPROVAL: [ProjectStatus.STORYBOARD_REVIEW, ProjectStatus.FOOTAGE_DISCOVERY], # Hard approval gate
    ProjectStatus.STORYBOARD_REVIEW: [ProjectStatus.NARRATION_GENERATION, ProjectStatus.ASSETS_PENDING_APPROVAL],
    ProjectStatus.NARRATION_GENERATION: [ProjectStatus.ANIMATION_SYNTHESIS, ProjectStatus.FAILED],
    ProjectStatus.ANIMATION_SYNTHESIS: [ProjectStatus.EDITING_RENDERING, ProjectStatus.FAILED],
    ProjectStatus.EDITING_RENDERING: [ProjectStatus.QUALITY_CONTROL, ProjectStatus.FAILED],
    ProjectStatus.QUALITY_CONTROL: [ProjectStatus.THUMBNAIL_GENERATION, ProjectStatus.EXPORT_READY, ProjectStatus.EDITING_RENDERING, ProjectStatus.FAILED], # QC can return for repair
    ProjectStatus.THUMBNAIL_GENERATION: [ProjectStatus.EXPORT_READY, ProjectStatus.FAILED],
    ProjectStatus.EXPORT_READY: [ProjectStatus.COMPLETED],
    ProjectStatus.COMPLETED: [],
    ProjectStatus.FAILED: [ProjectStatus.TOPIC_SELECTION, ProjectStatus.RESEARCH_IN_PROGRESS, ProjectStatus.SCRIPTING, ProjectStatus.FOOTAGE_DISCOVERY, ProjectStatus.EDITING_RENDERING]
}

APPROVAL_CHECKPOINTS = {
    ProjectStatus.SCRIPT_REVIEW: "Review and approve documentary narration script before visual production.",
    ProjectStatus.ASSETS_PENDING_APPROVAL: "Mandatory visual approval: Review every proposed archive video, photo, and graphic.",
    ProjectStatus.STORYBOARD_REVIEW: "Review the complete scene-by-scene storyboard sequence before audio & rendering."
}

def validate_transition(current_status: str, new_status: str) -> Tuple[bool, Optional[str]]:
    """Validates if transitioning from current_status to new_status is allowed."""
    try:
        curr = ProjectStatus(current_status)
        target = ProjectStatus(new_status)
    except ValueError as e:
        return False, f"Invalid status value: {e}"

    if curr == target:
        return True, None

    allowed = ALLOWED_TRANSITIONS.get(curr, [])
    if target not in allowed:
        return False, f"Illegal transition from '{curr.value}' to '{target.value}'. Allowed: {[s.value for s in allowed]}"
    return True, None

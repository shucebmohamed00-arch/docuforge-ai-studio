#!/usr/bin/env python3
"""
DocuForge Multi-Agent Graphics Engine - Execution Runner
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from docuforge_engine.cli import main

if __name__ == "__main__":
    main()

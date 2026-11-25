"""
DocuForge Multi-Agent Graphics Engine - Core Base Agent
Provides lifecycle management, message passing, task execution, and reporting for specialized agents.
"""
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger("docuforge_engine")

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, description: str):
        self.name = name
        self.role = role
        self.description = description
        self.execution_log: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(f"docuforge.{name}")

    def log(self, message: str, level: str = "INFO"):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{self.name.upper()}] {message}"
        print(entry, flush=True)
        self.execution_log.append({"time": timestamp, "message": message, "level": level})

    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a specialized task and returns the result artifact metadata.
        """
        pass

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "tasks_executed": len(self.execution_log)
        }

"""
RAG Data Synthesis Pipeline

Clean implementation using the new sandbox architecture.
"""

__version__ = "1.0.0"
__author__ = "Data Synthesis Team"

from .core import (
    SynthesisConfig,
    SandboxWorker,
    TrajectorySampler,
    TrajectorySelector,
    QASynthesizer,
    TrajectoryNode,
    Trajectory,
    SynthesizedQA,
)
from .api import load_config, load_seeds, synthesize

__all__ = [
    "SynthesisConfig",
    "SandboxWorker",
    "TrajectorySampler",
    "TrajectorySelector",
    "QASynthesizer",
    "TrajectoryNode",
    "Trajectory",
    "SynthesizedQA",
    "load_config",
    "load_seeds",
    "synthesize",
]

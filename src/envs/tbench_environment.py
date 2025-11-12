# -*- coding: utf-8 -*-
"""
TBench Environment - Terminal Bench environment for configuration-only scenarios.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from envs.enviroment import Environment


class TBenchEnvironment(Environment):
    """
    A minimal concrete environment for configuration-only scenarios (e.g., initializing Terminal Bench)
    without registering any tools. Use this when you only need environment setup but no specific tools.
    """

    @property
    def mode(self) -> str:
        return "tbench"

    def _initialize_tools(self):
        """No tools by default; suitable for bench/config-only usage."""
        self.tools = {}
        self._generate_tool_metadata()

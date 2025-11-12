# -*- coding: utf-8 -*-
"""
Python Environment - Environment with interpreter tools.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from envs.enviroment import Environment


class PythonEnvironment(Environment):
    """Python environment with interpreter tools."""

    @property
    def mode(self) -> str:
        return "py"

    def _initialize_tools(self):
        """Initialize Python-specific tools."""
        try:
            from tools.python_interpreter import PythonInterpreterTool
            self.register_tool(PythonInterpreterTool())
        except ImportError:
            raise ImportError("PythonInterpreterTool not available")


# Convenience function for common use cases
def create_python_environment(**kwargs):
    """Create a Python environment with interpreter tools."""
    return PythonEnvironment(**kwargs)

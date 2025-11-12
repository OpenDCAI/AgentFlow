# -*- coding: utf-8 -*-
"""
Math Environment - Environment with calculator tools.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from envs.enviroment import Environment
from tools import CalculatorTool


class MathEnvironment(Environment):
    """Math environment with calculator tools."""

    @property
    def mode(self) -> str:
        return "math"

    def _initialize_tools(self):
        """Initialize math-specific tools."""
        self.register_tool(CalculatorTool())


# Convenience function for common use cases
def create_math_environment(**kwargs):
    """Create a math environment with calculator tools."""
    return MathEnvironment(**kwargs)

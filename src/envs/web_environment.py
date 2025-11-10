# -*- coding: utf-8 -*-
"""
Web Environment - Environment with search and visit tools.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from envs.enviroment import Environment
from tools import WebSearchTool, WebVisitTool


class WebEnvironment(Environment):
    """Web environment with search and visit tools."""

    @property
    def mode(self) -> str:
        return "web"

    def _initialize_tools(self):
        """Initialize web-specific tools."""
        # Configure web search tool
        web_search_config = {
            "top_k": self.config.get("web_search_top_k", 5),
            "search_type": self.config.get("web_search_type", "search"),
            "max_workers": self.config.get("web_search_max_workers", 5)
        }

        # Configure web visit tool
        web_visit_config = {
            "summary_model": self.config.get("web_visit_summary_model", "gpt-4.1-2025-04-14"),
            "visit_method": self.config.get("web_visit_visit_method", "jina")
        }

        self.register_tool(WebSearchTool(**web_search_config))
        self.register_tool(WebVisitTool(**web_visit_config))


# Convenience function for common use cases
def create_web_environment(**kwargs):
    """Create a web environment with search and visit tools."""
    return WebEnvironment(**kwargs)

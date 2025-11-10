# -*- coding: utf-8 -*-
"""
RAG Environment - Environment with retrieval tools.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from envs.enviroment import Environment


class RAGEnvironment(Environment):
    """RAG environment with retrieval tools."""

    def __init__(self, rag_index, **kwargs):
        self.rag_index = rag_index
        super().__init__(**kwargs)

    @property
    def mode(self) -> str:
        return "rag"

    def _initialize_tools(self):
        """Initialize RAG-specific tools."""
        try:
            from tools.rag_tools import QueryRAGIndexTool
            local_search_tool = QueryRAGIndexTool(self.rag_index)
            self.register_tool(local_search_tool)
        except ImportError:
            raise ImportError("RAG tools not available")


# Convenience function for common use cases
def create_rag_environment(**kwargs):
    """Create a RAG environment with retrieval tools."""
    return RAGEnvironment(**kwargs)

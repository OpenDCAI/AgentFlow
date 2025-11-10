
import os
import json
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
import sys
import pdb
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ToolResponse:
    """
    Structured tool response format for OSWorld tools.

    This class encapsulates tool execution results with status, message, and observation data.
    For OSWorld tools, observations are pre-processed (base64 encoded screenshots, linearized a11y tree)
    so that _run_conversation can use them directly without additional processing.

    Attributes:
        status: 'success' or 'failed'
        response: Human-readable execution message
        observation: Optional dict with pre-processed observation data:
            - 'screenshot': base64-encoded PNG string (ready for image_url)
            - 'a11y_tree': linearized accessibility tree string (ready for text content)
    """

    def __init__(
        self,
        status: str,
        response: str,
        observation: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize ToolResponse.

        Args:
            status: Execution status ('success' or 'failed')
            response: Human-readable message describing the execution result
            observation: Optional pre-processed observation data for OSWorld tools.
                        Should contain base64-encoded screenshot and linearized a11y tree.
        """
        self.status = status
        self.response = response
        self.observation = observation or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format.

        Returns:
            Dict with 'status', 'response', and 'observation' keys
        """
        return {
            'status': self.status,
            'response': self.response,
            'observation': self.observation
        }

    def to_json(self) -> str:
        """
        Convert to JSON string format (for backward compatibility).

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __str__(self) -> str:
        """String representation returns JSON format."""
        return self.to_json()


class Tool(ABC):
    """Abstract base class for all tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> List[Dict[str, Any]]:
        """Tool parameters schema."""
        pass

    @abstractmethod
    def call(self, params: Union[str, dict], **kwargs) -> str:
        """Execute the tool with given parameters."""
        pass

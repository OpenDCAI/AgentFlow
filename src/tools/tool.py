import os
from typing import Dict, List, Any, Union
from abc import ABC, abstractmethod
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    def call(self, params: Union[str, dict], **kwargs) -> Union[str, Dict[str, Any]]:
        """
        Execute the tool with given parameters.
        
        Returns:
            A dictionary containing the execution result (recommended) or a JSON string.
            The dictionary should ideally follow this structure for OSWorld compatibility:
            {
                'status': 'success' | 'failed',
                'response': 'Human readable output',
                'observation': { ... } # Optional formatted observation
            }
        """
        pass
"""
Environment classes for AgentFlow - manages tools and configuration for agent environments.
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all available tools
from tools import (
    CalculatorTool,
    WebSearchTool, 
    WebVisitTool,
    # RAG tools will be imported conditionally
)


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


class Environment(ABC):
    """
    Abstract base class for agent environments.
    
    This class provides a unified interface for:
    - Tool registration and management
    - Configuration management (API keys, model settings, etc.)
    - Tool execution and schema generation
    """
    
    def __init__(self, 
                 model_name: str = "gpt-4.1-2025-04-14",
                 openai_api_key: Optional[str] = None,
                 openai_api_url: Optional[str] = None,
                 **kwargs):
        """
        Initialize the environment.
        
        Args:
            model_name: OpenAI model name to use
            openai_api_key: OpenAI API key (if None, will use env var)
            openai_api_url: OpenAI API URL (if None, will use env var)
            **kwargs: Additional configuration parameters
        """
        self.model_name = model_name
        self.tools: Dict[str, Tool] = {}
        self.tool_schemas: List[Dict[str, Any]] = []
        self.tool_descriptions: str = ""
        
        # Configuration
        self.config = {
            "openai_api_key": openai_api_key or os.environ.get("OPENAI_API_KEY", ""),
            "openai_api_url": openai_api_url or os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", "")),
            **kwargs
        }
        
        self._initialize_config()
        # Validate required configuration
        self._validate_config()
        
        # Initialize tools - to be implemented by subclasses
        self._initialize_tools()
    
    @property
    @abstractmethod
    def mode(self) -> str:
        """Return the environment mode name."""
        pass
    
    @abstractmethod
    def _initialize_tools(self):
        """Initialize tools specific to this environment. Must be implemented by subclasses."""
        pass
    
    def _validate_config(self):
        """Validate required configuration parameters."""
        if not self.config["openai_api_key"]:
            print("Warning: OPENAI_API_KEY is not set. Some tools may not work properly.")
        if not self.config["openai_api_url"]:
            print("Warning: OPENAI_API_URL or OPENAI_API_BASE is not set. Some tools may not work properly.")

    def _initialize_config(self):
        """Initialize configuration, including Docker and Vriture Machine."""
        pass

    def _generate_tool_metadata(self):
        """Generate tool schemas and descriptions."""
        self.tool_schemas = []
        descriptions = []
        
        for tool in self.tools.values():
            # Convert tool to JSON schema
            schema = self._convert_tool_to_schema(tool)
            self.tool_schemas.append(schema)
            
            # Add to descriptions
            descriptions.append(f"- {tool.name}: {tool.description}")
        
        self.tool_descriptions = "\n".join(descriptions)
    
    def register_tool(self, tool: Tool):
        """Register a tool in the environment."""
        self.tools[tool.name] = tool
        print(f"Registered tool: {tool.name}")
        # Regenerate metadata after adding tool
        self._generate_tool_metadata()
    
    def unregister_tool(self, tool_name: str):
        """Unregister a tool from the environment."""
        if tool_name in self.tools:
            del self.tools[tool_name]
            print(f"Unregistered tool: {tool_name}")
            # Regenerate metadata after removing tool
            self._generate_tool_metadata()
        else:
            print(f"Tool {tool_name} not found")
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self.tools.keys())
    
    def _convert_tool_to_schema(self, tool: Tool) -> Dict[str, Any]:
        """Convert a tool to OpenAI function calling schema."""
        required_params = [param['name'] for param in tool.parameters if param.get('required', False)]
        properties = {}
        
        for param in tool.parameters:
            properties[param['name']] = {
                "type": param['type'],
                "description": param['description']
            }
            if param['type'] == 'array':
                properties[param['name']]['items'] = {
                    "type": param['array_type']
                }
        
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required_params
                }
            }
        }
    
    def execute_tool(self, tool_name: str, params: Union[str, dict], **kwargs) -> str:
        """Execute a tool with given parameters."""
        tool = self.get_tool(tool_name)
        if not tool:
            return f"Tool '{tool_name}' not found"
        
        try:
            return tool.call(params, **kwargs)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get tool schemas for OpenAI function calling."""
        return self.tool_schemas
    
    def get_tool_descriptions(self) -> str:
        """Get tool descriptions for system prompts."""
        return self.tool_descriptions
    
    def update_config(self, **kwargs):
        """Update environment configuration."""
        self.config.update(kwargs)
        print(f"Updated configuration: {kwargs}")
    
    def get_config(self, key: str = None):
        """Get configuration value(s)."""
        if key:
            return self.config.get(key)
        return self.config.copy()
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get comprehensive environment information."""
        return {
            "mode": self.mode,
            "model_name": self.model_name,
            "tools": list(self.tools.keys()),
            "tool_count": len(self.tools),
            "config": self.config
        }
    
    def save_environment(self, filepath: str):
        """Save environment configuration to file."""
        env_data = {
            "mode": self.mode,
            "model_name": self.model_name,
            "config": self.config,
            "tools": list(self.tools.keys())
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(env_data, f, indent=2, ensure_ascii=False)
        
        print(f"Environment saved to {filepath}")
    
    def load_environment(self, filepath: str):
        """Load environment configuration from file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            env_data = json.load(f)
        
        # Update configuration
        self.model_name = env_data.get("model_name", self.model_name)
        self.config.update(env_data.get("config", {}))
        
        # Reinitialize tools
        self._initialize_tools()
        
        print(f"Environment loaded from {filepath}")


# Concrete Environment Implementations

class MathEnvironment(Environment):
    """Math environment with calculator tools."""
    
    @property
    def mode(self) -> str:
        return "math"
    
    def _initialize_tools(self):
        """Initialize math-specific tools."""
        self.register_tool(CalculatorTool())


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
            query_tool = QueryRAGIndexTool(self.rag_index)
            self.register_tool(query_tool)
        except ImportError:
            raise ImportError("RAG tools not available")


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
            "summary_model": self.config.get("web_visit_summary_model", "gpt-4.1-2025-04-14")
        }
        
        self.register_tool(WebSearchTool(**web_search_config))
        self.register_tool(WebVisitTool(**web_visit_config))


# Convenience functions for common use cases
def create_math_environment(**kwargs) -> MathEnvironment:
    """Create a math environment with calculator tools."""
    return MathEnvironment(**kwargs)


def create_python_environment(**kwargs) -> PythonEnvironment:
    """Create a Python environment with interpreter tools."""
    return PythonEnvironment(**kwargs)


def create_rag_environment(**kwargs) -> RAGEnvironment:
    """Create a RAG environment with retrieval tools."""
    return RAGEnvironment(**kwargs)


def create_web_environment(**kwargs) -> WebEnvironment:
    """Create a web environment with search and visit tools."""
    return WebEnvironment(**kwargs)


# Example usage
if __name__ == "__main__":
    # Example: Create different environments
    print("Creating math environment...")
    math_env = create_math_environment()
    print(f"Math environment info: {math_env.get_environment_info()}")
    
    print("\nCreating web environment...")
    web_env = create_web_environment(
        web_search_top_k=10,
        web_search_type="search"
    )
    print(f"Web environment info: {web_env.get_environment_info()}")
    
    # Example: Execute a tool
    print("\nTesting calculator tool...")
    result = math_env.execute_tool("calculator", {"expressions": ["2+2", "sqrt(16)"]})
    print(f"Calculator result: {result}")
    
    # Example: Direct instantiation
    print("\nDirect instantiation example...")
    math_env_direct = MathEnvironment(model_name="gpt-4")
    print(f"Direct math environment mode: {math_env_direct.mode}")
    print(f"Direct math environment tools: {math_env_direct.list_tools()}")

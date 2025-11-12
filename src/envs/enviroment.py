"""
Environment classes for AgentFlow - manages tools and configuration for agent environments.
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
import sys
import pdb
import bdb
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Note: Tool imports have been moved to individual environment files
# Each concrete environment (MathEnvironment, WebEnvironment, etc.)
# imports only the tools it needs

# Note: Trajectory data models (Observation, TrajectoryStep, TaskTrajectory)
# have been moved to envs.data_models module
# Import them from there if needed in specific environments


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
                 enable_terminal_bench: bool = False, # added for Terminal Bench
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
        self.config = {
            "openai_api_key": openai_api_key or os.environ.get("OPENAI_API_KEY", ""),
            "openai_api_url": openai_api_url or os.environ.get("OPENAI_API_URL", os.environ.get("OPENAI_API_BASE", "")),
            "enable_terminal_bench": enable_terminal_bench,
            "terminal_bench_images": kwargs.get("terminal_bench_images", ["tbench/ubuntu:latest"]),
            "container_timeout": kwargs.get("container_timeout", 300),
            "max_containers": kwargs.get("max_containers", 5),
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

    def get_action_space(self) -> Optional[str]:
        """
        Get the action space for this environment (if applicable).

        Returns:
            Action space string (e.g., "computer_13", "pyautogui") or None if not applicable.

        Note:
            Subclasses should override this method if they use action spaces.
            Default implementation returns None.
        """
        return None

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
        """Initialize configuration, including Docker and Virtual Machine."""
        # Check if Terminal Bench is required for this environment
        if not self.config.get("enable_terminal_bench", False):
            return
        
        import subprocess
        import shutil
        
        try:
            # 1. Check if Docker is installed
            if not shutil.which("docker"):
                print("Warning: Docker is not installed. Terminal Bench requires Docker.")
                print("Please install Docker from: https://docs.docker.com/get-docker/")
                self.config["terminal_bench_available"] = False
                return
            
            # 2. Check if Docker daemon is running
            try:
                subprocess.run(
                    ["docker", "info"],
                    check=True,
                    capture_output=True,
                    timeout=10
                )
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                print("Warning: Docker daemon is not running. Please start Docker.")
                self.config["terminal_bench_available"] = False
                return
            
            # 3. Check if Terminal Bench is installed
            try:
                result = subprocess.run(
                    ["tbench", "--version"],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                print(f"Terminal Bench installed: {result.stdout.strip()}")
            except (FileNotFoundError, subprocess.CalledProcessError):
                print("Terminal Bench not found. Installing...")
                try:
                    # Install Terminal Bench via pip
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "terminal-bench"],
                        check=True,
                        capture_output=True
                    )
                    print("Terminal Bench installed successfully.")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to install Terminal Bench: {e}")
                    self.config["terminal_bench_available"] = False
                    return
            
            # 4. Pull required Docker images
            print("Pulling Terminal Bench Docker images...")
            images = self.config.get("terminal_bench_images", ["tbench/ubuntu:latest"])
            
            for image in images:
                try:
                    print(f"Pulling {image}...")
                    subprocess.run(
                        ["docker", "pull", image],
                        check=True,
                        capture_output=True,
                        timeout=300  # 5 minutes timeout
                    )
                    print(f"Successfully pulled {image}")
                except subprocess.TimeoutExpired:
                    print(f"Timeout pulling {image}. Please pull manually.")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to pull {image}: {e}")
            
            # 5. Initialize Terminal Bench configuration
            tbench_config = {
                "docker_available": True,
                "images": images,
                "container_timeout": self.config.get("container_timeout", 300),
                "max_containers": self.config.get("max_containers", 5)
            }
            self.config["terminal_bench"] = tbench_config
            self.config["terminal_bench_available"] = True
            
            print("Terminal Bench environment initialized successfully.")
            
        except Exception as e:
            print(f"Error initializing Terminal Bench: {e}")
            self.config["terminal_bench_available"] = False

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
            if isinstance(e, bdb.BdbQuit):
                raise e
            return f"Error executing tool '{tool_name}': {str(e)}"
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get tool schemas for OpenAI function calling."""
        return self.tool_schemas
    
    def get_tool_descriptions(self) -> str:
        """Get tool descriptions for system prompts."""
        return self.tool_descriptions

    def get_system_prompt(self, task_question: str) -> str:
        """
        Get the complete system prompt for this environment.

        This method constructs the system prompt by:
        1. Selecting the appropriate prompt template based on mode and action_space
        2. Replacing placeholders with actual values (tool descriptions, passwords, etc.)
        3. Adding the task question

        Args:
            task_question: The task/question to be completed

        Returns:
            Complete system prompt string ready for LLM

        Note:
            Subclasses can override this method for custom prompt construction.
            Default implementation uses the prompts module.
        """
        from prompts import get_system_prompt as get_prompt_template

        # Get environment mode and action space
        environment_mode = self.mode
        action_space = self.get_action_space()

        # Get the appropriate system prompt template
        system_prompt_template = get_prompt_template(environment_mode, action_space)

        # Replace tool descriptions placeholder
        system_prompt = system_prompt_template.replace(
            "{tool_descriptions}",
            self.get_tool_descriptions()
        )

        # Replace environment-specific placeholders (can be overridden by subclasses)
        system_prompt = self._replace_prompt_placeholders(system_prompt)

        # Add task question
        system_prompt = system_prompt + f"\nYou are asked to complete the following task: {task_question}"

        return system_prompt

    def _replace_prompt_placeholders(self, prompt: str) -> str:
        """
        Replace environment-specific placeholders in the prompt.

        Args:
            prompt: Prompt template with placeholders

        Returns:
            Prompt with placeholders replaced

        Note:
            Subclasses should override this method to handle their specific placeholders.
            Default implementation does nothing.
        """
        return prompt

    def get_initial_observation(self, task_question: str) -> Optional[Dict[str, Any]]:
        """
        Get the initial observation for the task (if applicable).

        This method is called at the start of a task to gather initial state information
        that should be provided to the LLM along with the task question.

        Args:
            task_question: The task/question to be completed

        Returns:
            Dictionary containing initial observation data, or None if not applicable.
            Format depends on environment type:
            - For OSWorld: {"screenshot": base64_str, "a11y_tree": str, ...}
            - For other environments: None (no initial observation needed)

        Note:
            Subclasses should override this method if they need to provide
            initial observations (e.g., screenshot, state info).
        """
        return None

    def format_observation_for_message(self, observation: Any) -> List[Dict[str, Any]]:
        """
        Format observation data into message content parts for LLM.

        This method converts raw observation data into the format expected by
        the LLM conversation (text, images, etc.).

        Args:
            observation: Raw observation data from get_initial_observation()

        Returns:
            List of message content parts (dicts with "type" and data).
            Empty list if no observation or not applicable.

        Note:
            Subclasses should override this method to format their specific
            observation types.
        """
        return []

    def format_initial_observation_for_message(self, initial_obs: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format initial observation from env_task_init() into message content parts.

        This is a convenience method that handles the simplified observation format
        commonly returned by env_task_init() in various environments.

        Args:
            initial_obs: Initial observation dict from env_task_init()
                        Default format: {'text': str, 'image': str (base64)}
                        (Format may vary by environment)

        Returns:
            List of message content parts for LLM conversation.
            Empty list if no observation or not applicable.

        Note:
            Default implementation returns empty list. Subclasses should override
            this method if they provide initial observations (e.g., OSWorld).
        """
        return []

    # ========================================================================
    # Task Lifecycle Methods
    # ========================================================================
    # These methods manage the lifecycle of individual tasks within a benchmark

    def env_task_init(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Initialize environment for a new task and return initial observation.

        This method performs:
        1. Reset environment for the task
        2. Start recording (if applicable)
        3. Clear trajectory storage
        4. Get and return initial observation

        Args:
            task: Task dictionary with 'id', 'question', and optionally 'metadata'

        Returns:
            Initial observation dictionary, or None if not applicable.
            For OSWorld: {'text': str, 'image': base64_str}
            For other environments: None

        Note:
            Default implementation returns None.
            Subclasses should override to provide initial observations (e.g., OSWorld).
        """
        return None

    def env_task_end(self, task_id: str, task_output_dir: Optional[str] = None, final_answer: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Finalize task execution: end recording, save trajectory, and return final result.

        This method performs:
        1. End recording and save video (if applicable)
        2. Save trajectory data to task_output_dir
        3. Determine final answer (LLM output or environment evaluation)
        4. Clear task-specific data

        Args:
            task_id: Task identifier
            task_output_dir: Directory to save recordings and trajectory
            final_answer: LLM's final answer from conversation

        Returns:
            Result dictionary with final answer:
            {
                "answer": str  # Final answer for this task
            }

            **For environments with internal evaluation** (e.g., OSWorld):
            - Ignores LLM's final_answer
            - Returns evaluation score as answer: {"answer": "0.85"}

            **For general environments** (math, rag, web, etc.):
            - Returns LLM's final_answer: {"answer": final_answer}

        Note:
            - OSWorld: Uses environment evaluator, ignores LLM output
            - Other envs: Uses LLM output as answer
            - Returned answer will be used in benchmark.evaluate()
            - Subclasses should override if they have internal evaluation
        """
        # Default implementation: return LLM's answer
        return {"answer": final_answer} if final_answer is not None else None

    def env_start(self) -> None:
        """
        Start the environment (called once at benchmark start).

        This is called in run_benchmark before processing any tasks.
        Use this to initialize resources needed across all tasks.

        Note:
            Default implementation does nothing.
            Subclasses can override for environment-wide initialization.
        """
        pass

    def env_close(self) -> None:
        """
        Close and cleanup the environment (called once at benchmark end).

        This is called in run_benchmark after all tasks complete.
        Use this to cleanup resources used across all tasks.

        Note:
            Default implementation does nothing.
            Subclasses should override if they need cleanup (e.g., OSWorld).
        """
        pass

    # ========================================================================
    # Legacy Task Lifecycle Methods (kept for backward compatibility)
    # ========================================================================
    # These methods are still used internally by env_task_init/env_task_end

    def reset_for_task(self, task: Dict[str, Any]) -> None:
        """Reset environment for a new task (legacy method, use env_task_init instead)."""
        pass

    def start_task_recording(self) -> None:
        """Start recording task execution (legacy method, use env_task_init instead)."""
        pass

    def end_task_recording(self, output_path: str) -> None:
        """End task recording and save to file (legacy method, use env_task_end instead)."""
        pass

    def evaluate_task(self) -> float:
        """Evaluate task execution result (legacy method, use env_task_end instead)."""
        return 0.0

    def get_task_output_dir(self, base_output_dir: str, task_id: str, model_name: str) -> Optional[str]:
        """
        Get the output directory for a specific task.

        This determines where task-specific files (recordings, trajectories, etc.)
        should be saved.

        Args:
            base_output_dir: Base output directory (e.g., "results")
            task_id: Task identifier
            model_name: Model name being used

        Returns:
            Path to task output directory, or None if not applicable

        Note:
            Default implementation returns None (no task-specific directory).
            Subclasses should override if they need per-task directories (e.g., OSWorld).
        """
        return None

    def needs_trajectory_saving(self) -> bool:
        """
        Check if this environment needs trajectory saving.

        Returns:
            True if trajectory (screenshots, observations) should be saved

        Note:
            Default implementation returns False.
            Subclasses should override if they need trajectory saving (e.g., OSWorld).
        """
        return False

    def has_internal_evaluation(self) -> bool:
        """
        Check if this environment has internal evaluation capability.

        Returns:
            True if environment can evaluate task results internally (e.g., OSWorld)
            False if evaluation should use LLM's final answer (default)

        Note:
            Default implementation returns False (use LLM output as answer).
            Subclasses should override to return True if they have internal evaluators.
        """
        return False

    def close(self) -> None:
        """
        Close and cleanup the environment.

        This is called ONCE after ALL tasks complete, not between tasks.
        Use reset_for_task() between tasks instead.

        Note:
            Default implementation does nothing.
            Subclasses should override if they need cleanup (e.g., OSWorld).
        """
        pass

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
            local_search_tool = QueryRAGIndexTool(self.rag_index)
            self.register_tool(local_search_tool)
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
            "top_k": self.config.get("web_search_top_k", 10),
            "max_workers": self.config.get("web_search_max_workers", 5)
        }
            
        # Configure web visit tool
        web_visit_config = {
            "summary_model": self.config.get("web_visit_summary_model", "gpt-4.1-2025-04-14"),
        }
        
        self.register_tool(WebSearchTool(**web_search_config))
        self.register_tool(WebVisitTool(**web_visit_config))


class TBenchEnvironment(Environment): # for Terminal Bench
    """
    A minimal concrete environment for configuration-only scenarios (e.g., initializing Terminal Bench)
    without registering any tools. Use this when you only need environment setup but no specific tools.
    """

    @property
    def mode(self) -> str:
        return "tbench"

    def _initialize_tools(self):
        # No tools by default; suitable for bench/config-only usage
        self.tools = {}
        self._generate_tool_metadata()


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
        web_search_top_k=10
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
# Note: Concrete environment implementations have been moved to separate files:
# - MathEnvironment -> math_environment.py
# - PythonEnvironment -> python_environment.py
# - RAGEnvironment -> rag_environment.py
# - WebEnvironment -> web_environment.py
# - TBenchEnvironment -> tbench_environment.py

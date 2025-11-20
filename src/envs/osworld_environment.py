# -*- coding: utf-8 -*-
"""
OSWorld Environment - Desktop automation environment using DesktopEnv.

This environment provides interface for OSWorld desktop automation tasks.
It wraps the DesktopEnv from utils/desktop_env and exposes unified methods
for task execution, observation retrieval, evaluation, and recording.
"""

import os
import sys
import json
import base64
from typing import Any, Dict, Optional, List, Union

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from envs.enviroment import Environment
from envs.data_models import Observation

# Import DesktopEnv from utils (already migrated from OSWorld)
from utils.desktop_env.desktop_env import DesktopEnv


class OSWorldEnvironment(Environment):
    """
    OSWorld desktop automation environment.

    This environment manages:
    - DesktopEnv lifecycle (initialization, reset, close)
    - Desktop action execution via DesktopActionTool
    - Observation retrieval and recording control
    - Task evaluation

    External code should ONLY interact with DesktopEnv through this class's
    封装 methods (reset/step/get_obs/evaluate/start_recording/end_recording/close).
    Never access self._desktop_env directly from outside.
    """

    def __init__(self, **kwargs):
        """
        Initialize OSWorld environment.

        Args:
            **kwargs: Configuration parameters including:
                Required:
                - path_to_vm: Path to VM image

                Optional with defaults:
                - provider_name: VM provider (default: "vmware")
                - action_space: Action space type (default: "pyautogui")
                - observation_type: Observation type (default: "screenshot_a11y_tree")
                - screen_width: Screen width in pixels (default: 1920)
                - screen_height: Screen height in pixels (default: 1080)
                - headless: Run in headless mode (default: False)
                - os_type: OS type (default: "Ubuntu")
                - client_password: VM client password for sudo operations (default: "password")
                - sleep_after_execution: Sleep time after each action in seconds (default: 2)

                Optional (only used if provided):
                - snapshot_name: VM snapshot name
                - require_terminal: Require terminal access
        """
        self._desktop_env: Optional[DesktopEnv] = None
        self._tool_response_use_dict: bool = False

        # Trajectory storage for current task
        self._current_trajectory: List[Dict[str, Any]] = []
        self._current_task_id: Optional[str] = None

        super().__init__(**kwargs)

    def enable_tool_response_dict(self, enabled: bool) -> None:
        """Enable/disable returning tool responses as dict instead of JSON string."""
        self._tool_response_use_dict = enabled

    @property
    def mode(self) -> str:
        """Return the environment mode name."""
        return "osworld"

    def get_action_space(self) -> str:
        """
        Get the action space mode for this environment.

        Returns:
            Action space string (e.g., "computer_13", "pyautogui")
        """
        return self.config.get("osworld", {}).get("action_space", "computer_13")

    def _replace_prompt_placeholders(self, prompt: str) -> str:
        """
        Replace OSWorld-specific placeholders in the prompt.

        Args:
            prompt: Prompt template with placeholders

        Returns:
            Prompt with {CLIENT_PASSWORD} replaced
        """
        # Replace {CLIENT_PASSWORD} placeholder if present
        if "{CLIENT_PASSWORD}" in prompt:
            client_password = self.config.get("osworld", {}).get("client_password", "password")
            prompt = prompt.replace("{CLIENT_PASSWORD}", client_password)

        return prompt

    def get_initial_observation(self, task_question: str) -> Optional[Dict[str, Any]]:
        """
        Get the initial observation for OSWorld task.

        This retrieves the current state of the desktop (screenshot + accessibility tree)
        at the start of the task.

        Args:
            task_question: The task/question to be completed (not used, kept for interface consistency)

        Returns:
            Dictionary with raw observation data:
            {
                'screenshot': bytes,
                'accessibility_tree': str or dict
            }
        """
        if not self._desktop_env:
            print("Warning: DesktopEnv not initialized, cannot get initial observation")
            return None

        print(f"📷 Getting initial observation from desktop environment...")
        return self.get_obs()

    def format_observation_for_message(self, observation: Any) -> List[Dict[str, Any]]:
        """
        Format OSWorld observation into message content parts for LLM.

        Converts raw observation (screenshot bytes + accessibility tree) into
        formatted message parts (text + base64 image).

        Args:
            observation: Raw observation dict from get_obs()

        Returns:
            List of message content parts:
            [
                {"type": "text", "text": "Initial observation text..."},
                {"type": "text", "text": "Accessibility tree:\n..."},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64,...", "detail": "high"}}
            ]
        """
        if not observation:
            return []

        content_parts = []

        # Process observation using existing method
        formatted_obs = self._format_observation_for_llm(observation)

        # Add introduction text
        content_parts.append({
            "type": "text",
            "text": "The following are the computer's initial observations.\n"
        })

        # Add accessibility tree if available
        if formatted_obs.get('a11y_tree'):
            content_parts.append({
                "type": "text",
                "text": f"\nAccessibility tree as below:\n{formatted_obs['a11y_tree']}\n"
            })

        # Add screenshot image if available
        if formatted_obs.get('screenshot'):
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{formatted_obs['screenshot']}",
                    "detail": "high"
                }
            })

        return content_parts

    def format_initial_observation_for_message(
        self,
        initial_obs: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Format initial observation from env_task_init() into message content parts.

        This method handles the simplified observation format returned by env_task_init(),
        which uses {'text': str, 'image': str} format (where 'image' is base64-encoded).

        Args:
            initial_obs: Initial observation dict from env_task_init()
                        Format: {'text': str, 'image': str (base64)}

        Returns:
            List of message content parts for LLM conversation:
            [
                {"type": "text", "text": "The following are the computer's initial observations.\n"},
                {"type": "text", "text": "\nAccessibility tree as below:\n..."},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64,...", ...}}
            ]
        """
        if not initial_obs:
            return []

        content_parts = []

        # Add introduction text
        content_parts.append({
            "type": "text",
            "text": "The following are the computer's initial observations.\n"
        })

        # Add accessibility tree (text)
        if initial_obs.get('text'):
            content_parts.append({
                "type": "text",
                "text": f"\nAccessibility tree as below:\n{initial_obs['text']}\n"
            })

        # Add screenshot (image)
        if initial_obs.get('image'):
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{initial_obs['image']}",
                    "detail": "high"
                }
            })

        return content_parts

    def _format_observation_for_llm(self, obs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method to format raw observation for LLM (extracted from existing code).

        Args:
            obs: Raw observation dict

        Returns:
            Formatted observation dict with base64 screenshot and linearized a11y tree
        """
        # Process accessibility tree
        a11y_tree = obs.get("accessibility_tree", {})
        max_tokens = self.config.get("osworld", {}).get("a11y_tree_max_tokens", 10000)
        linearized_a11y_tree = self._linearize_accessibility_tree(a11y_tree)
        linearized_a11y_tree = self._trim_accessibility_tree(linearized_a11y_tree, max_tokens)

        # Encode screenshot to base64
        base64_image = self._encode_image(obs.get("screenshot", b""))

        return {
            'screenshot': base64_image,
            'a11y_tree': linearized_a11y_tree,
        }

    def format_observation_by_type(
        self,
        raw_obs: Dict[str, Any],
        output_format: str = "dict"
    ) -> Union[Dict[str, Any], List[Observation]]:
        """
        Format observation based on observation_type configuration, supporting multiple output formats.

        This method respects the observation_type setting (screenshot, a11y_tree, or screenshot_a11y_tree)
        and returns observations in the requested output format.

        Args:
            raw_obs: Raw observation dict from get_obs() containing:
                - 'screenshot': bytes (raw screenshot data)
                - 'accessibility_tree': str or dict (raw a11y tree data)
            output_format: Output format:
                - "dict": Dict format for tool return values
                  Returns: {'text': str, 'image': str} (only includes enabled observation types)
                - "observation_list": List of Observation objects
                  Returns: [Observation(...), ...] (only includes enabled observation types)
                - "openai_message": List of dicts for OpenAI message format
                  Returns: [{"type": "text", ...}, {"type": "image_url", ...}] (only includes enabled types)

        Returns:
            Formatted observation in the specified output format, containing only the
            observation types enabled by observation_type configuration.

        Examples:
            >>> # With observation_type="screenshot_a11y_tree" (both enabled)
            >>> obs = env.format_observation_by_type(raw_obs, output_format="dict")
            >>> # {'text': '...a11y tree...', 'image': '...base64...'}

            >>> # With observation_type="screenshot" (only screenshot)
            >>> obs = env.format_observation_by_type(raw_obs, output_format="dict")
            >>> # {'image': '...base64...'}

            >>> # With observation_type="a11y_tree" (only accessibility tree)
            >>> obs = env.format_observation_by_type(raw_obs, output_format="dict")
            >>> # {'text': '...a11y tree...'}

            >>> # Observation list output (respects observation_type)
            >>> obs_list = env.format_observation_by_type(raw_obs, output_format="observation_list")
            >>> # [Observation(type="text", ...), Observation(type="image", ...)]
            >>> # or [Observation(type="text", ...)] if observation_type="a11y_tree"
            >>> # or [Observation(type="image", ...)] if observation_type="screenshot"
        """
        if not raw_obs:
            # Return appropriate empty value based on output format
            if output_format == "dict":
                return {}
            elif output_format == "observation_list":
                return []
            elif output_format == "openai_message":
                return []
            else:
                raise ValueError(f"Unknown output_format: {output_format}")

        # Get observation_type from configuration
        observation_type = self.config.get("osworld", {}).get("observation_type", "screenshot_a11y_tree")

        # Determine which observation types to include
        include_screenshot = observation_type in ["screenshot", "screenshot_a11y_tree", "som"]
        include_a11y_tree = observation_type in ["a11y_tree", "screenshot_a11y_tree", "som"]

        # Format observation to get base64 image and linearized a11y tree
        formatted_obs = self._format_observation_for_llm(raw_obs)
        base64_image = formatted_obs.get('screenshot', '') if include_screenshot else ''
        linearized_a11y_tree = formatted_obs.get('a11y_tree', '') if include_a11y_tree else ''

        # Return in requested output format
        if output_format == "dict":
            # Dict format: {'text': str, 'image': str}
            # Only includes enabled observation types
            result = {}
            if include_a11y_tree and linearized_a11y_tree:
                result['text'] = linearized_a11y_tree
            if include_screenshot and base64_image:
                result['image'] = base64_image
            return result

        elif output_format == "observation_list":
            # List[Observation] format: unified interface
            # Only includes enabled observation types
            from datetime import datetime

            observation_objects = []

            # Add text observation (accessibility tree) if enabled
            if include_a11y_tree and linearized_a11y_tree:
                text_obs = Observation(
                    type="text",
                    content=linearized_a11y_tree,
                    timestamp=datetime.now().isoformat(),
                    metadata={"source": "accessibility_tree", "observation_type": observation_type}
                )
                observation_objects.append(text_obs)

            # Add image observation (screenshot) if enabled
            if include_screenshot and base64_image:
                image_obs = Observation(
                    type="image",
                    content=base64_image,  # base64 string
                    timestamp=datetime.now().isoformat(),
                    metadata={"format": "png", "encoding": "base64", "observation_type": observation_type}
                )
                observation_objects.append(image_obs)

            return observation_objects

        elif output_format == "openai_message":
            # List[Dict] format: OpenAI message content parts
            # Only includes enabled observation types
            content_parts = []

            # Add text part (accessibility tree) if enabled
            if include_a11y_tree and linearized_a11y_tree:
                content_parts.append({
                    "type": "text",
                    "text": f"\n--- Current Page State ---\n{linearized_a11y_tree}"
                })

            # Add image part (screenshot) if enabled
            if include_screenshot and base64_image:
                content_parts.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}",
                        "detail": "high"
                    }
                })

            return content_parts

        else:
            raise ValueError(f"Unknown output_format: {output_format}. Must be 'dict', 'observation_list', or 'openai_message'")

    def _initialize_config(self):
        """
        Initialize and prepare OSWorld-specific configuration.

        This method is called by the base class __init__ BEFORE _validate_config().
        It prepares configuration parameters but does NOT create DesktopEnv yet.

        Overrides the base class _initialize_config to add OSWorld-specific config preparation.
        """
        # Call parent's _initialize_config first (for Terminal Bench, etc.)
        super()._initialize_config()

        # Build OSWorld-specific configuration in a separate namespace
        observation_type = self.config.get("observation_type", "screenshot_a11y_tree")

        osworld_config = {
            # VM-related parameters (will be passed to DesktopEnv)
            "path_to_vm": self.config.get("path_to_vm"),
            "provider_name": self.config.get("provider_name", "vmware"),
            "action_space": self.config.get("action_space", "computer_13"),
            "screen_width": self.config.get("screen_width", 1920),
            "screen_height": self.config.get("screen_height", 1080),
            "headless": self.config.get("headless", False),
            "os_type": self.config.get("os_type", "Ubuntu"),
            "client_password": self.config.get("client_password", "password"),
            "snapshot_name": self.config.get("snapshot_name"),
            "require_terminal": self.config.get("require_terminal"),

            # Runtime configuration (NOT passed to DesktopEnv)
            "observation_type": observation_type,
            "sleep_after_execution": self.config.get("sleep_after_execution", 2),

            # Derived values
            "require_a11y_tree": observation_type in ["a11y_tree", "screenshot_a11y_tree", "som"],
        }

        # Store OSWorld config in dedicated namespace
        self.config["osworld"] = osworld_config
        # Mark as not yet available (will be set to True after DesktopEnv is created)
        self.config["osworld_available"] = False

        # Note: DesktopEnv creation is deferred to _initialize_tools() after validation

    def _validate_config(self):
        """
        Validate OSWorld-specific configuration parameters.

        This method is called by the base class __init__ AFTER _initialize_config().
        It validates all required and optional parameters.

        Overrides base class method to add validation for required OSWorld parameters.
        """
        # Call parent's validation first (OpenAI API keys, etc.)
        super()._validate_config()

        # Get OSWorld config namespace
        osworld_config = self.config.get("osworld", {})

        # Validate provider_name
        provider_name = osworld_config["provider_name"]
        valid_providers = ["vmware", "virtualbox", "aws", "gcp", "azure", "aliyun", "volcengine", "docker"]
        if provider_name not in valid_providers:
            raise ValueError(
                f"Invalid provider_name '{provider_name}'. "
                f"Must be one of: {', '.join(valid_providers)}"
            )

        # Validate observation_type
        observation_type = osworld_config["observation_type"]
        valid_obs_types = ["screenshot", "screenshot_a11y_tree", "a11y_tree", "som"]
        if observation_type not in valid_obs_types:
            raise ValueError(
                f"Invalid observation_type '{observation_type}'. "
                f"Must be one of: {', '.join(valid_obs_types)}"
            )

        # Validate action_space
        action_space = osworld_config["action_space"]
        valid_action_spaces = ["pyautogui", "computer_13", "claude_computer_use"]
        if action_space not in valid_action_spaces:
            raise ValueError(
                f"Invalid action_space '{action_space}'. "
                f"Must be one of: {', '.join(valid_action_spaces)}"
            )

        # Validate screen dimensions
        screen_width = osworld_config["screen_width"]
        screen_height = osworld_config["screen_height"]
        if screen_width <= 0 or screen_height <= 0:
            raise ValueError(
                f"Invalid screen dimensions: {screen_width}x{screen_height}. "
                f"Both width and height must be positive integers."
            )

        print("OSWorld configuration validation passed ✓")

    def _initialize_tools(self):
        """
        Initialize OSWorld-specific tools and underlying environment.

        This method is called by the base class __init__ AFTER _validate_config().
        It creates the DesktopEnv instance and registers tools based on action_space mode.

        Supports two action space modes:
        - computer_13: Structured action tools (mouse, keyboard, control)
        - pyautogui: Python script execution tool + control tools

        Both modes share common control tools (WAIT, DONE, FAIL).

        Note: Config is already validated at this point, safe to create DesktopEnv.
        
        Note: If defer_init=True was used, this method will only be called when env_start() is invoked.
        This allows parallel mode to avoid creating VM instances in the main process.
        """
        # Create DesktopEnv instance (this will start the VM)
        try:
            print("Starting DesktopEnv initialization...")
            self._init_desktop_env_from_config()
            print("DesktopEnv initialization completed")
        except Exception as e:
            print(f"❌ Failed to initialize DesktopEnv: {e}")
            import traceback
            traceback.print_exc()
            raise

        # Mark OSWorld as available after successful initialization
        self.config["osworld_available"] = True
        print("OSWorld environment initialized successfully ✓")

        # Get action space mode from config
        action_space = self.config.get("osworld", {}).get("action_space", "computer_13")

        # Register tools based on action space mode
        if action_space == "computer_13":
            self._register_computer13_tools()
        elif action_space == "pyautogui":
            self._register_pyautogui_tools()
        else:
            # For other action spaces (e.g., claude_computer_use), fall back to computer_13
            print(f"⚠️  Action space '{action_space}' not fully implemented, using computer_13 tools")
            self._register_computer13_tools()

        print(f"Registered {len(self.tools)} OSWorld desktop automation tools for '{action_space}' mode")

    def _register_computer13_tools(self):
        """
        Register computer_13 action space tools.

        This includes structured tools for:
        - Mouse operations (move, click, drag, etc.)
        - Keyboard operations (type, press, hotkey, etc.)
        - Scroll operations
        - Control signals (WAIT, DONE, FAIL)

        Total: 13 tools covering all computer_13 action types.
        """
        # Lazy import to avoid circular dependency
        from tools.osworld_tools import (
            # Mouse tools
            MouseMoveTool,
            MouseClickTool,
            MouseRightClickTool,
            MouseDoubleClickTool,
            MouseButtonTool,
            MouseDragTool,
            # Scroll tool
            ScrollTool,
            # Keyboard tools
            TypeTool,
            KeyPressTool,
            KeyHoldTool,
            HotkeyTool,
            # Control tool
            ControlTool
        )

        print("📦 Registering computer_13 tools...")

        # Mouse tools (6 tools covering 8 action types)
        self.register_tool(MouseMoveTool(self))          # MOVE_TO
        self.register_tool(MouseClickTool(self))         # CLICK
        self.register_tool(MouseRightClickTool(self))    # RIGHT_CLICK
        self.register_tool(MouseDoubleClickTool(self))   # DOUBLE_CLICK
        self.register_tool(MouseButtonTool(self))        # MOUSE_DOWN, MOUSE_UP
        self.register_tool(MouseDragTool(self))          # DRAG_TO

        # Scroll tool (1 tool)
        self.register_tool(ScrollTool(self))             # SCROLL

        # Keyboard tools (4 tools covering 4 action types)
        self.register_tool(TypeTool(self))               # TYPING
        self.register_tool(KeyPressTool(self))           # PRESS
        self.register_tool(KeyHoldTool(self))            # KEY_DOWN, KEY_UP
        self.register_tool(HotkeyTool(self))             # HOTKEY

        # Control tool (1 tool covering 3 control actions)
        self.register_tool(ControlTool(self))            # WAIT, DONE, FAIL

        print("✓ computer_13 tools registered")

    def _register_pyautogui_tools(self):
        """
        Register pyautogui action space tools.

        This includes:
        - Python script execution tool (for pyautogui commands)
        - Control signals (WAIT, DONE, FAIL) - shared with computer_13

        Total: 2 tools (ExecutePythonScriptTool + ControlTool)

        Key difference from computer_13:
        - Single ExecutePythonScriptTool replaces all mouse/keyboard/scroll tools
        - Allows direct execution of pyautogui Python code
        - More flexible but requires users to write code
        """
        # Lazy import to avoid circular dependency
        from tools.osworld_tools import (
            ExecutePythonScriptTool,
            ControlTool
        )

        print("📦 Registering pyautogui tools...")

        # Python script execution tool (replaces all structured action tools)
        self.register_tool(ExecutePythonScriptTool(self))  # Python script execution

        # Control tool (shared with computer_13)
        self.register_tool(ControlTool(self))              # WAIT, DONE, FAIL

        print("✓ pyautogui tools registered")
    
    def _register_tools_without_desktop_env(self):
        """
        注册工具但不创建新的DesktopEnv(用于VM池模式)
        
        当使用VM池时,DesktopEnv已经存在,只需要注册工具即可
        """
        if self._desktop_env is None:
            raise ValueError("DesktopEnv must be set before calling this method")
        
        # 获取action space模式
        action_space = self.config.get("osworld", {}).get("action_space", "computer_13")
        
        # 根据action space注册工具
        if action_space == "computer_13":
            self._register_computer13_tools()
        elif action_space == "pyautogui":
            self._register_pyautogui_tools()
        else:
            print(f"⚠️  Action space '{action_space}' not fully implemented, using computer_13 tools")
            self._register_computer13_tools()
        
        print(f"Registered {len(self.tools)} OSWorld desktop automation tools for '{action_space}' mode")

    def _init_desktop_env_from_config(self):
        """
        Initialize DesktopEnv from configuration.

        Reads VM and environment settings from self.config["osworld"] namespace
        and creates the underlying DesktopEnv instance.

        Note: Config is already validated by _validate_config() before this method is called.
        """
        # Get OSWorld configuration from dedicated namespace
        osworld_config = self.config["osworld"]

        # Extract VM-related parameters for DesktopEnv
        provider_name = osworld_config["provider_name"]
        path_to_vm = osworld_config["path_to_vm"]
        action_space = osworld_config["action_space"]
        screen_width = osworld_config["screen_width"]
        screen_height = osworld_config["screen_height"]
        headless = osworld_config["headless"]
        os_type = osworld_config["os_type"]
        client_password = osworld_config["client_password"]
        require_a11y_tree = osworld_config["require_a11y_tree"]

        # Extract runtime configuration (not passed to DesktopEnv)
        observation_type = osworld_config["observation_type"]
        sleep_after_execution = osworld_config["sleep_after_execution"]

        print(f"Initializing DesktopEnv with:")
        print(f"  Provider: {provider_name}")
        print(f"  VM Path: {path_to_vm}")
        print(f"  Action Space: {action_space}")
        print(f"  Observation Type: {observation_type}")
        print(f"  Screen Size: {screen_width}x{screen_height}")
        print(f"  Headless: {headless}")
        print(f"  Require A11y Tree: {require_a11y_tree}")
        print(f"  Client Password: {'*' * len(client_password)}")
        print(f"  Sleep After Execution: {sleep_after_execution}s")

        # Build kwargs for DesktopEnv with VM-related parameters only
        desktop_env_kwargs = {
            "provider_name": provider_name,
            "path_to_vm": path_to_vm,
            "action_space": action_space,
            "screen_size": (screen_width, screen_height),
            "headless": headless,
            "require_a11y_tree": require_a11y_tree,
            "os_type": os_type,
            "client_password": client_password,
        }

        # Add optional VM parameters if provided
        snapshot_name = osworld_config.get("snapshot_name")
        require_terminal = osworld_config.get("require_terminal")

        if snapshot_name is not None:
            desktop_env_kwargs["snapshot_name"] = snapshot_name
            print(f"  Snapshot: {snapshot_name}")

        if require_terminal is not None:
            desktop_env_kwargs["require_terminal"] = require_terminal
            print(f"  Require Terminal: {require_terminal}")

        # Create DesktopEnv instance
        self._desktop_env = DesktopEnv(**desktop_env_kwargs)

        print(f"DesktopEnv initialized successfully")

    # ---- 封装 Methods for External Access ----
    # These methods provide the ONLY interface for interacting with DesktopEnv.
    # External code (runner, tools) must use these instead of accessing _desktop_env.

    def reset(self, task_config: Dict[str, Any]):
        """
        Reset environment for a new task.

        Args:
            task_config: Task configuration with 'id', 'instruction', 'config', etc.

        Returns:
            Initial observation from DesktopEnv
        """
        if not self._desktop_env:
            raise ValueError("DesktopEnv not initialized")

        print(f"Resetting environment for task: {task_config.get('id', 'unknown')}")
        return self._desktop_env.reset(task_config=task_config)

    def step(self, action: str, pause: float = 2):
        """
        Execute an action in the environment.

        Args:
            action: Action string (pyautogui command or WAIT/DONE/FAIL)
            pause: Pause duration after action (seconds)

        Returns:
            Tuple of (observation, reward, done, info)
        """
        if not self._desktop_env:
            raise ValueError("DesktopEnv not initialized")

        return self._desktop_env.step(action, pause=pause)

    def get_obs(self) -> Dict[str, Any]:
        """
        Get current observation from environment.

        Returns:
            Dictionary with 'screenshot' (bytes) and 'accessibility_tree' (str)
        """
        if not self._desktop_env:
            raise ValueError("DesktopEnv not initialized")

        # Call internal _get_obs method
        obs = self._desktop_env._get_obs()

        if obs is None:
            return {}

        if isinstance(obs, dict):
            return obs

        # Some legacy controllers may return JSON strings; attempt to decode
        if isinstance(obs, (str, bytes, bytearray)):
            try:
                decoded = json.loads(obs) if isinstance(obs, str) else json.loads(obs.decode("utf-8"))
                if isinstance(decoded, dict):
                    return decoded
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

        print(f"Warning: Unexpected observation type {type(obs)} from DesktopEnv._get_obs(), returning empty dict")
        return {}

    def evaluate(self) -> float:
        """
        Evaluate current state against task goal.

        Returns:
            Score (float) indicating task completion success
        """
        if not self._desktop_env:
            raise ValueError("DesktopEnv not initialized")

        score = self._desktop_env.evaluate()
        return float(score)

    def start_recording(self):
        """
        Start screen recording.

        Should be called after reset and before task execution begins.
        """
        if not self._desktop_env:
            raise ValueError("DesktopEnv not initialized")

        self._desktop_env.controller.start_recording()

    def end_recording(self, output_path: str):
        """
        End screen recording and save to file.

        Args:
            output_path: Path where recording should be saved (e.g., "recording.mp4")

        Should be called after task evaluation completes.
        """
        if not self._desktop_env:
            raise ValueError("DesktopEnv not initialized")

        self._desktop_env.controller.end_recording(output_path)

    def _encode_image(self, image_content: bytes) -> str:
        """Encode image bytes to base64 string."""
        if not image_content:
            return ""
        return base64.b64encode(image_content).decode('utf-8')

    def _linearize_accessibility_tree(self, accessibility_tree: Dict[str, Any]) -> str:
        """
        Convert accessibility tree to linearized string format.

        Simplified implementation - converts tree structure to readable text.
        For full OSWorld compatibility, this should match the original implementation.
        """
        def _traverse_tree(node, depth=0):
            """Recursively traverse and format tree nodes."""
            lines = []
            indent = "  " * depth

            # Get node information
            role = node.get("role", "unknown")
            name = node.get("name", "")
            description = node.get("description", "")

            # Format node line
            node_info = f"{indent}[{role}]"
            if name:
                node_info += f" {name}"
            if description:
                node_info += f" - {description}"

            lines.append(node_info)

            # Process children
            children = node.get("children", [])
            for child in children:
                if isinstance(child, dict):
                    lines.extend(_traverse_tree(child, depth + 1))

            return lines

        if not accessibility_tree:
            return ""

        # Accept pre-formatted string trees (e.g., XML returned by controller) directly
        if isinstance(accessibility_tree, (str, bytes, bytearray)):
            try:
                # Normalize bytes to string if needed
                text = accessibility_tree.decode("utf-8") if isinstance(accessibility_tree, (bytes, bytearray)) else accessibility_tree
                return text
            except UnicodeDecodeError:
                # Fall back to repr to avoid crashing
                return repr(accessibility_tree)

        if not isinstance(accessibility_tree, dict):
            return str(accessibility_tree)

        tree_lines = _traverse_tree(accessibility_tree)
        return "\n".join(tree_lines)

    def _trim_accessibility_tree(self, linearized_tree: str, max_tokens: int) -> str:
        """
        Trim accessibility tree to fit within max tokens.

        Args:
            linearized_tree: Linearized tree string
            max_tokens: Maximum number of tokens (approximate)

        Returns:
            Trimmed tree string
        """
        # Approximate: 1 token ≈ 4 characters
        max_chars = max_tokens * 4

        if len(linearized_tree) <= max_chars:
            return linearized_tree

        # Trim and add truncation notice
        return linearized_tree[:max_chars] + "\n...[accessibility tree truncated]"

    # ========================================================================
    # Task Lifecycle Methods (Override from Environment base class)
    # ========================================================================

    def env_task_init(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Initialize OSWorld environment for a new task and return initial observation.

        This method performs:
        1. Reset environment for the task
        2. Start screen recording
        3. Clear trajectory storage
        4. Get initial observation (respects observation_type configuration)

        Args:
            task: Task dictionary with 'id', 'question', 'answer', 'metadata'

        Returns:
            Initial observation dictionary (respects observation_type):
            {
                'text': str,  # Linearized accessibility tree (if observation_type includes a11y_tree)
                'image': str  # Base64-encoded screenshot (if observation_type includes screenshot)
            }
            Keys are only included if enabled by observation_type configuration.
        """
        task_id = task.get('id', 'unknown')
        print(f"   Initializing OSWorld environment for task {task_id}...")

        # Store current task ID
        self._current_task_id = task_id

        # Reset environment for the task
        print(f"   Resetting desktop environment...")
        self.reset(task)

        # Start screen recording (optional, can be disabled)
        # Check if recording is enabled (default: True for backward compatibility)
        enable_recording = self.config.get("osworld", {}).get("enable_recording", True)
        
        if enable_recording:
            print(f"   Starting screen recording...")
            try:
                self.start_recording()
            except Exception as e:
                print(f"   ⚠️  Warning: Screen recording failed: {e}")
                print(f"   ℹ️  Continuing without recording...")
        else:
            print(f"   ℹ️  Screen recording disabled (enable_recording=False)")

        # Clear trajectory storage for new task
        self._current_trajectory = []

        # Get initial observation
        print(f"   Getting initial observation...")
        raw_obs = self.get_obs()

        if not raw_obs:
            print(f"   Warning: Failed to get initial observation")
            return None

        # Format observation according to observation_type configuration
        # This respects the observation_type setting (screenshot, a11y_tree, or screenshot_a11y_tree)
        formatted_obs_dict = self.format_observation_by_type(raw_obs, output_format="dict")

        # Store initial observation in trajectory
        self._current_trajectory.append({
            'step': 0,
            'type': 'initial_observation',
            'text': formatted_obs_dict.get('text', ''),
            'image': formatted_obs_dict.get('image', '')
        })

        # Return observation in dict format (compatible with run_osworld.py)
        return formatted_obs_dict

    def env_task_end(self, task_id: str, task_output_dir: Optional[str] = None, final_answer: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Finalize OSWorld task execution: end recording and save trajectory.

        This method performs:
        1. End screen recording and save video
        2. Save trajectory data (screenshots + a11y trees)
        3. Clear task-specific data

        Note: Evaluation is now decoupled and should be called separately before this method.

        Args:
            task_id: Task identifier
            task_output_dir: Directory to save recordings and trajectory
            final_answer: LLM's final answer (optional, not used in OSWorld)

        Returns:
            None (evaluation result is obtained separately via evaluate())
        """
        print(f"   Finalizing task {task_id}...")

        # End screen recording and save (if recording was enabled)
        enable_recording = self.config.get("osworld", {}).get("enable_recording", True)
        
        if enable_recording and task_output_dir:
            try:
                recording_path = os.path.join(task_output_dir, f"task_{task_id}.mp4")
                print(f"   Stopping screen recording...")
                self.end_recording(recording_path)
                print(f"   Recording saved to: {recording_path}")
            except Exception as e:
                print(f"   ⚠️  Warning: Failed to save recording: {e}")

        # Save trajectory to files
        if task_output_dir and self._current_trajectory:
            print(f"   Saving trajectory ({len(self._current_trajectory)} steps)...")
            self._save_trajectory_to_files(task_output_dir)

        # Clear task-specific data
        self._current_trajectory = []
        self._current_task_id = None

        # No longer return evaluation result - that's handled separately
        return None

    def env_start(self) -> None:
        """
        Start the OSWorld environment (called once at benchmark start).

        This initializes the DesktopEnv if not already initialized.
        """
        if self._desktop_env is None:
            print("Starting OSWorld environment...")
            # Create DesktopEnv if it was deferred (e.g., in parallel mode)
            self._init_desktop_env_from_config()
            print("OSWorld environment started successfully")
        else:
            print("OSWorld environment already running")

    def env_close(self) -> None:
        """
        Close and cleanup the OSWorld environment (called once at benchmark end).

        This closes the DesktopEnv and releases all resources.
        """
        if not self._desktop_env:
            print("OSWorld environment already closed or not initialized")
            return

        print("Closing OSWorld environment...")
        self._desktop_env.close()
        self._desktop_env = None
        print("OSWorld environment closed successfully")

    def _save_trajectory_to_files(self, output_dir: str) -> None:
        """
        Save trajectory data to individual step files.

        Creates:
        - step_N.png: Screenshot for each step
        - step_N_accessibility_tree.txt: Accessibility tree for each step

        Args:
            output_dir: Directory to save trajectory files
        """
        import base64

        for step_data in self._current_trajectory:
            step_num = step_data['step']

            # Save screenshot
            if step_data.get('image'):
                try:
                    screenshot_path = os.path.join(output_dir, f"step_{step_num}.png")
                    screenshot_bytes = base64.b64decode(step_data['image'])
                    with open(screenshot_path, 'wb') as f:
                        f.write(screenshot_bytes)
                except Exception as e:
                    print(f"   ⚠️  Failed to save step {step_num} screenshot: {e}")

            # Save accessibility tree
            if step_data.get('text'):
                try:
                    a11y_path = os.path.join(output_dir, f"step_{step_num}_accessibility_tree.txt")
                    with open(a11y_path, 'w', encoding='utf-8') as f:
                        f.write(step_data['text'])
                except Exception as e:
                    print(f"   ⚠️  Failed to save step {step_num} a11y tree: {e}")

    def add_step_to_trajectory(self, observation: Dict[str, Any], step_number: int) -> None:
        """
        Add a step observation to the current trajectory.

        This should be called by the runner after each tool execution
        that returns an observation.

        Args:
            observation: Observation dict with 'text' and 'image'
            step_number: Step number in the trajectory
        """
        self._current_trajectory.append({
            'step': step_number,
            'type': 'action_observation',
            'text': observation.get('text', ''),
            'image': observation.get('image', '')
        })

    # ========================================================================
    # Legacy Task Lifecycle Methods (kept for backward compatibility)
    # ========================================================================

    def reset_for_task(self, task: Dict[str, Any]) -> None:
        """
        Reset OSWorld environment for a new task.

        Args:
            task: Task dictionary with 'id', 'question', 'answer', 'metadata'
        """
        print(f"   Resetting OSWorld environment for task {task.get('id', 'unknown')}...")
        self.reset(task)

    def start_task_recording(self) -> None:
        """Start screen recording for task execution."""
        print(f"   Starting screen recording...")
        self.start_recording()

    def end_task_recording(self, output_path: str) -> None:
        """
        End screen recording and save to file.

        Args:
            output_path: Path where recording should be saved (e.g., "task_xxx.mp4")
        """
        print(f"   Stopping screen recording...")
        self.end_recording(output_path)
        print(f"   Recording saved to: {output_path}")

    def evaluate_task(self) -> float:
        """
        Evaluate task execution result.

        Returns:
            Evaluation score (float in [0, 1] range)
        """
        print(f"   Evaluating task result...")
        score = self.evaluate()
        print(f"   Evaluation score: {score:.2f}")
        return score

    def get_task_output_dir(self, base_output_dir: str, task_id: str, model_name: str) -> Optional[str]:
        """
        Get the output directory for OSWorld task.

        Returns:
            Path like "results/osworld/{task_id}/{model_name}"
        """
        import os
        task_output_dir = os.path.join(base_output_dir, self.mode, task_id, model_name)
        os.makedirs(task_output_dir, exist_ok=True)
        return task_output_dir

    def needs_trajectory_saving(self) -> bool:
        """OSWorld needs trajectory saving (screenshots + a11y trees)."""
        return True

    def has_internal_evaluation(self) -> bool:
        """OSWorld has internal evaluation capability using DesktopEnv evaluator."""
        return True

    def close(self):
        """
        Close and cleanup the environment.

        Should be called ONLY after ALL tasks complete, not between tasks.
        Each task should use reset_for_task() instead.
        """
        if not self._desktop_env:
            print("DesktopEnv already closed or not initialized")
            return

        print("Closing DesktopEnv...")
        self._desktop_env.close()
        self._desktop_env = None
        print("DesktopEnv closed successfully")


# Convenience function for creating OSWorld environment
def create_osworld_environment(**kwargs) -> OSWorldEnvironment:
    """
    Create an OSWorld environment for desktop automation.

    Args:
        **kwargs: Configuration parameters for OSWorldEnvironment including:
            Required:
            - path_to_vm: Path to VM image

            Optional with defaults:
            - provider_name: VM provider (default: "vmware")
            - action_space: Action space type (default: "pyautogui")
            - observation_type: Observation type (default: "screenshot_a11y_tree")
            - screen_width: Screen width in pixels (default: 1920)
            - screen_height: Screen height in pixels (default: 1080)
            - headless: Run in headless mode (default: False)
            - os_type: OS type (default: "Ubuntu")
            - client_password: VM client password (default: "password")
            - sleep_after_execution: Sleep time after each action in seconds (default: 0.5)

            Optional (only used if provided):
            - snapshot_name: VM snapshot name
            - require_terminal: Require terminal access

    Returns:
        Configured OSWorldEnvironment instance

    Example:
        >>> env = create_osworld_environment(
        ...     path_to_vm="/path/to/vm.vmx",
        ...     provider_name="vmware",
        ...     screen_width=1920,
        ...     screen_height=1080
        ... )
    """
    return OSWorldEnvironment(**kwargs)

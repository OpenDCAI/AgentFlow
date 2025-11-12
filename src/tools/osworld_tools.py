"""
OSWorld Desktop Automation Tools - Strict computer_13 Implementation

This module provides desktop automation tools that strictly follow the computer_13 action space.
Each tool validates parameters according to execute_action() requirements and returns proper error messages.

All tools follow the computer_13 action format:
{
    "action_type": "ACTION_NAME",
    "parameters": {...}
}
"""

import json
import os
from abc import ABC
from typing import Any, Dict, List, Union, Optional

from tools.tool import Tool, ToolResponse

# Import from desktop_env.actions
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
from utils.desktop_env.actions import KEYBOARD_KEYS, X_MAX, Y_MAX


class BaseDesktopTool(ABC):
    """
    Base class for all OSWorld desktop tools.

    顶层设计原则:
    ================
    1. **统一返回格式**: 所有情况（参数异常、执行异常、成功）都返回 ToolResponse
    2. **观察数据完整性**: 每个响应都包含当前环境观察（observation），包括错误情况
    3. **预处理观察数据**: 在工具层完成 observation 预处理（base64编码 + 树形结构线性化）
    4. **分层责任**:
       - 工具层: 参数验证、动作执行、观察获取、数据格式化
       - 运行层: 消息组装、对话管理

    数据流:
    ========
    Tool.call(params)
        ↓
    [参数验证] → 失败 → _create_result('failed', error_msg, observation)
        ↓ 成功
    [执行动作] → 失败 → _create_result('failed', error_msg, observation)
        ↓ 成功
    [获取观察] → _create_result('success', success_msg, observation)
        ↓
    ToolResponse.to_json() → JSON string

    核心方法:
    ==========
    - _get_current_observation(): 获取并格式化当前观察
    - _create_result(): 创建统一的结果字典（包含观察）
    - _serialize_result(): 序列化为 JSON 字符串
    - _execute_action(): 执行动作并返回结果
    """

    def __init__(self, osworld_env):
        """
        Initialize base desktop tool.

        Args:
            osworld_env: Instance of OSWorldEnvironment
        """
        self.osworld_env = osworld_env

    # ==================================================================
    # Core Methods - 核心方法（所有工具必经）
    # ==================================================================

    def _get_current_observation(self) -> Dict[str, Any]:
        """
        获取并格式化当前环境观察数据。

        此方法是获取 observation 的唯一入口，确保所有观察数据都经过预处理。

        Returns:
            格式化的观察数据:
            {
                'screenshot': base64-encoded PNG string,
                'a11y_tree': linearized accessibility tree string,
                'terminal': optional terminal output
            }
        """
        raw_obs: Any = {}
        try:
            raw_obs = self.osworld_env.get_obs()
        except Exception:
            # Fallback: try to get observation directly from desktop_env
            desktop_env = getattr(self.osworld_env, "_desktop_env", None)
            if desktop_env is not None:
                try:
                    raw_obs = desktop_env._get_obs()
                except Exception:
                    raw_obs = {}

        return self._format_observation(raw_obs)

    def _format_observation(self, observation: Any) -> Dict[str, Any]:
        """
        将原始观察数据转换为预处理的格式。

        使用OSWorldEnvironment的format_observation_by_type方法，
        该方法会根据observation_type配置自动返回正确的观察类型。

        Args:
            observation: 原始观察数据（可能包含bytes、dict等）

        Returns:
            预处理的观察数据（base64字符串、线性化树结构）
            格式: {'text': str, 'image': str}
            注意：只包含observation_type配置启用的字段
        """
        if not observation:
            return {}

        try:
            # Use the unified format_observation_by_type method
            # This automatically respects observation_type configuration
            # (screenshot, a11y_tree, or screenshot_a11y_tree)
            formatted = self.osworld_env.format_observation_by_type(
                observation if isinstance(observation, dict) else {},
                output_format="dict"
            )
        except Exception as e:
            print(f"⚠️  Warning: Failed to format observation: {e}")
            formatted = {}

        # Add optional fields from raw observation
        if isinstance(observation, dict):
            if observation.get("terminal"):
                formatted["terminal"] = observation.get("terminal")

        return formatted

    def _create_result(
        self,
        status: str,
        response: str,
        observation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建统一的结果字典（核心方法）。

        这是创建结果的唯一入口，确保所有结果都包含完整的观察数据。

        Args:
            status: 'success' 或 'failed'
            response: 人类可读的响应消息
            observation: 可选的观察数据。如果为None，会自动获取当前观察

        Returns:
            结果字典:
            {
                'status': str,
                'response': str,
                'observation': Dict (已预处理)
            }
        """
        # 如果没有提供observation，获取当前观察
        if observation is None:
            observation = self._get_current_observation()

        return {
            'status': status,
            'response': response,
            'observation': observation or {}
        }

    def _serialize_result(self, result: Dict[str, Any]) -> str:
        """
        将结果字典序列化为 JSON 字符串。

        Args:
            result: 来自 _create_result() 的结果字典

        Returns:
            JSON 字符串表示
        """
        tool_response = ToolResponse(
            status=result.get('status', 'unknown'),
            response=result.get('response', ''),
            observation=result.get('observation', {})
        )
        return tool_response.to_json()

    # ==================================================================
    # Helper Methods - 辅助方法
    # ==================================================================

    def _create_error_result(self, error_message: str, action_type: Optional[str] = None) -> Dict[str, Any]:
        """
        创建错误结果（便捷方法）。

        Args:
            error_message: 错误描述
            action_type: 可选的动作类型（如 'MOVE_TO', 'CLICK'）

        Returns:
            错误结果字典（包含当前观察）
        """
        # Format response with action type if provided
        if action_type:
            response = f"Validation failed for {action_type}: {error_message}"
        else:
            response = error_message

        return self._create_result('failed', response)

    def _validate_coordinates(self, params: dict, x_key: str = 'x', y_key: str = 'y') -> Optional[str]:
        """
        Validate coordinate parameters for type and range.

        Args:
            params: Parameters dict
            x_key: Key for x coordinate (default 'x')
            y_key: Key for y coordinate (default 'y')

        Returns:
            Error message if validation fails, None if valid
        """
        if x_key not in params or y_key not in params:
            return None  # No coordinates to validate

        # Type validation
        try:
            x = float(params[x_key])
            y = float(params[y_key])
        except (ValueError, TypeError):
            return f"Coordinates must be numbers, got {x_key}={params[x_key]}, {y_key}={params[y_key]}"

        # Range validation
        if not (0 <= x <= X_MAX):
            return f"{x_key} coordinate {x} out of range [0, {X_MAX}]"
        if not (0 <= y <= Y_MAX):
            return f"{y_key} coordinate {y} out of range [0, {Y_MAX}]"

        return None

    def _execute_action(self, action: Union[str, Dict[str, Any]], pause: Optional[float] = None) -> Dict[str, Any]:
        """
        执行 computer_13 格式的动作。

        Args:
            action: 动作字典 {"action_type": ..., "parameters": ...} 或控制字符串 ('WAIT', 'DONE', 'FAIL')
            pause: 可选的暂停时长（如果为None，使用配置中的默认值）

        Returns:
            结果字典（通过 _create_result 创建，包含观察数据）
        """
        env = self.osworld_env

        # Get pause from config if not provided
        if pause is None:
            osworld_config = env.get_config('osworld') or {}
            pause = osworld_config.get('sleep_after_execution', 2)

        # Format action description for response message
        if isinstance(action, dict):
            action_type = action.get('action_type', 'UNKNOWN')
            params = action.get('parameters', {})
            if params:
                action_desc = f"{action_type} with parameters {params}"
            else:
                action_desc = f"{action_type}"
        else:
            action_desc = str(action)

        # Execute action
        try:
            observation, reward, done, info = env.step(action, pause=pause)

            # Format observation and create success result
            formatted_obs = self._format_observation(observation)
            response = f"Action executed successfully: {action_desc}"

            return self._create_result('success', response, formatted_obs)

        except Exception as e:
            # Execution failed - create error result with current observation
            response = f"Execution failed for {action_desc}: {str(e)}"
            return self._create_result('failed', response)


# ==========================
# Mouse Tools
# ==========================

class MouseMoveTool(BaseDesktopTool, Tool):
    """
    Move mouse cursor to specified position.

    Action: MOVE_TO

    Parameter Requirements (from execute_action):
    - Case 1: Empty parameters {} → pyautogui.moveTo() [move to default]
    - Case 2: x AND y both provided → pyautogui.moveTo(x, y, duration, mode)
    - Invalid: Only x or only y → raise Exception
    """

    @property
    def name(self) -> str:
        return "desktop_mouse_move"

    @property
    def description(self) -> str:
        return f"Move the cursor to the specified position. Both x and y must be provided together, or omit both for default position. Coordinate ranges: x[0-{X_MAX}], y[0-{Y_MAX}]."

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "x",
                "type": "number",
                "description": f"X coordinate (0-{X_MAX}). If provided, y must also be provided.",
                "required": False
            },
            {
                "name": "y",
                "type": "number",
                "description": f"Y coordinate (0-{Y_MAX}). If provided, x must also be provided.",
                "required": False
            },
            {
                "name": "pause",
                "type": "number",
                "description": "Pause after action (seconds)",
                "required": False
            }
        ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        if isinstance(params, str):
            params = json.loads(params)

        # Type guard: ensure params is dict after json.loads
        if not isinstance(params, dict):
            result = self._create_error_result("Parameters must be a dictionary", "MOVE_TO")
            return self._serialize_result(result)

        has_x = 'x' in params
        has_y = 'y' in params

        # Validate: both x and y must be provided together, or both absent
        if has_x != has_y:
            result = self._create_error_result("MOVE_TO requires both 'x' and 'y' parameters together, or neither", "MOVE_TO")
            return self._serialize_result(result)

        # Validate coordinate types and ranges if provided
        if has_x and has_y:
            error_msg = self._validate_coordinates(params)
            if error_msg:
                result = self._create_error_result(error_msg, "MOVE_TO")
                return self._serialize_result(result)

        action_params = {}
        if has_x and has_y:
            action_params['x'] = params['x']
            action_params['y'] = params['y']

        action = {
            "action_type": "MOVE_TO",
            "parameters": action_params
        }

        pause = params.get('pause')
        result = self._execute_action(action, pause)
        return self._serialize_result(result)


class MouseClickTool(BaseDesktopTool, Tool):
    """
    Click mouse button.

    Action: CLICK

    Parameter Requirements (from execute_action):
    - Case 1: Empty {} → pyautogui.click() [click at current position, left button, 1 click]
    - Case 2: button + x + y (+ optional num_clicks)
    - Case 3: button only (+ optional num_clicks) [click at current position]
    - Case 4: x + y only (+ optional num_clicks) [left button]
    - Invalid: Any other combination → raise Exception

    Valid button values: "left", "right", "middle"
    Valid num_clicks: 1, 2, 3
    """

    @property
    def name(self) -> str:
        return "desktop_mouse_click"

    @property
    def description(self) -> str:
        return f"Click the left button if the button not specified, otherwise click the specified button; click at the current position if x and y are not specified, otherwise click at the specified position. Valid buttons: 'left'/'right'/'middle'. Optional num_clicks (1-3) must accompany button or x+y. Coordinate ranges: x[0-{X_MAX}], y[0-{Y_MAX}]."

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "x",
                "type": "number",
                "description": f"X coordinate (0-{X_MAX}). If provided, y must also be provided.",
                "required": False
            },
            {
                "name": "y",
                "type": "number",
                "description": f"Y coordinate (0-{Y_MAX}). If provided, x must also be provided.",
                "required": False
            },
            {
                "name": "button",
                "type": "string",
                "description": "Button: 'left', 'right', or 'middle'. Default: 'left'.",
                "required": False
            },
            {
                "name": "num_clicks",
                "type": "integer",
                "description": "Number of clicks: 1, 2, or 3. Must be used with button or x+y.",
                "required": False
            },
            {
                "name": "pause",
                "type": "number",
                "description": "Pause after action (seconds)",
                "required": False
            }
        ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        if isinstance(params, str):
            params = json.loads(params)

        # Type guard: ensure params is dict after json.loads
        if not isinstance(params, dict):
            result = self._create_error_result("Parameters must be a dictionary", "CLICK")
            return self._serialize_result(result)

        has_button = 'button' in params
        has_x = 'x' in params
        has_y = 'y' in params
        has_num_clicks = 'num_clicks' in params

        # Validate button value if provided
        if has_button and params['button'] not in ['left', 'right', 'middle']:
            result = self._create_error_result(f"Invalid button '{params['button']}'. Must be 'left', 'right', or 'middle'.", "CLICK")
            return self._serialize_result(result)

        # Validate num_clicks value if provided
        if has_num_clicks and params['num_clicks'] not in [1, 2, 3]:
            result = self._create_error_result(f"Invalid num_clicks '{params['num_clicks']}'. Must be 1, 2, or 3.", "CLICK")
            return self._serialize_result(result)

        # Validate x and y must appear together
        if has_x != has_y:
            result = self._create_error_result("If 'x' is provided, 'y' must also be provided, and vice versa.", "CLICK")
            return self._serialize_result(result)

        # Validate num_clicks cannot appear alone (must have button or x/y)
        if has_num_clicks and not has_button and not has_x:
            result = self._create_error_result("num_clicks cannot be used alone; must be accompanied by button or x+y coordinates.", "CLICK")
            return self._serialize_result(result)

        # Validate coordinate ranges if provided
        if has_x and has_y:
            error_msg = self._validate_coordinates(params)
            if error_msg:
                result = self._create_error_result(error_msg, "CLICK")
                return self._serialize_result(result)

        action_params = {}
        if has_button:
            action_params['button'] = params['button']
        if has_x and has_y:
            action_params['x'] = params['x']
            action_params['y'] = params['y']
        if has_num_clicks:
            action_params['num_clicks'] = params['num_clicks']

        action = {
            "action_type": "CLICK",
            "parameters": action_params
        }

        pause = params.get('pause')
        result = self._execute_action(action, pause)
        return self._serialize_result(result)


class MouseButtonTool(BaseDesktopTool, Tool):
    """
    Press or release mouse button (MOUSE_DOWN / MOUSE_UP).

    Parameter Requirements (from execute_action):
    - Case 1: Empty {} → mouseDown/Up() [left button]
    - Case 2: button provided → mouseDown/Up(button)
    - Invalid: Any other parameters → raise Exception

    Valid button values: "left", "right", "middle"
    """

    @property
    def name(self) -> str:
        return "desktop_mouse_button"

    @property
    def description(self) -> str:
        return "Press the left button if the button not specified, otherwise press the specified button (action='down'); release the left button if the button not specified, otherwise release the specified button (action='up'). Valid buttons: 'left'/'right'/'middle'."

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "action",
                "type": "string",
                "description": "Action: 'down' (press) or 'up' (release). REQUIRED.",
                "required": True
            },
            {
                "name": "button",
                "type": "string",
                "description": "Button: 'left', 'right', or 'middle'. Default: 'left'.",
                "required": False
            },
            {
                "name": "pause",
                "type": "number",
                "description": "Pause after action (seconds)",
                "required": False
            }
        ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        if isinstance(params, str):
            params = json.loads(params)

        # Type guard: ensure params is dict after json.loads
        if not isinstance(params, dict):
            result = self._create_error_result("Parameters must be a dictionary", "MOUSE_DOWN/MOUSE_UP")
            return self._serialize_result(result)

        # Validate action
        if 'action' not in params:
            result = self._create_error_result("'action' parameter is required", "MOUSE_DOWN/MOUSE_UP")
            return self._serialize_result(result)

        action_str = params['action'].upper()
        if action_str not in ['DOWN', 'UP']:
            result = self._create_error_result(f"Invalid action '{params['action']}'. Must be 'down' or 'up'.", "MOUSE_DOWN/MOUSE_UP")
            return self._serialize_result(result)

        # Validate button if provided
        has_button = 'button' in params
        if has_button and params['button'] not in ['left', 'right', 'middle']:
            result = self._create_error_result(f"Invalid button '{params['button']}'. Must be 'left', 'right', or 'middle'.", f"MOUSE_{action_str}")
            return self._serialize_result(result)

        action_params = {}
        if has_button:
            action_params['button'] = params['button']

        action = {
            "action_type": f"MOUSE_{action_str}",
            "parameters": action_params
        }

        pause = params.get('pause')
        result = self._execute_action(action, pause)
        return self._serialize_result(result)


class MouseRightClickTool(BaseDesktopTool, Tool):
    """
    Right-click at position.

    Action: RIGHT_CLICK

    Parameter Requirements (from execute_action):
    - Case 1: Empty {} → pyautogui.rightClick() [at current position]
    - Case 2: x AND y both provided → pyautogui.rightClick(x, y)
    - Invalid: Only x or only y → raise Exception
    """

    @property
    def name(self) -> str:
        return "desktop_mouse_right_click"

    @property
    def description(self) -> str:
        return f"Right click at the current position if x and y are not specified, otherwise right click at the specified position. Coordinate ranges: x[0-{X_MAX}], y[0-{Y_MAX}]."

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "x",
                "type": "number",
                "description": f"X coordinate (0-{X_MAX}). If provided, y must also be provided. Optional.",
                "required": False
            },
            {
                "name": "y",
                "type": "number",
                "description": f"Y coordinate (0-{Y_MAX}). If provided, x must also be provided. Optional.",
                "required": False
            },
            {
                "name": "pause",
                "type": "number",
                "description": "Pause after action (seconds)",
                "required": False
            }
        ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        if isinstance(params, str):
            params = json.loads(params)

        # Type guard: ensure params is dict after json.loads
        if not isinstance(params, dict):
            result = self._create_error_result("Parameters must be a dictionary", "RIGHT_CLICK")
            return self._serialize_result(result)

        has_x = 'x' in params
        has_y = 'y' in params

        # Validate: x and y must both be present or both absent
        if has_x != has_y:
            result = self._create_error_result("RIGHT_CLICK requires both 'x' and 'y', or neither.", "RIGHT_CLICK")
            return self._serialize_result(result)

        # Validate coordinate ranges if provided
        if has_x and has_y:
            error_msg = self._validate_coordinates(params)
            if error_msg:
                result = self._create_error_result(error_msg, "RIGHT_CLICK")
                return self._serialize_result(result)

        action_params = {}
        if has_x and has_y:
            action_params['x'] = params['x']
            action_params['y'] = params['y']

        action = {
            "action_type": "RIGHT_CLICK",
            "parameters": action_params
        }

        pause = params.get('pause')
        result = self._execute_action(action, pause)
        return self._serialize_result(result)


class MouseDoubleClickTool(BaseDesktopTool, Tool):
    """
    Double-click at position.

    Action: DOUBLE_CLICK

    Parameter Requirements (from execute_action):
    - Case 1: Empty {} → pyautogui.doubleClick() [at current position]
    - Case 2: x AND y both provided → pyautogui.doubleClick(x, y)
    - Invalid: Only x or only y → raise Exception
    """

    @property
    def name(self) -> str:
        return "desktop_mouse_double_click"

    @property
    def description(self) -> str:
        return f"Double click at the current position if x and y are not specified, otherwise double click at the specified position. Coordinate ranges: x[0-{X_MAX}], y[0-{Y_MAX}]."

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "x",
                "type": "number",
                "description": f"X coordinate (0-{X_MAX}). If provided, y must also be provided. Optional.",
                "required": False
            },
            {
                "name": "y",
                "type": "number",
                "description": f"Y coordinate (0-{Y_MAX}). If provided, x must also be provided. Optional.",
                "required": False
            },
            {
                "name": "pause",
                "type": "number",
                "description": "Pause after action (seconds)",
                "required": False
            }
        ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        if isinstance(params, str):
            params = json.loads(params)

        # Type guard: ensure params is dict after json.loads
        if not isinstance(params, dict):
            result = self._create_error_result("Parameters must be a dictionary", "DOUBLE_CLICK")
            return self._serialize_result(result)

        has_x = 'x' in params
        has_y = 'y' in params

        # Validate: x and y must both be present or both absent
        if has_x != has_y:
            result = self._create_error_result("DOUBLE_CLICK requires both 'x' and 'y', or neither.", "DOUBLE_CLICK")
            return self._serialize_result(result)

        # Validate coordinate ranges if provided
        if has_x and has_y:
            error_msg = self._validate_coordinates(params)
            if error_msg:
                result = self._create_error_result(error_msg, "DOUBLE_CLICK")
                return self._serialize_result(result)

        action_params = {}
        if has_x and has_y:
            action_params['x'] = params['x']
            action_params['y'] = params['y']

        action = {
            "action_type": "DOUBLE_CLICK",
            "parameters": action_params
        }

        pause = params.get('pause')
        result = self._execute_action(action, pause)
        return self._serialize_result(result)


class MouseDragTool(BaseDesktopTool, Tool):
    """
    Drag mouse to position.

    Action: DRAG_TO

    Parameter Requirements (from execute_action):
    - x AND y are REQUIRED (no default case)
    - Drags with left button pressed
    """

    @property
    def name(self) -> str:
        return "desktop_mouse_drag"

    @property
    def description(self) -> str:
        return f"Drag the cursor to the specified position with the left button pressed. Both x and y are required. Coordinate ranges: x[0-{X_MAX}], y[0-{Y_MAX}]."

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "x",
                "type": "number",
                "description": f"Target X coordinate (0-{X_MAX}). REQUIRED.",
                "required": True
            },
            {
                "name": "y",
                "type": "number",
                "description": f"Target Y coordinate (0-{Y_MAX}). REQUIRED.",
                "required": True
            },
            {
                "name": "pause",
                "type": "number",
                "description": "Pause after action (seconds)",
                "required": False
            }
        ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        if isinstance(params, str):
            params = json.loads(params)

        # Type guard: ensure params is dict after json.loads
        if not isinstance(params, dict):
            result = self._create_error_result("Parameters must be a dictionary", "DRAG_TO")
            return self._serialize_result(result)

        # Validate: both required
        if 'x' not in params or 'y' not in params:
            result = self._create_error_result("DRAG_TO requires both 'x' and 'y' parameters", "DRAG_TO")
            return self._serialize_result(result)

        # Validate coordinate ranges
        error_msg = self._validate_coordinates(params)
        if error_msg:
            result = self._create_error_result(error_msg, "DRAG_TO")
            return self._serialize_result(result)

        action = {
            "action_type": "DRAG_TO",
            "parameters": {
                "x": params['x'],
                "y": params['y']
            }
        }

        pause = params.get('pause')
        result = self._execute_action(action, pause)
        return self._serialize_result(result)


# ==========================
# Scroll Tool
# ==========================

class ScrollTool(BaseDesktopTool, Tool):
    """
    Scroll horizontally and/or vertically.

    Action: SCROLL

    Parameter Requirements (from execute_action):
    - Case 1: dx AND dy both provided → hscroll(dx) + vscroll(dy)
    - Case 2: dx only → hscroll(dx)
    - Case 3: dy only → vscroll(dy)
    - Invalid: Neither dx nor dy → raise Exception

    Note: At least ONE of dx or dy must be provided
    """

    @property
    def name(self) -> str:
        return "desktop_scroll"

    @property
    def description(self) -> str:
        return "Scroll the mouse wheel up or down. At least one of dx (horizontal scroll amount) or dy (vertical scroll amount) is required. Positive values scroll up/right, negative values scroll down/left."

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "dx",
                "type": "integer",
                "description": "Horizontal scroll (positive=right, negative=left). At least dx or dy required.",
                "required": False
            },
            {
                "name": "dy",
                "type": "integer",
                "description": "Vertical scroll (positive=up, negative=down). At least dx or dy required.",
                "required": False
            },
            {
                "name": "pause",
                "type": "number",
                "description": "Pause after action (seconds)",
                "required": False
            }
        ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        if isinstance(params, str):
            params = json.loads(params)

        # Type guard: ensure params is dict after json.loads
        if not isinstance(params, dict):
            result = self._create_error_result("Parameters must be a dictionary", "SCROLL")
            return self._serialize_result(result)

        has_dx = 'dx' in params
        has_dy = 'dy' in params

        # Validate: at least one required
        if not has_dx and not has_dy:
            result = self._create_error_result("SCROLL requires at least one of 'dx' or 'dy'", "SCROLL")
            return self._serialize_result(result)

        action_params = {}
        if has_dx:
            action_params['dx'] = params['dx']
        if has_dy:
            action_params['dy'] = params['dy']

        action = {
            "action_type": "SCROLL",
            "parameters": action_params
        }

        pause = params.get('pause')
        result = self._execute_action(action, pause)
        return self._serialize_result(result)


# ==========================
# Keyboard Tools
# ==========================

class TypeTool(BaseDesktopTool, Tool):
    """
    Type text string.

    Action: TYPING

    Parameter Requirements (from execute_action):
    - text is REQUIRED
    - Raises exception if text not provided
    """

    @property
    def name(self) -> str:
        return "desktop_type"

    @property
    def description(self) -> str:
        return "Type the specified text. Parameter 'text' is required and contains the string to type."

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "text",
                "type": "string",
                "description": "Text to type. REQUIRED.",
                "required": True
            },
            {
                "name": "pause",
                "type": "number",
                "description": "Pause after action (seconds)",
                "required": False
            }
        ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        if isinstance(params, str):
            params = json.loads(params)

        # Type guard: ensure params is dict after json.loads
        if not isinstance(params, dict):
            result = self._create_error_result("Parameters must be a dictionary", "TYPING")
            return self._serialize_result(result)

        # Validate
        if 'text' not in params:
            result = self._create_error_result("TYPING requires 'text' parameter", "TYPING")
            return self._serialize_result(result)

        action = {
            "action_type": "TYPING",
            "parameters": {
                "text": params['text']
            }
        }

        pause = params.get('pause')
        result = self._execute_action(action, pause)
        return self._serialize_result(result)


class KeyPressTool(BaseDesktopTool, Tool):
    """
    Press and release a key.

    Action: PRESS

    Parameter Requirements (from execute_action):
    - key is REQUIRED
    - key must be in KEYBOARD_KEYS list
    - Raises exception if key not provided or invalid
    """

    @property
    def name(self) -> str:
        return "desktop_key_press"

    @property
    def description(self) -> str:
        return "Press the specified key and release it. Parameter 'key' is required and must be a valid keyboard key from KEYBOARD_KEYS."

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "key",
                "type": "string",
                "description": "Key to press (e.g., 'enter', 'esc', 'tab', 'a'). REQUIRED. Must be in valid key list.",
                "required": True
            },
            {
                "name": "pause",
                "type": "number",
                "description": "Pause after action (seconds)",
                "required": False
            }
        ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        if isinstance(params, str):
            params = json.loads(params)

        # Type guard: ensure params is dict after json.loads
        if not isinstance(params, dict):
            result = self._create_error_result("Parameters must be a dictionary", "PRESS")
            return self._serialize_result(result)

        # Validate presence
        if 'key' not in params:
            result = self._create_error_result("PRESS requires 'key' parameter", "PRESS")
            return self._serialize_result(result)

        key = params['key']

        # Validate key is in allowed list
        if key.lower() not in KEYBOARD_KEYS:
            result = self._create_error_result(f"Invalid key '{key}'. Must be one of the valid keyboard keys.", "PRESS")
            return self._serialize_result(result)

        action = {
            "action_type": "PRESS",
            "parameters": {
                "key": key
            }
        }

        pause = params.get('pause')
        result = self._execute_action(action, pause)
        return self._serialize_result(result)


class KeyHoldTool(BaseDesktopTool, Tool):
    """
    Press or release a key (KEY_DOWN / KEY_UP).

    Parameter Requirements (from execute_action):
    - key is REQUIRED
    - key must be in KEYBOARD_KEYS list
    - Raises exception if key not provided or invalid
    """

    @property
    def name(self) -> str:
        return "desktop_key_hold"

    @property
    def description(self) -> str:
        return "Press the specified key (action='down') or release the specified key (action='up'). Both 'action' and 'key' are required. Key must be a valid keyboard key from KEYBOARD_KEYS."

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "action",
                "type": "string",
                "description": "Action: 'down' (press) or 'up' (release). REQUIRED.",
                "required": True
            },
            {
                "name": "key",
                "type": "string",
                "description": "Key to press/release. REQUIRED. Must be in valid key list.",
                "required": True
            },
            {
                "name": "pause",
                "type": "number",
                "description": "Pause after action (seconds)",
                "required": False
            }
        ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        if isinstance(params, str):
            params = json.loads(params)

        # Type guard: ensure params is dict after json.loads
        if not isinstance(params, dict):
            result = self._create_error_result("Parameters must be a dictionary", "KEY_DOWN/KEY_UP")
            return self._serialize_result(result)

        # Validate action
        if 'action' not in params:
            result = self._create_error_result("'action' parameter is required", "KEY_DOWN/KEY_UP")
            return self._serialize_result(result)

        action_str = params['action'].upper()
        if action_str not in ['DOWN', 'UP']:
            result = self._create_error_result(f"Invalid action '{params['action']}'. Must be 'down' or 'up'.", "KEY_DOWN/KEY_UP")
            return self._serialize_result(result)

        # Validate key presence
        if 'key' not in params:
            result = self._create_error_result("'key' parameter is required", f"KEY_{action_str}")
            return self._serialize_result(result)

        key = params['key']

        # Validate key is in allowed list
        if key.lower() not in KEYBOARD_KEYS:
            result = self._create_error_result(f"Invalid key '{key}'. Must be one of the valid keyboard keys.", f"KEY_{action_str}")
            return self._serialize_result(result)

        action = {
            "action_type": f"KEY_{action_str}",
            "parameters": {
                "key": key
            }
        }

        pause = params.get('pause')
        result = self._execute_action(action, pause)
        return self._serialize_result(result)


class HotkeyTool(BaseDesktopTool, Tool):
    """
    Press key combination.

    Action: HOTKEY

    Parameter Requirements (from execute_action):
    - keys is REQUIRED
    - keys must be a list
    - Each key in the list must be in KEYBOARD_KEYS
    - Raises exception if keys not provided, not a list, or contains invalid keys
    """

    @property
    def name(self) -> str:
        return "desktop_hotkey"

    @property
    def description(self) -> str:
        return "Press the specified key combination (hotkey). Parameter 'keys' is required and must be a list of valid keyboard keys from KEYBOARD_KEYS (e.g., ['ctrl', 'c'] for copy)."

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "keys",
                "type": "array",
                "array_type": "string",
                "description": "List of keys to press simultaneously (e.g., ['ctrl', 'c']). REQUIRED. All keys must be valid.",
                "required": True
            },
            {
                "name": "pause",
                "type": "number",
                "description": "Pause after action (seconds)",
                "required": False
            }
        ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        if isinstance(params, str):
            params = json.loads(params)

        # Type guard: ensure params is dict after json.loads
        if not isinstance(params, dict):
            result = self._create_error_result("Parameters must be a dictionary", "HOTKEY")
            return self._serialize_result(result)

        # Validate presence
        if 'keys' not in params:
            result = self._create_error_result("HOTKEY requires 'keys' parameter", "HOTKEY")
            return self._serialize_result(result)

        keys = params['keys']

        # Validate is list
        if not isinstance(keys, list):
            result = self._create_error_result(f"'keys' must be a list, got {type(keys).__name__}", "HOTKEY")
            return self._serialize_result(result)

        # Validate each key
        for key in keys:
            if key.lower() not in KEYBOARD_KEYS:
                result = self._create_error_result(f"Invalid key '{key}' in keys list. All keys must be valid keyboard keys.", "HOTKEY")
                return self._serialize_result(result)

        action = {
            "action_type": "HOTKEY",
            "parameters": {
                "keys": keys
            }
        }

        pause = params.get('pause')
        result = self._execute_action(action, pause)
        return self._serialize_result(result)


# ==========================
# Python Script Tool
# ==========================

class ExecutePythonScriptTool(BaseDesktopTool, Tool):
    """
    Execute Python script using pyautogui.

    Action: Python Script (string)

    Parameter Requirements:
    - script is REQUIRED (string containing Python code)
    - The script will be executed directly via env.step()
    - Supports pyautogui commands with explicit (x, y) coordinates
    - Should NOT use pyautogui.locateCenterOnScreen or pyautogui.screenshot
    - Can include time.sleep() for delays between actions

    Note: This tool executes arbitrary Python code in the desktop environment.
    The code must specify coordinates directly rather than using image recognition.
    """

    @property
    def name(self) -> str:
        return "desktop_execute_python_script"

    @property
    def description(self) -> str:
        sudo_password = os.getenv('SUDO_PASSWORD', 'password')
        return (
            f"Executes one or more lines of Python code using `pyautogui` to interact with the screen. "
            "The code must specify (x, y) coordinates directly. "
            "DO NOT use `pyautogui.locateCenterOnScreen` or `pyautogui.screenshot`. "
            "You can include small delays like `time.sleep(0.5)` between actions. "
            f"The computer's password is '{sudo_password}' if sudo rights are needed."
        )

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "script",
                "type": "string",
                "description": "A string containing one or more lines of valid Python code. "
                               "Example: 'import pyautogui; pyautogui.click(100, 200)'",
                "required": True
            },
            {
                "name": "pause",
                "type": "number",
                "description": "Pause after action (seconds)",
                "required": False
            }
        ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        if isinstance(params, str):
            params = json.loads(params)

        # Type guard: ensure params is dict after json.loads
        if not isinstance(params, dict):
            result = self._create_error_result("Parameters must be a dictionary", "PYTHON_SCRIPT")
            return self._serialize_result(result)

        # Validate script parameter
        if 'script' not in params:
            result = self._create_error_result("'script' parameter is required", "PYTHON_SCRIPT")
            return self._serialize_result(result)

        script = params['script']

        # Validate script is a string
        if not isinstance(script, str):
            result = self._create_error_result(f"'script' must be a string, got {type(script).__name__}", "PYTHON_SCRIPT")
            return self._serialize_result(result)

        # Validate script is not empty
        if not script.strip():
            result = self._create_error_result("'script' cannot be empty", "PYTHON_SCRIPT")
            return self._serialize_result(result)

        # Execute the Python script directly (env.step will route string to run_python_script)
        pause = params.get('pause')
        result = self._execute_action(script, pause)
        return self._serialize_result(result)


# ==========================
# Control Tool
# ==========================

class ControlTool(BaseDesktopTool, Tool):
    """
    Send control signals.

    Actions: WAIT, DONE, FAIL

    Parameter Requirements (from execute_action):
    - These are special string actions, not dict format
    - Passed directly as strings: 'WAIT', 'DONE', 'FAIL'
    """

    @property
    def name(self) -> str:
        return "desktop_control"

    @property
    def description(self) -> str:
        return "Send control signal to manage task flow. Parameter 'action' is required: 'wait' (wait until the next action), 'done' (decide the task is done), or 'fail' (decide the task cannot be performed)."

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "action",
                "type": "string",
                "description": "Control action: 'wait', 'done', or 'fail'. REQUIRED.",
                "required": True
            },
            {
                "name": "pause",
                "type": "number",
                "description": "Pause after action (seconds)",
                "required": False
            }
        ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        if isinstance(params, str):
            params = json.loads(params)

        # Type guard: ensure params is dict after json.loads
        if not isinstance(params, dict):
            result = self._create_error_result("Parameters must be a dictionary", "WAIT/DONE/FAIL")
            return self._serialize_result(result)

        # Validate
        if 'action' not in params:
            result = self._create_error_result("'action' parameter is required", "WAIT/DONE/FAIL")
            return self._serialize_result(result)

        action_str = params['action'].upper()
        if action_str not in ['WAIT', 'DONE', 'FAIL']:
            result = self._create_error_result(f"Invalid action '{params['action']}'. Must be 'wait', 'done', or 'fail'.", "WAIT/DONE/FAIL")
            return self._serialize_result(result)

        # Control actions are passed as strings, not dicts
        action = action_str

        pause = params.get('pause')
        result = self._execute_action(action, pause)
        return self._serialize_result(result)


# ==========================
# Tool Registration
# ==========================

def register_osworld_tools(osworld_env) -> List[Tool]:
    """
    Register all OSWorld desktop automation tools.

    Args:
        osworld_env: Instance of OSWorldEnvironment

    Returns:
        List of all registered Tool instances
    """
    tools = [
        # Mouse Tools
        MouseMoveTool(osworld_env),
        MouseClickTool(osworld_env),
        MouseButtonTool(osworld_env),
        MouseRightClickTool(osworld_env),
        MouseDoubleClickTool(osworld_env),
        MouseDragTool(osworld_env),

        # Scroll Tool
        ScrollTool(osworld_env),

        # Typing Tool
        TypeTool(osworld_env),

        # Keyboard Tools
        KeyPressTool(osworld_env),
        KeyHoldTool(osworld_env),
        HotkeyTool(osworld_env),

        # Python Script Tool
        ExecutePythonScriptTool(osworld_env),

        # Control Tool
        ControlTool(osworld_env),
    ]

    return tools

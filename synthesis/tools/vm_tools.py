"""
VM Tool Schemas

This module defines the tool schemas for VM operations.
These schemas are used to construct prompts for the LLM agent.
"""

from typing import List, Dict, Any

VM_RESPONSE_NOTE = (
    "Returns accessibility_tree; do not call vm-screenshot just to fetch UI state."
)


def get_vm_tool_schemas() -> List[Dict[str, Any]]:
    """
    Get all VM tool schemas.

    Returns:
        List of tool schema dictionaries
    """
    return [
        get_vm_click_schema(),
        get_vm_double_click_schema(),
        get_vm_screenshot_schema(),
        get_vm_type_schema(),
        get_vm_key_schema(),
        get_vm_hotkey_schema(),
        get_vm_scroll_schema(),
        get_vm_drag_schema(),
        get_vm_move_schema(),
        get_vm_mouse_down_schema(),
        get_vm_mouse_up_schema(),
        get_vm_right_click_schema(),
        get_vm_key_down_schema(),
        get_vm_key_up_schema(),
    ]


def get_vm_click_schema() -> Dict[str, Any]:
    """Schema for vm_click - click at a coordinate."""
    return {
        "name": "vm-click",
        "description": f"Click at the given (x, y) coordinate. {VM_RESPONSE_NOTE}",
        "parameters": [
            {"name": "x", "type": "integer", "description": "X coordinate", "required": True},
            {"name": "y", "type": "integer", "description": "Y coordinate", "required": True},
            {
                "name": "button",
                "type": "string",
                "description": "Mouse button: left/right/middle (default: left)",
                "required": False,
            },
        ],
    }


def get_vm_double_click_schema() -> Dict[str, Any]:
    """Schema for vm_double_click - double click at a coordinate."""
    return {
        "name": "vm-double_click",
        "description": f"Double click at the given (x, y) coordinate. {VM_RESPONSE_NOTE}",
        "parameters": [
            {"name": "x", "type": "integer", "description": "X coordinate", "required": True},
            {"name": "y", "type": "integer", "description": "Y coordinate", "required": True},
        ],
    }


def get_vm_screenshot_schema() -> Dict[str, Any]:
    """Schema for vm_screenshot - take a screenshot."""
    return {
        "name": "vm-screenshot",
        "description": f"Capture the current VM screen. {VM_RESPONSE_NOTE}",
        "parameters": [],
    }


def get_vm_type_schema() -> Dict[str, Any]:
    """Schema for vm_type - type text."""
    return {
        "name": "vm-type",
        "description": f"Type text into the active input. {VM_RESPONSE_NOTE}",
        "parameters": [
            {"name": "text", "type": "string", "description": "Text to type", "required": True},
            {
                "name": "interval",
                "type": "number",
                "description": "Delay between keystrokes in seconds (default: 0.0)",
                "required": False,
            },
        ],
    }


def get_vm_key_schema() -> Dict[str, Any]:
    """Schema for vm_key - press a key."""
    return {
        "name": "vm-key",
        "description": f"Press a single key (e.g., enter/tab/escape/space/backspace). {VM_RESPONSE_NOTE}",
        "parameters": [
            {"name": "key", "type": "string", "description": "Key name", "required": True},
        ],
    }


def get_vm_hotkey_schema() -> Dict[str, Any]:
    """Schema for vm_hotkey - press a key combination."""
    return {
        "name": "vm-hotkey",
        "description": f"Press a key combination (e.g., ['ctrl', 'c']). {VM_RESPONSE_NOTE}",
        "parameters": [
            {
                "name": "keys",
                "type": "array",
                "array_type": "string",
                "description": "List of key names in order",
                "required": True,
            },
        ],
    }


def get_vm_scroll_schema() -> Dict[str, Any]:
    """Schema for vm_scroll - scroll at a coordinate."""
    return {
        "name": "vm-scroll",
        "description": f"Scroll at the given (x, y) position. {VM_RESPONSE_NOTE}",
        "parameters": [
            {"name": "x", "type": "integer", "description": "X coordinate", "required": True},
            {"name": "y", "type": "integer", "description": "Y coordinate", "required": True},
            {
                "name": "clicks",
                "type": "integer",
                "description": "Scroll amount (positive up, negative down)",
                "required": True,
            },
        ],
    }


def get_vm_drag_schema() -> Dict[str, Any]:
    """Schema for vm_drag - drag from start to end coordinates."""
    return {
        "name": "vm-drag",
        "description": f"Drag from (start_x, start_y) to (end_x, end_y). {VM_RESPONSE_NOTE}",
        "parameters": [
            {"name": "start_x", "type": "integer", "description": "Start X coordinate", "required": True},
            {"name": "start_y", "type": "integer", "description": "Start Y coordinate", "required": True},
            {"name": "end_x", "type": "integer", "description": "End X coordinate", "required": True},
            {"name": "end_y", "type": "integer", "description": "End Y coordinate", "required": True},
        ],
    }


def get_vm_move_schema() -> Dict[str, Any]:
    """Schema for vm_move - move mouse to a coordinate."""
    return {
        "name": "vm-move",
        "description": f"Move mouse to the given (x, y) coordinate. {VM_RESPONSE_NOTE}",
        "parameters": [
            {"name": "x", "type": "integer", "description": "X coordinate", "required": True},
            {"name": "y", "type": "integer", "description": "Y coordinate", "required": True},
        ],
    }


def get_vm_mouse_down_schema() -> Dict[str, Any]:
    """Schema for vm_mouse_down - press mouse button down."""
    return {
        "name": "vm-mouse_down",
        "description": f"Press mouse button down. {VM_RESPONSE_NOTE}",
        "parameters": [
            {
                "name": "button",
                "type": "string",
                "description": "Mouse button: left/right/middle (default: left)",
                "required": False,
            },
        ],
    }


def get_vm_mouse_up_schema() -> Dict[str, Any]:
    """Schema for vm_mouse_up - release mouse button."""
    return {
        "name": "vm-mouse_up",
        "description": f"Release mouse button. {VM_RESPONSE_NOTE}",
        "parameters": [
            {
                "name": "button",
                "type": "string",
                "description": "Mouse button: left/right/middle (default: left)",
                "required": False,
            },
        ],
    }


def get_vm_right_click_schema() -> Dict[str, Any]:
    """Schema for vm_right_click - right click optionally at a coordinate."""
    return {
        "name": "vm-right_click",
        "description": f"Right click at (x, y) if provided; otherwise at current cursor. {VM_RESPONSE_NOTE}",
        "parameters": [
            {
                "name": "x",
                "type": "integer",
                "description": "X coordinate (must be provided together with y)",
                "required": False,
            },
            {
                "name": "y",
                "type": "integer",
                "description": "Y coordinate (must be provided together with x)",
                "required": False,
            },
        ],
    }


def get_vm_key_down_schema() -> Dict[str, Any]:
    """Schema for vm_key_down - press a key down."""
    return {
        "name": "vm-key_down",
        "description": f"Press and hold a key down. {VM_RESPONSE_NOTE}",
        "parameters": [
            {"name": "key", "type": "string", "description": "Key name", "required": True},
        ],
    }


def get_vm_key_up_schema() -> Dict[str, Any]:
    """Schema for vm_key_up - release a key."""
    return {
        "name": "vm-key_up",
        "description": f"Release a key. {VM_RESPONSE_NOTE}",
        "parameters": [
            {"name": "key", "type": "string", "description": "Key name", "required": True},
        ],
    }


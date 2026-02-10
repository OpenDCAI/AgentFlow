# Tool Schemas

This directory contains tool schema definitions for the RAG synthesis pipeline.

## Overview

The sandbox does not provide a `get_tools()` method, so we maintain tool schemas locally. These schemas are used to construct prompts for the LLM agent during trajectory sampling.

## Structure

- `rag_tools.py` - RAG-related tool schemas
- `web_tools.py` - Web-related tool schemas
- `__init__.py` - Module initialization and exports

## Current Tools

- `rag_search` - Basic RAG index query tool
- `web_search` - Batched web search tool
- `web_visit` - Web page visit and content extraction tool

## Adding New Tools

To add a new tool schema:

1. Create a new function in the appropriate module (or create a new file for a different category):

```python
def get_my_new_tool_schema() -> Dict[str, Any]:
    """
    Schema for my_new_tool - description of what it does.
    """
    return {
        "name": "my_new_tool",
        "description": "Clear description of what this tool does",
        "parameters": [
            {
                "name": "param1",
                "type": "string",  # or "integer", "array", etc.
                "description": "Description of this parameter",
                "required": True  # or False
            },
            # Add more parameters as needed
        ]
    }
```

2. Add the new schema to the category list (e.g., `get_rag_tool_schemas()`):

```python
def get_rag_tool_schemas() -> List[Dict[str, Any]]:
    return [
        get_local_search_schema(),
        get_goal_focused_search_schema(),
        get_my_new_tool_schema(),  # Add your new tool here
    ]
```

3. Register the category in `tools/__init__.py` so the tool is included in `get_tool_schemas()`.

4. The tool will automatically be available to the LLM agent in the next run.

## Schema Format

Each tool schema must follow this format:

```python
{
    "name": "tool_name",           # Unique identifier for the tool
    "description": "...",          # Clear description for the LLM
    "parameters": [                # List of parameters
        {
            "name": "param_name",
            "type": "string",      # string, integer, array, etc.
            "description": "...",  # What this parameter does
            "required": True       # Whether it's required
        }
    ]
}
```

## Usage

The tool schemas are loaded in `core/sampler.py`:

```python
from tools import get_tool_schemas

# In TrajectorySampler.sample_trajectory_tree():
self.available_tools = get_tool_schemas()
```

These schemas are then used to construct prompts that inform the LLM about available tools during trajectory exploration.

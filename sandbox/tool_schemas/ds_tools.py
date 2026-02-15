"""
Data Science Tool Schemas

This module defines the tool schemas for Data Science operations (read_csv, run_python).
These schemas are used to construct prompts for the LLM agent.
"""

from typing import List, Dict, Any


def get_ds_tool_schemas() -> List[Dict[str, Any]]:
    """
    Get all Data Science tool schemas.

    Returns:
        List of tool schema dictionaries
    """
    return [
        get_ds_read_csv_schema(),
        get_ds_run_python_schema(),
        get_ds_inspect_data_schema(),
    ]


def get_ds_read_csv_schema() -> Dict[str, Any]:
    """
    Schema for ds_read_csv tool.
    """
    return {
        "name": "ds_read_csv",
        "description": (
            "Read the first few rows of a CSV file to inspect its structure and content. "
            "Use this to understand the data schema before writing analysis code. "
            "Note: base_dir is automatically provided from seed context."
        ),
        "parameters": [
            {
                "name": "csv_file",
                "type": "string",
                "description": "Name of the CSV file to read (e.g., 'data.csv').",
                "required": True,
            },
            {
                "name": "max_rows",
                "type": "integer",
                "description": "Number of rows to preview (default: 50).",
                "required": False,
            },
        ],
    }


def get_ds_run_python_schema() -> Dict[str, Any]:
    """
    Schema for ds_run_python tool.
    """
    return {
        "name": "ds_run_python",
        "description": (
            "Execute Python code for data analysis. "
            "Pre-installed libraries: pandas, numpy, scipy, sklearn, statsmodels, matplotlib, seaborn. "
            "The code allows creating charts/plots. "
            "Input/Output: Can read CSVs from the current directory and save results/figures. "
            "Security: File access is restricted to the current directory. "
            "Note: base_dir is automatically provided from seed context."
        ),
        "parameters": [
            {
                "name": "code",
                "type": "string",
                "description": "Python code to execute.",
                "required": True,
            },
            {
                "name": "return_vars",
                "type": "array",
                "array_type": "string",
                "description": "List of variable names to inspect after execution (e.g., ['df_head', 'result']).",
                "required": False,
            },
        ],
    }


def get_ds_inspect_data_schema() -> Dict[str, Any]:
    """
    Schema for ds_inspect_data tool.
    """
    return {
        "name": "ds_inspect_data",
        "description": (
            "Inspect the data directory to list all CSV files and get a summary of their content (columns, shapes, missing values). "
            "Use this as the FIRST step to understand what data is available."
        ),
        "parameters": [],
    }


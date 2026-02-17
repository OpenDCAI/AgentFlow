# sandbox/server/backends/tools/ds_tool.py
"""
Data Science API Tools

Provides read_csv, run_python, inspect_data and other tools for data science tasks.
Ported from DS_synthesis/src/tools/ds_tools.py
"""

import io
import os
import sys
import traceback
import contextlib
import json
import time
import math
import re
import random
import datetime
import collections
import itertools
import functools
import warnings
import base64
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# --- Third-party libraries ---
try:
    import pandas as pd
    import numpy as np
    import scipy
    import statsmodels.api as sm
    import sklearn
    import patsy
    # --- Plotting library setup ---
    import matplotlib
    matplotlib.use('Agg') 
    import matplotlib.pyplot as plt
    import seaborn as sns
    DS_LIBS_AVAILABLE = True
except ImportError:
    DS_LIBS_AVAILABLE = False
    # Define some placeholders to prevent IDE errors, runtime will check DS_LIBS_AVAILABLE
    pd = None
    np = None
    plt = None
    sns = None


from . import register_api_tool
from ..error_codes import ErrorCode
from .base_tool import BaseApiTool, ToolBusinessError


# ==========================================
# Core Tool Functions (ported from DS_synthesis)
# ==========================================

def _resolve_csv_path(base_dir: str, csv_file: str) -> Path:
    """
    Resolve CSV filename to a safe path under base_dir, preventing path traversal.
    """
    # If already an absolute path and within base_dir, return directly
    if os.path.isabs(csv_file):
        candidate = Path(csv_file).resolve()
    else:
        root = Path(base_dir).expanduser().resolve()
        candidate = (root / csv_file).expanduser().resolve()
        
    root = Path(base_dir).expanduser().resolve()
    if not str(candidate).startswith(str(root)):
        raise ValueError(f"Security Error: File path '{csv_file}' escapes the seed directory.")
    
    return candidate


def summarize_csvs_in_folder(folder_path: str, max_csv: int = 100) -> str:
    """
    Scans a folder for all CSV files and returns a natural language summary for each.
    """
    if not DS_LIBS_AVAILABLE:
        return "Error: Data Science libraries (pandas, etc.) are not installed."

    # 1. Validate Folder Path
    if not os.path.exists(folder_path):
        return f"Error: The directory '{folder_path}' does not exist."
    
    # 2. Get list of CSV files
    all_files = os.listdir(folder_path)
    csv_files = [f for f in all_files if f.lower().endswith('.csv')]
    csv_files.sort()
    
    if not csv_files:
        return f"No CSV files found in directory: {folder_path}"

    results = []

    # 3. Loop through each CSV file
    for file_name in csv_files[:max_csv]:
        file_path = os.path.join(folder_path, file_name)
        
        try:
            df = pd.read_csv(file_path)
            num_rows, num_cols = df.shape
            columns = df.columns.tolist()
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            cat_cols = df.select_dtypes(exclude=['number']).columns.tolist()
            missing_count = df.isnull().sum().sum()
            duplicate_count = df.duplicated().sum()
            
            desc = f"This dataset contains {num_rows} rows and {num_cols} columns. "
            if len(columns) > 5:
                col_str = ", ".join(columns[:5]) + f", and {len(columns)-5} others"
            else:
                col_str = ", ".join(columns)
            desc += f"Key attributes include: [{col_str}]. "
            desc += f"It has {len(numeric_cols)} numeric fields "
            if numeric_cols: desc += f"(e.g., {numeric_cols[0]}) "
            desc += f"and {len(cat_cols)} categorical fields. "
            
            if missing_count == 0 and duplicate_count == 0:
                desc += "Data quality is high (no missing values or duplicates)."
            else:
                issues = []
                if missing_count > 0: issues.append(f"{missing_count} missing values")
                if duplicate_count > 0: issues.append(f"{duplicate_count} duplicates")
                desc += f"Data requires cleaning: found {', '.join(issues)}."

            results.append(f"{file_name}:\n{desc}")
        except Exception as e:
            results.append(f"{file_name}:\nError processing file - {str(e)}")

    summary = "\n\n".join(results)
    if len(csv_files) > max_csv:
        summary += f"\n\n... truncated: showing first {max_csv} of {len(csv_files)} CSV files ..."
    return summary


def read_csv_impl(
    csv_file: str,
    base_dir: str,
    max_rows: int = 50,
) -> Dict[str, Any]:
    """
    Read CSV file from seed directory and return text content.
    """
    if not DS_LIBS_AVAILABLE:
        return {"text": "Error: Data Science libraries (pandas, etc.) are not installed.", "images": []}

    if not base_dir:
        return {"text": "base_dir is empty, environment did not correctly inject CSV root directory.", "images": []}

    try:
        path = _resolve_csv_path(base_dir, csv_file)
        if not path.exists():
            return {"text": f"File does not exist: {path}", "images": []}
        if not path.is_file():
            return {"text": f"Path is not a file: {path}", "images": []}

        df = pd.read_csv(path)
    except Exception as exc:
        return {"text": f"Read failed: {exc}", "images": []}

    preview = df.head(max_rows)
    body = preview.to_csv(index=False)
    note = ""
    if len(df) > max_rows:
        note = f"\n... Truncated, showing first {max_rows} rows out of {len(df)} total rows ..."

    return {"text": f"{path.name}\n{body}{note}", "images": []}


# ==========================================
# Whitelist and Import Control
# ==========================================
ALLOWED_MODULES = {
    "pandas", "numpy", "scipy", "statsmodels", "patsy",
    "sklearn", "joblib", "xgboost", "lightgbm", "imblearn",
    "sys", "os", "io", "pathlib", "json", "csv", "pickle", "glob", "shutil",
    "datetime", "time", "dateutil", "calendar", "pytz",
    "collections", "itertools", "functools", "operator", "heapq", "bisect", "copy", "enum",
    "re", "string", "textwrap", "difflib", "unicodedata",
    "math", "random", "statistics", "decimal", "fractions",
    "warnings", "logging", "pprint", "uuid", "hashlib", "typing", "dataclasses",
    "matplotlib", "seaborn", "plotly", "altair",
    "urllib", "html", "xml" 
}

def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    root_module = name.split(".")[0]
    if root_module not in ALLOWED_MODULES:
        raise ImportError(f"Security: Import of module '{root_module}' is blocked.")
    return __import__(name, globals, locals, fromlist, level)

@contextlib.contextmanager
def _patch_pandas_io(base_dir: str):
    if not DS_LIBS_AVAILABLE:
        yield
        return

    original_read_csv = pd.read_csv
    
    def patched_read_csv(filepath_or_buffer, *args, **kwargs):
        if isinstance(filepath_or_buffer, str):
            if not filepath_or_buffer.startswith(('http:', 'https:', 'ftp:', 's3:')):
                try:
                    resolved_path = _resolve_csv_path(base_dir, filepath_or_buffer)
                    filepath_or_buffer = str(resolved_path)
                except Exception:
                    pass
        return original_read_csv(filepath_or_buffer, *args, **kwargs)

    pd.read_csv = patched_read_csv
    try:
        yield
    finally:
        pd.read_csv = original_read_csv


def run_python_impl(
    code: str,
    base_dir: str,
    return_vars: Optional[List[str]] = None,
) -> Dict[str, Any]:
    
    if not DS_LIBS_AVAILABLE:
        return {"text": "Error: Data Science libraries (pandas, etc.) are not installed.", "images": []}

    base_dir = base_dir or os.getcwd()

    # --- Helper functions ---
    def load_csv(name: str, **kwargs):
        path = _resolve_csv_path(base_dir, name)
        return pd.read_csv(path, **kwargs)

    def save_file(data: Any, name: str, **kwargs):
        path = Path(base_dir) / name
        if not str(path.resolve()).startswith(str(Path(base_dir).resolve())):
             raise ValueError("Security Error: Cannot save file outside base_dir.")
        
        if isinstance(data, pd.DataFrame):
            data.to_csv(path, **kwargs)
        elif hasattr(data, 'savefig'): 
            data.savefig(path, **kwargs)
        else:
            import joblib
            joblib.dump(data, path, **kwargs)
        return f"File saved to: {name}"

    # --- Safe Builtins ---
    safe_builtins = {
        "__import__": _safe_import,
        "abs": abs, "min": min, "max": max, "sum": sum, "round": round, "pow": pow, "divmod": divmod,
        "all": all, "any": any,
        "len": len, "range": range, "enumerate": enumerate, "zip": zip, 
        "map": map, "filter": filter, "iter": iter, "next": next,
        "slice": slice, "reversed": reversed, "sorted": sorted,
        "list": list, "dict": dict, "set": set, "tuple": tuple, "frozenset": frozenset,
        "str": str, "int": int, "float": float, "bool": bool, "complex": complex, "bytes": bytes,
        "type": type, "isinstance": isinstance, "issubclass": issubclass, "callable": callable,
        "hash": hash, "id": id, "object": object,
        "getattr": getattr, "setattr": setattr, "hasattr": hasattr, "delattr": delattr,
        "vars": vars, "dir": dir,
        "print": print, "repr": repr, "ascii": ascii, "format": format,
        "chr": chr, "ord": ord, "bin": bin, "hex": hex, "oct": oct,
        "Exception": Exception, "ValueError": ValueError, "TypeError": TypeError, "KeyError": KeyError, 
        "IndexError": IndexError, "NameError": NameError, "AttributeError": AttributeError, 
        "ImportError": ImportError, "RuntimeError": RuntimeError, "ZeroDivisionError": ZeroDivisionError
    }

    globals_ns = {
        "__builtins__": safe_builtins,
        "pd": pd,
        "np": np,
        "scipy": scipy,
        "sm": sm,
        "sklearn": sklearn,
        "sys": sys,
        "os": os,
        "json": json,
        "time": time,
        "datetime": datetime,
        "re": re,
        "math": math,
        "random": random,
        "collections": collections,
        "itertools": itertools,
        "warnings": warnings,
        "plt": plt,
        "sns": sns,
        "Path": Path,
        "load_csv": load_csv,
        "save_file": save_file,
    }
    locals_ns = {}

    plt.close('all') 
    warnings.filterwarnings("ignore")

    stdout_capture = io.StringIO()
    error_message = None
    images = []

    try:
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stdout_capture):
            # Use patch to automatically correct relative paths in pd.read_csv
            with _patch_pandas_io(base_dir):
                exec(code, globals_ns, locals_ns)
        
        # Image capture
        if plt.get_fignums():
            fig = plt.gcf()
            img_buf = io.BytesIO()
            fig.savefig(img_buf, format='png', bbox_inches='tight')
            img_buf.seek(0)
            img_b64 = base64.b64encode(img_buf.read()).decode('utf-8')
            images.append({
                "type": "image/png",
                "base64": img_b64,
                "description": "Generated Plot"
            })
            
    except Exception:
        error_message = traceback.format_exc()

    finally:
        plt.close('all')

    stdout = stdout_capture.getvalue().strip()
    MAX_CHARS = 5000
    if len(stdout) > MAX_CHARS:
        stdout = stdout[:MAX_CHARS] + f"\n\n[System Warning]: Output truncated! (Total {len(stdout)} chars)."

    parts = []
    
    if error_message:
        parts.append(f"❌ Execution Error:\n{error_message}")
    
    if stdout:
        parts.append(f"📄 Standard Output:\n{stdout}")

    if return_vars and not error_message:
        captures = []
        for name in return_vars:
            if name in locals_ns:
                val = locals_ns[name]
                if isinstance(val, pd.DataFrame):
                    preview = val.head(5).to_markdown(index=False)
                    captures.append(f"{name} (shape={val.shape}):\n{preview}")
                else:
                    captures.append(f"{name} = {str(val)}")
        if captures:
            parts.append("📦 Variables Inspection:\n" + "\n".join(captures))
            
    if not parts and not images:
        parts.append("✅ Execution successful (No output printed).")

    return {
        "text": "\n\n".join(parts),
        "images": images 
    }


# ==========================================
# Tool Class Definitions
# ==========================================

class InspectDataTool(BaseApiTool):
    """Inspect Data Tool"""
    def __init__(self):
        super().__init__(tool_name="ds:inspect_data", resource_type="ds")

    async def execute(self, **kwargs) -> Any:
        seed_path = kwargs.get("seed_path")
        if not seed_path:
             # If seed_path is not in kwargs, try to get from config (though for ds, seed_path is usually dynamic)
             # Here we throw an error, requiring seed_path to be provided
             raise ToolBusinessError("seed_path must be provided in kwargs", ErrorCode.EXECUTION_ERROR)

        max_csv = self.get_config("ds_max_csv")
        if max_csv is None:
            max_csv = 100
        max_csv = int(max_csv)

        max_chars = self.get_config("ds_summary_max_chars")
        if max_chars is None:
            max_chars = 12000
        max_chars = int(max_chars)

        summary = summarize_csvs_in_folder(seed_path, max_csv=max_csv)
        if len(summary) > max_chars:
            summary = summary[:max_chars] + "\n\n... [Summary truncated to comply with maximum length limit] ..."
        return {"result": summary}

class ReadCsvTool(BaseApiTool):
    """Read CSV Tool"""
    def __init__(self):
        super().__init__(tool_name="ds:read_csv", resource_type="ds")

    async def execute(self, csv_file: str, max_rows: int = 50, **kwargs) -> Any:
        seed_path = kwargs.get("seed_path")
        if not seed_path:
             raise ToolBusinessError("seed_path must be provided in kwargs", ErrorCode.EXECUTION_ERROR)
        
        result = read_csv_impl(csv_file, seed_path, max_rows)
        return {"result": result["text"]}  # Currently only return text, ignore images (read_csv doesn't produce images)

class RunPythonTool(BaseApiTool):
    """Run Python Tool"""
    def __init__(self):
        super().__init__(tool_name="ds:run_python", resource_type="ds")

    async def execute(self, code: str, return_vars: Optional[List[str]] = None, **kwargs) -> Any:
        seed_path = kwargs.get("seed_path")
        if not seed_path:
             raise ToolBusinessError("seed_path must be provided in kwargs", ErrorCode.EXECUTION_ERROR)
        
        result = run_python_impl(code, seed_path, return_vars)
        
        # Format output, including images
        output = result["text"]
        if result["images"]:
            output += "\n\n[Generated Images]:\n"
            # We cannot directly display images in text here, but in the sandbox protocol, images are usually returned separately
            # Currently BaseApiTool's execute returns Any, usually a dict.
            # We can return {"result": text, "images": [...] } 
            # But the standard response_builder might serialize the dict.
            # For simplicity, we only return text description here, or we could make BaseApiTool support returning multimedia.
            # Check base_tool.py implementation, it just returns the result of execute.
            # If we return a dict, it will be JSON serialized.
            # To allow the frontend (if any) to display images, we need to follow some protocol.
            # For now, only return "Generated X images", actual image data is in result['images']
            output += f"Generated {len(result['images'])} images (base64 data available)."
            
        return {
            "result": output,
            "images": result["images"]  # Pass raw image data
        }


# ==========================================
# Register Tools
# ==========================================

inspect_data = register_api_tool(
    name="ds:inspect_data",
    config_key="ds",
    description="Inspect data directory"
)(InspectDataTool())

read_csv = register_api_tool(
    name="ds:read_csv",
    config_key="ds",
    description="Read CSV file"
)(ReadCsvTool())

run_python = register_api_tool(
    name="ds:run_python",
    config_key="ds",
    description="Run Python code"
)(RunPythonTool())

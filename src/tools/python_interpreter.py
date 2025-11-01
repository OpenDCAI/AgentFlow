import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union, List


class PythonInterpreterTool:
    def __init__(self, timeout: int = 30, use_venv: bool = True):
        self.name = "python_interpreter"
        self.description = "Executes Python code and returns the result."
        self.timeout = timeout
        self.use_venv = use_venv
        self.python_executable = sys.executable  # use the current python env
        self.parameters = [
            {
                'name': 'expressions',
                'type': 'array',
                'array_type': 'string',
                'description': 'An array of Python code lines to execute sequentially in the interpreter, '
                'supporting assignments, loops, conditionals, function definitions, and more. '
                'Example: ["a = 10", "for i in range(3): print(a * i)", "def greet(): return \'Hello!\'", "greet()"]',
                'required': True
            },
        ]
        
    def call(self, params: Union[str, dict], **kwargs) -> str:
        try:
            expressions = params["expressions"]
        except Exception:
            return "[PythonInterpreter] Invalid request: Input must contain 'expressions' field"

        if isinstance(expressions, str):
            expressions = [expressions]
        elif not isinstance(expressions, list):
            return "[PythonInterpreter] Invalid request: 'expressions' must be a list or string"
  
        namespace = {"__builtins__": {}}
        allowed_builtins = ['abs', 'round', 'len', 'sum', 'min', 'max', 'range', 'list', 'dict', 'str', 'int', 'float']
        for name in allowed_builtins:
            if hasattr(__builtins__, name):
                namespace[name] = __builtins__[name]
        
        results = []
        print("call_expressions", expressions)  
        for expr in expressions:
            cur_mode = "exec"
            try:
                # judge mode: "exec", "eval"
                try: # expression
                    compile(expr, '<string>', 'eval')
                    cur_mode = "eval"
                except SyntaxError: # statement
                    cur_mode = "exec"
                
                if cur_mode == "eval":
                    result = eval(expr, namespace)
                    results.append({"expression": expr, "result": result})
                else: # cur_mode == "exec"
                    exec(expr, namespace)
                    results.append({"expression": expr, "result": None})

            except Exception as e:
                results.append({"expression": expr, "error": str(e)})

        # 格式化输出
        fact_str = ''
        for item in results:
            if "error" in item:
                fact_str += f"{item['expression']} = ERROR ({item['error']})\n"
            else:
                fact_str += f"{item['expression']} = {item['result']}\n"

        return f"""### PythonInterpreter Results:
                {fact_str}
                """

    # abandon (丢掉)
    def call_python(self, code: str, mode: str = "exec") -> Dict[str, Any]:
        """
        Args:
            code: Python code
            mode: 'exec' or 'eval'

        Returns:
            Dict[str, Any]: success, output, error, result
        """
        try:
            if mode == "eval": # calculate value, return result
                result = eval(code)
                return {
                    "success": True,
                    "output": None,
                    "error": None,
                    "result": result
                }
            elif mode == "exec": # execute python code, result: None
                # use subprocess
                completed = subprocess.run(
                    [self.python_executable, "-c", code],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=Path.cwd()
                )
                return {
                    "success": completed.returncode == 0,
                    "output": completed.stdout,
                    "error": completed.stderr,
                    "result": None
                }
            else:
                raise ValueError("mode must be 'exec' or 'eval'")
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": None,
                "error": "Execution timed out.",
                "result": None
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": str(e),
                "result": None
            }
            
    # abandon (丢掉)
    def call_file(self, file_path: str, args: Optional[list] = None) -> Dict[str, Any]:
        """
        execute an external Python file.

        Args:
            file_path: Python file path
            args: Command line arguments to pass to the script (list)

        Returns:
            Dict[str, Any]: success, output, error, result
        """
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            return {
                "success": False,
                "output": None,
                "error": f"File not found: {file_path}",
                "result": None
            }

        cmd = [self.python_executable, str(file_path)]
        if args:
            cmd.extend(args)

        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=file_path.parent
            )
            return {
                "success": completed.returncode == 0,
                "output": completed.stdout,
                "error": completed.stderr,
                "result": None
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": None,
                "error": "Script execution timed out.",
                "result": None
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": str(e),
                "result": None
            }

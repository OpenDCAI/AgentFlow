from typing import Union, List
import math

class CalculatorTool:
    name = "calculator"
    description = (
        "A simple calculator tool: supports basic arithmetic operations (+, -, *, /) "
        "and some advanced functions (sqrt, pow, sin, cos). "
        "Provide an expression or multiple expressions for evaluation."
    )
    parameters = [
        {
            'name': 'expressions',
            'type': 'array',
            'array_type': 'string',
            'description': 'An array of mathematical expressions to evaluate. '
                           'Example: ["2+2", "sqrt(16)", "pow(2,3)"]',
            'required': True
        },
    ]

    def call(self, params: Union[str, dict], **kwargs) -> str:
        try:
            expressions = params["expressions"]
        except Exception:
            return "[Calculator] Invalid request: Input must contain 'expressions' field"

        if isinstance(expressions, str):
            expressions = [expressions]
        elif not isinstance(expressions, list):
            return "[Calculator] Invalid request: 'expressions' must be a list or string"

        results = []
        for expr in expressions:
            try:
                # 安全地限制可用函数
                allowed_names = {
                    k: v for k, v in math.__dict__.items() if not k.startswith("__")
                }
                allowed_names['abs'] = abs
                allowed_names['round'] = round

                result = eval(expr, {"__builtins__": {}}, allowed_names)
                results.append({"expression": expr, "result": result})
            except Exception as e:
                results.append({"expression": expr, "error": str(e)})

        # 格式化输出
        fact_str = ''
        for item in results:
            if "error" in item:
                fact_str += f"{item['expression']} = ERROR ({item['error']})\n"
            else:
                fact_str += f"{item['expression']} = {item['result']}\n"

        return f"""### Calculator Results:
{fact_str}
"""


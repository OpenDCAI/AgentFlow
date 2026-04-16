from __future__ import annotations

from pathlib import Path
from typing import Any

from .tool import Tool


class EditTool(Tool):
    name = "Edit"
    description = (
        "Perform an exact string replacement in a file. "
        "old_string must uniquely identify the target location unless replace_all=true."
    )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "old_string": {"type": "string"},
                "new_string": {"type": "string"},
                "replace_all": {"type": "boolean", "default": False},
            },
            "required": ["file_path", "old_string", "new_string"],
        }

    async def call(self, args: dict[str, Any], ctx: Any) -> str:
        del ctx
        path = Path(args["file_path"])
        old_string = args["old_string"]
        new_string = args["new_string"]
        replace_all = args.get("replace_all", False)

        if not path.exists():
            return f"Error: file not found: {path}"

        content = path.read_text(encoding="utf-8")
        count = content.count(old_string)
        if count == 0:
            return f"Error: old_string not found in {path}. Read the file first to verify the exact text."
        if count > 1 and not replace_all:
            return (
                f"Error: old_string appears {count} times in {path}. "
                "Provide more surrounding context to make it unique, or set replace_all=true."
            )

        if replace_all:
            updated = content.replace(old_string, new_string)
            replacements = count
        else:
            updated = content.replace(old_string, new_string, 1)
            replacements = 1

        path.write_text(updated, encoding="utf-8")
        return f"Replaced {replacements} occurrence(s) in {path}"


class WriteTool(Tool):
    name = "Write"
    description = "Write content to a file, creating parent directories if needed."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["file_path", "content"],
        }

    async def call(self, args: dict[str, Any], ctx: Any) -> str:
        del ctx
        path = Path(args["file_path"])
        content = args["content"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        line_count = content.count("\n")
        if content and not content.endswith("\n"):
            line_count += 1
        return f"Wrote {len(content)} bytes ({line_count} lines) to {path}"

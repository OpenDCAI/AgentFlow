from __future__ import annotations

import asyncio
import io
import locale
import os
import signal
import subprocess
from pathlib import Path
from typing import Any

from .tool import Tool


class BashTool(Tool):
    name = "Bash"
    description = "Execute a shell command and return stdout/stderr."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to run"},
            },
            "required": ["command"],
        }

    async def call(self, args: dict[str, Any], ctx: Any) -> str:
        proc = await asyncio.create_subprocess_shell(
            args["command"],
            shell=True,
            cwd=ctx.cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True,
        )

        try:
            stdout_bytes, stderr_bytes = await proc.communicate()
        except asyncio.CancelledError:
            if proc.returncode is None:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    proc.kill()
            await proc.communicate()
            raise

        output = _decode_text_mode_output(stdout_bytes)
        stderr = _decode_text_mode_output(stderr_bytes)
        if proc.returncode:
            return _format_command_error("bash", proc.returncode, output, stderr)
        return _format_command_output(output, stderr)


def _decode_text_mode_output(data: bytes | None) -> str:
    if not data:
        return ""

    text_stream = io.TextIOWrapper(
        io.BytesIO(data),
        encoding=locale.getpreferredencoding(False),
        newline=None,
    )
    try:
        return text_stream.read()
    finally:
        text_stream.detach()


def _format_command_output(stdout: str, stderr: str) -> str:
    output = stdout
    if stderr:
        output += f"\n[stderr]:\n{stderr}" if output else f"[stderr]:\n{stderr}"
    return output.strip() or "(no output)"


def _format_command_error(tool_name: str, returncode: int, stdout: str, stderr: str) -> str:
    if returncode < 0:
        status = f"signal {-returncode}"
    else:
        status = f"exit status {returncode}"

    summary = f"Error: {tool_name} command failed with {status}"
    details = _format_command_output(stdout, stderr)
    if details == "(no output)":
        return summary
    return f"{summary}\n{details}"


class ReadTool(Tool):
    name = "Read"
    description = "Read a file and return its contents with line numbers."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "offset": {"type": "integer", "description": "Start line (1-indexed)"},
                "limit": {"type": "integer", "description": "Maximum lines to return"},
            },
            "required": ["file_path"],
        }

    async def call(self, args: dict[str, Any], ctx: Any) -> str:
        del ctx
        path = Path(args["file_path"])
        if not path.exists():
            return f"Error: file not found: {path}"

        lines = path.read_text(encoding="utf-8").splitlines()
        offset = max(0, args.get("offset", 1) - 1)
        limit = args.get("limit", 2000)
        selected = lines[offset : offset + limit]
        return "\n".join(
            f"{line_number:4}→{line}"
            for line_number, line in enumerate(selected, start=offset + 1)
        )

    def is_read_only(self, args: dict[str, Any]) -> bool:
        del args
        return True


class GlobTool(Tool):
    name = "Glob"
    description = "Find files matching a glob pattern."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Glob pattern"},
                "path": {"type": "string", "description": "Directory to search from"},
            },
            "required": ["pattern"],
        }

    async def call(self, args: dict[str, Any], ctx: Any) -> str:
        base = Path(args.get("path", ctx.cwd))
        pattern = args["pattern"]
        matches = sorted(base.glob(pattern))
        return "\n".join(str(match) for match in matches) or "(no matches)"

    def is_read_only(self, args: dict[str, Any]) -> bool:
        del args
        return True


class GrepTool(Tool):
    name = "Grep"
    description = "Search file contents with a regex pattern."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Regex pattern"},
                "path": {"type": "string", "description": "Directory to search"},
                "glob": {"type": "string", "description": "Optional file glob filter"},
            },
            "required": ["pattern"],
        }

    async def call(self, args: dict[str, Any], ctx: Any) -> str:
        base = Path(args.get("path", ctx.cwd))
        cmd = ["grep", "-r", "-n"]
        if "glob" in args:
            cmd += ["--include", args["glob"]]
        cmd += ["--", args["pattern"], str(base)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout or "(no matches)"
        if result.returncode == 1:
            return "(no matches)"
        return _format_command_error("grep", result.returncode, result.stdout, result.stderr)

    def is_read_only(self, args: dict[str, Any]) -> bool:
        del args
        return True

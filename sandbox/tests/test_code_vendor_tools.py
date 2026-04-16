import asyncio
import importlib.util
import shlex
import sys
import time
from types import SimpleNamespace
from pathlib import Path

import pytest

PACKAGE_DIR = (
    Path(__file__).resolve().parents[1]
    / "server"
    / "backends"
    / "resources"
    / "code_vendor"
)


def load_code_vendor_module(module_name):
    package_name = "_test_code_vendor"
    package_spec = importlib.util.spec_from_file_location(
        package_name,
        PACKAGE_DIR / "__init__.py",
        submodule_search_locations=[str(PACKAGE_DIR)],
    )
    package = importlib.util.module_from_spec(package_spec)
    sys.modules[package_name] = package
    assert package_spec is not None
    assert package_spec.loader is not None
    package_spec.loader.exec_module(package)

    module_spec = importlib.util.spec_from_file_location(
        f"{package_name}.{module_name}",
        PACKAGE_DIR / f"{module_name}.py",
    )
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[f"{package_name}.{module_name}"] = module
    assert module_spec is not None
    assert module_spec.loader is not None
    module_spec.loader.exec_module(module)
    return module


file_tools = load_code_vendor_module("file_tools")
edit_tools = load_code_vendor_module("edit_tools")
tool_module = load_code_vendor_module("tool")

ReadTool = file_tools.ReadTool
GlobTool = file_tools.GlobTool
GrepTool = file_tools.GrepTool
BashTool = file_tools.BashTool
EditTool = edit_tools.EditTool
WriteTool = edit_tools.WriteTool


def make_ctx(tmp_path):
    return SimpleNamespace(cwd=str(tmp_path))


def call_tool(tool, args, ctx):
    return asyncio.run(tool.call(args, ctx))


def test_read_tool_returns_line_numbered_content(tmp_path):
    target = tmp_path / "sample.txt"
    target.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")

    result = call_tool(ReadTool(), {"file_path": str(target)}, make_ctx(tmp_path))

    assert result == "   1→alpha\n   2→beta\n   3→gamma"


def test_read_tool_honors_offset_and_limit(tmp_path):
    target = tmp_path / "sample.txt"
    target.write_text("alpha\nbeta\ngamma\ndelta\n", encoding="utf-8")

    result = call_tool(
        ReadTool(),
        {"file_path": str(target), "offset": 1, "limit": 2},
        make_ctx(tmp_path),
    )

    assert result == "   1→alpha\n   2→beta"


def test_edit_tool_requires_unique_match_by_default(tmp_path):
    target = tmp_path / "sample.txt"
    target.write_text("alpha\nbeta\nbeta\n", encoding="utf-8")

    result = call_tool(
        EditTool(),
        {"file_path": str(target), "old_string": "beta", "new_string": "BETA"},
        make_ctx(tmp_path),
    )

    assert "appears 2 times" in result
    assert "replace_all=true" in result
    assert target.read_text(encoding="utf-8") == "alpha\nbeta\nbeta\n"


def test_edit_tool_replace_all_updates_each_match(tmp_path):
    target = tmp_path / "sample.txt"
    target.write_text("alpha\nbeta\nbeta\n", encoding="utf-8")

    result = call_tool(
        EditTool(),
        {
            "file_path": str(target),
            "old_string": "beta",
            "new_string": "BETA",
            "replace_all": True,
        },
        make_ctx(tmp_path),
    )

    assert result == f"Replaced 2 occurrence(s) in {target}"
    assert target.read_text(encoding="utf-8") == "alpha\nBETA\nBETA\n"


def test_write_tool_creates_parent_directories_and_overwrites_full_file(tmp_path):
    target = tmp_path / "nested" / "dir" / "sample.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("stale content that should disappear\n", encoding="utf-8")

    result = call_tool(
        WriteTool(),
        {"file_path": str(target), "content": "hello\nworld\n"},
        make_ctx(tmp_path),
    )

    assert result == f"Wrote 12 bytes (2 lines) to {target}"
    assert target.read_text(encoding="utf-8") == "hello\nworld\n"


def test_glob_tool_returns_sorted_matches(tmp_path):
    (tmp_path / "a.py").write_text("print('a')\n", encoding="utf-8")
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "b.py").write_text("print('b')\n", encoding="utf-8")
    (pkg / "c.txt").write_text("ignore\n", encoding="utf-8")

    result = call_tool(
        GlobTool(),
        {"pattern": "**/*.py", "path": str(tmp_path)},
        make_ctx(tmp_path),
    )

    assert result == f"{tmp_path / 'a.py'}\n{tmp_path / 'pkg' / 'b.py'}"


def test_grep_tool_returns_matches_with_line_numbers_for_filtered_files(tmp_path):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("alpha\nbeta\n", encoding="utf-8")
    second.write_text("beta\ngamma\n", encoding="utf-8")

    result = call_tool(
        GrepTool(),
        {"pattern": "beta", "path": str(tmp_path), "glob": "*.txt"},
        make_ctx(tmp_path),
    )

    assert result.endswith("\n")
    assert set(result.splitlines()) == {
        f"{first}:2:beta",
        f"{second}:1:beta",
    }


def test_grep_tool_searches_recursively_without_glob_filter(tmp_path):
    root_match = tmp_path / "root.txt"
    nested_dir = tmp_path / "pkg" / "nested"
    nested_dir.mkdir(parents=True)
    nested_match = nested_dir / "deep.py"
    root_match.write_text("needle at root\n", encoding="utf-8")
    nested_match.write_text("first line\nneedle in nested file\n", encoding="utf-8")

    result = call_tool(
        GrepTool(),
        {"pattern": "needle", "path": str(tmp_path)},
        make_ctx(tmp_path),
    )

    assert result.endswith("\n")
    assert set(result.splitlines()) == {
        f"{nested_match}:2:needle in nested file",
        f"{root_match}:1:needle at root",
    }


def test_grep_tool_returns_no_matches_for_exit_code_one(tmp_path):
    target = tmp_path / "sample.txt"
    target.write_text("alpha\nbeta\n", encoding="utf-8")

    result = call_tool(
        GrepTool(),
        {"pattern": "missing", "path": str(tmp_path)},
        make_ctx(tmp_path),
    )

    assert result == "(no matches)"


def test_grep_tool_returns_error_prefix_for_invalid_pattern(tmp_path):
    target = tmp_path / "sample.txt"
    target.write_text("alpha\nbeta\n", encoding="utf-8")

    result = call_tool(
        GrepTool(),
        {"pattern": "[", "path": str(tmp_path)},
        make_ctx(tmp_path),
    )

    assert result.startswith("Error:")
    assert "exit status 2" in result
    assert "[stderr]:" in result


def test_grep_tool_treats_option_like_pattern_as_search_pattern(tmp_path):
    target = tmp_path / "sample.txt"
    target.write_text("--help\nalpha\n", encoding="utf-8")

    result = call_tool(
        GrepTool(),
        {"pattern": "--help", "path": str(tmp_path)},
        make_ctx(tmp_path),
    )

    assert result == f"{target}:1:--help\n"


def test_bash_tool_combines_stdout_and_stderr(tmp_path):
    result = call_tool(
        BashTool(),
        {
            "command": (
                "python -c \"import sys; "
                "print('out'); "
                "print('err', file=sys.stderr)\""
            )
        },
        make_ctx(tmp_path),
    )

    assert result == "out\n\n[stderr]:\nerr"


def test_bash_tool_matches_text_mode_newline_normalization(tmp_path):
    result = call_tool(
        BashTool(),
        {
            "command": (
                f"{shlex.quote(sys.executable)} -c "
                "\"import sys; sys.stdout.buffer.write(b'a\\r\\nb\\r\\n')\""
            )
        },
        make_ctx(tmp_path),
    )

    assert result == "a\nb"


def test_bash_tool_returns_error_prefix_for_nonzero_exit_status(tmp_path):
    result = call_tool(
        BashTool(),
        {
            "command": (
                f"{shlex.quote(sys.executable)} -c "
                "\"import sys; "
                "print('out'); "
                "print('err', file=sys.stderr); "
                "raise SystemExit(7)\""
            )
        },
        make_ctx(tmp_path),
    )

    assert result.startswith("Error:")
    assert "exit status 7" in result
    assert "out" in result
    assert "[stderr]:" in result
    assert "err" in result


def test_bash_tool_cancellation_stops_background_command(tmp_path):
    marker = tmp_path / "marker.txt"

    async def run_bash_with_timeout():
        timeout_start = time.monotonic()
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                BashTool().call(
                    {
                        "command": (
                            f"{shlex.quote(sys.executable)} -c "
                            "\"import pathlib, time; "
                            "time.sleep(0.3); "
                            "pathlib.Path('marker.txt').write_text('created', encoding='utf-8')\""
                        )
                    },
                    make_ctx(tmp_path),
                ),
                timeout=0.1,
            )
        timeout_elapsed = time.monotonic() - timeout_start
        await asyncio.sleep(0.4)
        return timeout_elapsed

    timeout_elapsed = asyncio.run(run_bash_with_timeout())

    assert timeout_elapsed < 0.25
    assert not marker.exists()


def test_tool_api_format_and_read_only_flags():
    read_tool = ReadTool()
    bash_tool = BashTool()

    api_format = read_tool.to_api_format()

    assert api_format["name"] == "Read"
    assert isinstance(api_format["description"], str)
    assert api_format["input_schema"] == read_tool.input_schema
    assert read_tool.is_read_only({}) is True
    assert bash_tool.is_read_only({}) is False

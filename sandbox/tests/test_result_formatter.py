from sandbox.result_formatter import format_tool_result


def test_format_tool_result_returns_plain_string_for_successful_code_response():
    response = {
        "code": 0,
        "message": "success",
        "data": "   1→hello",
        "meta": {
            "tool": "code:read",
            "resource_type": "code",
            "execution_time_ms": 1.2,
        },
    }

    assert format_tool_result(response) == "   1→hello"


def test_format_tool_result_preserves_whitespace_only_plain_string_for_successful_code_response():
    response = {
        "code": 0,
        "message": "success",
        "data": "  \n\t  ",
        "meta": {
            "tool": "code:read",
            "resource_type": "code",
            "execution_time_ms": 1.2,
        },
    }

    assert format_tool_result(response) == "  \n\t  "


def test_format_tool_result_keeps_dict_style_successful_code_response_behavior():
    response = {
        "code": 0,
        "message": "success",
        "data": {
            "stdout": "print('ok')\n",
            "stderr": "",
            "return_code": 0,
        },
        "meta": {
            "tool": "code:run",
            "resource_type": "code",
            "execution_time_ms": 1.2,
        },
    }

    assert format_tool_result(response) == "print('ok')"


def test_format_tool_result_preserves_error_behavior_for_failed_code_response():
    response = {
        "code": 1,
        "message": "read failed",
        "data": "ignored plain string payload",
        "meta": {
            "tool": "code:read",
            "resource_type": "code",
        },
    }

    assert format_tool_result(response) == "[Error] read failed"


def test_format_tool_result_returns_text_for_successful_mcp_response():
    response = {
        "code": 0,
        "message": "success",
        "data": {
            "content": [
                {"type": "text", "text": "ok"},
            ]
        },
        "meta": {
            "tool": "mcp:canvas.canvas_list_courses",
            "resource_type": "mcp",
            "execution_time_ms": 1.2,
        },
    }

    assert format_tool_result(response) == "ok"


def test_format_tool_result_handles_mixed_mcp_content_without_crashing():
    response = {
        "code": 0,
        "message": "success",
        "data": {
            "content": [
                {"type": "text", "text": "first"},
                {"type": "image", "mimeType": "image/png"},
                {"type": "text", "text": "second"},
            ]
        },
        "meta": {
            "tool": "mcp:canvas.canvas_list_courses",
            "resource_type": "mcp",
            "execution_time_ms": 1.2,
        },
    }

    assert format_tool_result(response) == "first\n[image content]\nsecond"


def test_format_tool_result_falls_back_to_structured_content_for_successful_mcp_response():
    response = {
        "code": 0,
        "message": "success",
        "data": {
            "content": [],
            "structuredContent": {
                "name": "Canvas",
                "status": "ok",
            },
        },
        "meta": {
            "tool": "mcp:canvas.canvas_health_check",
            "resource_type": "mcp",
            "execution_time_ms": 1.2,
        },
    }

    assert format_tool_result(response) == '{\n  "name": "Canvas",\n  "status": "ok"\n}'


def test_format_tool_result_prefers_structured_content_when_successful_mcp_content_has_no_text():
    response = {
        "code": 0,
        "message": "success",
        "data": {
            "content": [
                {"type": "image", "mimeType": "image/png"},
            ],
            "structuredContent": {
                "name": "Canvas",
                "status": "ok",
            },
        },
        "meta": {
            "tool": "mcp:canvas.canvas_health_check",
            "resource_type": "mcp",
            "execution_time_ms": 1.2,
        },
    }

    assert format_tool_result(response) == '{\n  "name": "Canvas",\n  "status": "ok"\n}'


def test_format_tool_result_preserves_error_behavior_for_failed_mcp_response():
    response = {
        "code": 1,
        "message": "mcp failed",
        "data": {
            "content": [
                {"type": "text", "text": "ignored"},
            ]
        },
        "meta": {
            "tool": "mcp:canvas.canvas_list_courses",
            "resource_type": "mcp",
        },
    }

    assert format_tool_result(response) == "[Error] mcp failed"

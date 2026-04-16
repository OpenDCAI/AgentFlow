ALL_MCP_SERVERS = (
    "arxiv-latex",
    "arxiv_local",
    "canvas",
    "emails",
    "excel",
    "fetch",
    "filesystem",
    "google_calendar",
    "google_forms",
    "google_sheet",
    "howtocook",
    "memory",
    "notion",
    "pdf-tools",
    "playwright_with_chunk",
    "pptx",
    "rail_12306",
    "scholarly",
    "snowflake",
    "terminal",
    "woocommerce",
    "word",
    "yahoo-finance",
    "youtube",
    "youtube-transcript",
)

PARALLEL_SAFE_MCP_SERVERS = ("filesystem", "terminal")

SERIAL_ONLY_MCP_SERVERS = tuple(
    name for name in ALL_MCP_SERVERS if name not in PARALLEL_SAFE_MCP_SERVERS
)

FILESYSTEM_TERMINAL_BOOTSTRAP_CASE = {
    "enabled_mcp_servers": ["filesystem", "terminal"],
    "write_action": "mcp:filesystem.write_file",
    "write_params": {"path": "hello.txt", "content": "bootstrap\n"},
    "verify_action": "mcp:terminal.run_command",
    "verify_params": {"command": "cat hello.txt"},
    "expected_signal": "bootstrap",
}


SERVER_SMOKE_CASES = {
    "arxiv-latex": {
        "action": "mcp:arxiv-latex.get_paper_abstract",
        "params": {"arxiv_id": "2401.00101"},
        "expected_signal": "differentiable topology optimization",
    },
    "arxiv_local": {
        "action": "mcp:arxiv_local.search_papers",
        "params": {"query": "transformer", "max_results": 1},
        "expected_signal": "transformer",
    },
    "canvas": {
        "action": "mcp:canvas.canvas_list_courses",
        "params": {},
        "expected_signal": "course_code",
    },
    "emails": {
        "action": "mcp:emails.get_folders",
        "params": {},
        "expected_signal": "inbox",
    },
    "excel": {
        "action": "mcp:excel.create_workbook",
        "params": {"filepath": "{workspace_root}/smoke.xlsx"},
        "expected_signal": "smoke.xlsx",
    },
    "fetch": {
        "action": "mcp:fetch.fetch_txt",
        "params": {"url": "{woocommerce_site_url}", "max_length": 500},
        "expected_signal": "woocommerce-pg-bridge",
    },
    "filesystem": {
        "action": "mcp:filesystem.create_directory",
        "params": {"path": "smoke-dir"},
        "expected_signal": "smoke-dir",
    },
    "google_calendar": {
        "action": "mcp:google_calendar.list_events",
        "params": {
            "calendar_id": "primary",
            "timeMin": "2026-04-01T00:00:00Z",
            "timeMax": "2026-04-30T23:59:59Z",
            "max_results": 1,
        },
        "expected_signal": "holiday30 campaign",
    },
    "google_forms": {
        "action": "mcp:google_forms.create_form",
        "params": {"title": "Smoke Form"},
        "expected_signal": "smoke form",
    },
    "google_sheet": {
        "action": "mcp:google_sheet.create_spreadsheet",
        "params": {"title": "Smoke Sheet"},
        "expected_signal": "smoke sheet",
    },
    "howtocook": {
        "action": "mcp:howtocook.mcp_howtocook_getRecipeById",
        "params": {"query": "可乐鸡翅"},
        "expected_signal": "可乐鸡翅",
    },
    "memory": {
        "action": "mcp:memory.read_graph",
        "params": {},
        "expected_signal": "entities",
    },
    "notion": {
        "action": "mcp:notion.API-get-users",
        "params": {},
        "expected_signal": "unauthorized",
    },
    "pdf-tools": {
        "action": "mcp:pdf-tools.get_pdf_info",
        "params": {
            "pdf_file_path": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        },
        "expected_signal": "total pages: 1",
    },
    "playwright_with_chunk": {
        "action": "mcp:playwright_with_chunk.browser_close",
        "params": {},
        "expected_signal": "no open tabs",
    },
    "pptx": {
        "action": "mcp:pptx.list_presentations",
        "params": {},
        "expected_signal": "total_presentations",
    },
    "rail_12306": {
        "action": "mcp:rail_12306.get-station-code-by-names",
        "params": {"stationNames": "北京南"},
        "expected_signal": "北京南",
    },
    "scholarly": {
        "action": "mcp:scholarly.search-google-scholar",
        "params": {"keyword": "deep learning"},
        "expected_signal": "deep learning",
    },
    "snowflake": {
        "action": "mcp:snowflake.read_query",
        "params": {"query": "SELECT 1 AS one"},
        "expected_signal": "one",
    },
    "terminal": {
        "action": "mcp:terminal.run_command",
        "params": {"command": "echo terminal-smoke"},
        "expected_signal": "terminal-smoke",
    },
    "woocommerce": {
        "action": "mcp:woocommerce.woo_customers_list",
        "params": {"perPage": 1},
        "expected_signal": "email",
    },
    "word": {
        "action": "mcp:word.list_available_documents",
        "params": {"directory": "."},
        "expected_signal": "test_doc.docx",
    },
    "yahoo-finance": {
        "action": "mcp:yahoo-finance.get_stock_info",
        "params": {"ticker": "AAPL"},
        "expected_signal": "aapl",
    },
    "youtube": {
        "action": "mcp:youtube.videos_searchVideos",
        "params": {"query": "test", "maxResults": 1},
        "expected_signal": "channeltitle",
    },
    "youtube-transcript": {
        "action": "mcp:youtube-transcript.get_video_info",
        "params": {"url": "https://www.youtube.com/watch?v=7ZQzGq32kAY"},
        "expected_signal": "afrobeat mix 2024",
    },
}


DOMAIN_SMOKE_CASES = {
    "canvas": {
        "enabled_mcp_servers": ["canvas", "filesystem"],
        "read_action": "mcp:canvas.canvas_list_courses",
        "read_params": {},
        "artifact_path": "reports/canvas_courses.json",
        "expected_signal": "course",
    },
    "snowflake": {
        "enabled_mcp_servers": ["snowflake", "filesystem"],
        "read_action": "mcp:snowflake.read_query",
        "read_params": {
            "query": (
                'SELECT * FROM sf_data."HR_ANALYTICS__PUBLIC__EMPLOYEES" LIMIT 3'
            )
        },
        "artifact_path": "reports/snowflake_hr.json",
        "expected_signal": "employee",
    },
    "woocommerce": {
        "enabled_mcp_servers": ["woocommerce", "filesystem"],
        "read_action": "mcp:woocommerce.woo_customers_list",
        "read_params": {"perPage": 2, "page": 1},
        "artifact_path": "reports/woocommerce_customers.json",
        "expected_signal": "customer",
    },
    "yahoo_finance": {
        "enabled_mcp_servers": ["yahoo-finance", "filesystem"],
        "read_action": "mcp:yahoo-finance.get_stock_info",
        "read_params": {"ticker": "AAPL"},
        "artifact_path": "reports/yahoo_finance_aapl.json",
        "expected_signal": "AAPL",
    },
    "youtube": {
        "enabled_mcp_servers": ["youtube", "filesystem"],
        "read_action": "mcp:youtube.videos_searchVideos",
        "read_params": {"query": "test", "maxResults": 1},
        "artifact_path": "reports/youtube_search.json",
        "expected_signal": "channeltitle",
    },
    "train": {
        "enabled_mcp_servers": ["rail_12306", "filesystem"],
        "read_action": "mcp:rail_12306.get-station-code-by-names",
        "read_params": {
            "stationNames": "\u5317\u4eac\u5357|\u4e0a\u6d77\u8679\u6865"
        },
        "artifact_path": "reports/train_station_codes.json",
        "expected_signal": "\u5317\u4eac\u5357",
    },
}

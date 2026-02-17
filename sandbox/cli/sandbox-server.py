#!/usr/bin/env python3
"""
Sandbox Server startup script.
Can be executed from any project directory.
"""

import sys
import argparse
import logging
import json
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional, Tuple

# Resolve project root.
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Add project root to Python path so the `sandbox` package is importable.
sys.path.insert(0, str(PROJECT_ROOT))


def setup_logging(level: str = "INFO"):
    """Configure logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def find_config_file(config_arg: str) -> Path:
    """
    Locate the configuration file.

    Supports:
    1. Absolute path.
    2. Relative path (relative to current working directory).
    """
    config_path = Path(config_arg).expanduser()
    if not config_path.is_absolute():
        config_path = Path.cwd() / config_path

    if config_path.exists():
        return config_path

    raise FileNotFoundError(f"Config file not found: {config_path}")


def resolve_server_endpoint(config_path: Path, cli_host: Optional[str], cli_port: Optional[int]) -> Tuple[str, int]:
    """
    Resolve server endpoint, preferring values from config (`server.url/port`).
    Falls back to CLI args and then defaults.
    """
    host = cli_host
    port = cli_port

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        raw = {}

    server_data = raw.get("server", {}) if isinstance(raw, dict) else {}
    config_url = str(server_data.get("url", "")).strip()
    config_host = str(server_data.get("host", "")).strip()
    config_port = server_data.get("port")

    if config_url:
        parsed = urlparse(config_url)
        if parsed.hostname:
            host = parsed.hostname
        if parsed.port:
            port = parsed.port

    if config_host:
        host = config_host
    if config_port is not None:
        try:
            port = int(config_port)
        except (TypeError, ValueError):
            pass

    host = host or "127.0.0.1"
    port = port if isinstance(port, int) else 18890
    return host, port


def main():
    parser = argparse.ArgumentParser(
        description="Start Sandbox Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --config /abs/path/to/dev.json
  %(prog)s --config ./configs/dev.json --port 8080
  %(prog)s --host 127.0.0.1 --port 9000
        """
    )

    parser.add_argument(
        "--config", "-c",
        type=str,
        required=True,
        help="Config file path (required, supports absolute or relative paths)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Server host (typically provided by config server.url/server.host)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=None,
        help="Server port (typically provided by config server.port)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log level (default: INFO)"
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show parsed configuration and exit"
    )

    args = parser.parse_args()

    # Configure logging.
    setup_logging(args.log_level)

    # Locate config file.
    config_path = find_config_file(args.config)
    host, port = resolve_server_endpoint(config_path, args.host, args.port)

    # Print startup info.
    print("=" * 80)
    print("🚀 Starting Sandbox Server...")
    print("=" * 80)
    print(f"📁 Project root: {PROJECT_ROOT}")
    print(f"⚙️  Config file: {config_path}")
    print(f"🌐 Service URL: http://{host}:{port}")
    print(f"📊 Log level: {args.log_level}")
    print("=" * 80)
    print()

    # Import and create server.
    try:
        from sandbox.server.config_loader import ConfigLoader

        # Load config.
        loader = ConfigLoader()
        config = loader.load(str(config_path))

        # Show config details.
        if args.show_config:
            print("\n📋 Configuration:")
            print(f"   Server title: {config.server.title}")
            print(f"   Session TTL: {config.server.session_ttl}s")
            print(f"\n   Enabled resources ({len(loader.get_enabled_resources())}):")
            for name, res in loader.get_enabled_resources().items():
                print(f"     ✅ {name}: {res.description}")
            print()
            return

        # Create server with standard flow.
        server = loader.create_server(host=host, port=port)

        # Start server.
        print("=" * 80)
        print("💡 Tip: configure warmup_resources in the client for backend warmup")
        print("   Example: Sandbox(config=SandboxConfig(warmup_resources=['rag']))")
        print("=" * 80)
        print("\n⏳ Server is starting, please wait...\n")

        # Use standard `server.run()` API.
        # It runs in the correct event loop and avoids warmup loop issues.
        server.run()

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Please ensure all dependencies are installed")
        print("   Tip: verify that PYTHONPATH is set correctly")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

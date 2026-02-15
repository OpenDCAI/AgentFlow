#!/usr/bin/env python3
"""
Sandbox Server startup script
Can be executed from any directory within the project
"""

import sys
import argparse
import logging
import json
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional, Tuple

# Get project root directory
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Add project root to Python path to ensure the sandbox package is importable
sys.path.insert(0, str(PROJECT_ROOT))


def setup_logging(level: str = "INFO"):
    """Configure logging"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def find_config_file(config_arg: str) -> Path:
    """
    Find the configuration file

    Supports only:
    1. Absolute path
    2. Relative path (relative to the current working directory)
    """
    config_path = Path(config_arg).expanduser()
    if not config_path.is_absolute():
        config_path = Path.cwd() / config_path

    if config_path.exists():
        return config_path

    raise FileNotFoundError(f"Configuration file not found: {config_path}")


def resolve_server_endpoint(config_path: Path, cli_host: Optional[str], cli_port: Optional[int]) -> Tuple[str, int]:
    """
    Resolve server address, prioritizing server.url/server.port from the config file.
    Falls back to CLI arguments if not specified in config, then to default values.
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
Examples:
  %(prog)s --config /abs/path/to/dev.json
  %(prog)s --config ./configs/dev.json --port 8080
  %(prog)s --host 127.0.0.1 --port 9000
        """
    )

    parser.add_argument(
        "--config", "-c",
        type=str,
        required=True,
        help="Path to config file (required, supports absolute or relative path)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Server host address (usually provided by config file server.url/server.host)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=None,
        help="Server port (usually provided by config file server.port)"
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
        help="Show configuration info and exit"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    # Find config file
    config_path = find_config_file(args.config)
    host, port = resolve_server_endpoint(config_path, args.host, args.port)

    # Display startup info
    print("=" * 80)
    print("🚀 Sandbox Server starting...")
    print("=" * 80)
    print(f"📁 Project root: {PROJECT_ROOT}")
    print(f"⚙️  Config file: {config_path}")
    print(f"🌐 Server address: http://{host}:{port}")
    print(f"📊 Log level: {args.log_level}")
    print("=" * 80)
    print()

    # Import and create server
    try:
        from sandbox.server.config_loader import ConfigLoader

        # Load configuration
        loader = ConfigLoader()
        config = loader.load(str(config_path))

        # Show configuration info
        if args.show_config:
            print("\n📋 Configuration info:")
            print(f"   Server title: {config.server.title}")
            print(f"   Session TTL: {config.server.session_ttl}s")
            print(f"\n   Enabled resources ({len(loader.get_enabled_resources())}):")
            for name, res in loader.get_enabled_resources().items():
                print(f"     ✅ {name}: {res.description}")
            print()
            return

        # Create server (using standard method)
        server = loader.create_server(host=host, port=port)

        # Start server
        print("=" * 80)
        print(f"🌐 Access URL: http://{host}:{port}")
        print(f"📖 API docs: http://{host}:{port}/docs")
        print(f"🔍 Health check: http://{host}:{port}/health")
        print()
        print(f"💡 Tip: For resource warmup, configure the warmup_resources parameter on the client side")
        print(f"   Example: Sandbox(config=SandboxConfig(warmup_resources=['rag']))")
        print("=" * 80)
        print("\n⏳ Server is starting, please wait...\n")

        # Use the standard server.run() method
        # This runs in the correct event loop without warmup issues
        server.run()

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"   Please make sure all dependencies are installed")
        print(f"   Tip: Check if PYTHONPATH is set correctly")
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

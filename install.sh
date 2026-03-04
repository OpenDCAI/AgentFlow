#!/bin/bash
set -e

echo "============================================"
echo "  AgentFlow - One-Click Installation"
echo "============================================"
echo ""

# Check Python version
PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python not found. Please install Python 3.8+ first."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "[INFO] Using $PYTHON_CMD ($PYTHON_VERSION)"

# Check pip
PIP_CMD="$PYTHON_CMD -m pip"
if ! $PIP_CMD --version &>/dev/null; then
    echo "[ERROR] pip not found. Please install pip first."
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Parse arguments
INSTALL_ALL=false
INSTALL_OPTIONAL_ML=false
INSTALL_OPTIONAL_CLOUD=false

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --all         Install all dependencies including optional ones"
    echo "  --ml          Install optional ML/DL dependencies (torch, transformers, etc.)"
    echo "  --cloud       Install optional Alibaba Cloud dependencies"
    echo "  --help        Show this help message"
    echo ""
    echo "By default, only core dependencies are installed."
}

for arg in "$@"; do
    case $arg in
        --all)
            INSTALL_ALL=true
            ;;
        --ml)
            INSTALL_OPTIONAL_ML=true
            ;;
        --cloud)
            INSTALL_OPTIONAL_CLOUD=true
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "[WARN] Unknown option: $arg"
            ;;
    esac
done

# Install core dependencies
echo ""
echo "[1/3] Installing core dependencies..."
$PIP_CMD install -r "$PROJECT_DIR/requirements.txt"
echo "[OK]  Core dependencies installed."

# Install optional ML/DL dependencies
if [ "$INSTALL_ALL" = true ] || [ "$INSTALL_OPTIONAL_ML" = true ]; then
    echo ""
    echo "[2/3] Installing optional ML/DL dependencies..."
    $PIP_CMD install "torch>=2.6.0" "transformers>=4.51.1" "accelerate>=1.5.1" torchvision
    echo "[OK]  ML/DL dependencies installed."
else
    echo ""
    echo "[2/3] Skipping optional ML/DL dependencies. Use --ml or --all to install."
fi

# Install optional Alibaba Cloud dependencies
if [ "$INSTALL_ALL" = true ] || [ "$INSTALL_OPTIONAL_CLOUD" = true ]; then
    echo ""
    echo "[3/3] Installing optional Alibaba Cloud dependencies..."
    $PIP_CMD install alibabacloud-ecs20140526 alibabacloud-tea-openapi alibabacloud-tea-util
    echo "[OK]  Alibaba Cloud dependencies installed."
else
    echo ""
    echo "[3/3] Skipping optional Alibaba Cloud dependencies. Use --cloud or --all to install."
fi

# Install Playwright browsers
echo ""
echo "[INFO] Installing Playwright browsers..."
$PYTHON_CMD -m playwright install chromium 2>/dev/null || echo "[WARN] Playwright browser install failed, you can run 'playwright install' manually."

echo ""
echo "============================================"
echo "  Installation complete!"
echo "============================================"
echo ""
echo "Quick start:"
echo "  ./start_sandbox_server.sh --config configs/sandbox-server/web_config.json --port 18890 --host 0.0.0.0"
echo ""

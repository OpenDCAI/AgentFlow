# Synthesis Project - Makefile
# 提供便捷的命令来管理项目

.PHONY: help server server-dev server-prod server-minimal synthesis clean test kill-server

# 默认目标
.DEFAULT_GOAL := help

# 设置 Python 路径
export PYTHONPATH := $(shell pwd)/sandbox:$(PYTHONPATH)

# 配置路径
CONFIG_DIR := sandbox/configs/profiles

# ============================================================================
# 帮助信息
# ============================================================================

help:
	@echo "Synthesis Project - 可用命令:"
	@echo ""
	@echo "  Sandbox Server:"
	@echo "    make server              - 启动 Sandbox Server (开发模式)"
	@echo "    make server-dev          - 启动 Sandbox Server (开发模式)"
	@echo "    make server-prod         - 启动 Sandbox Server (生产模式)"
	@echo "    make server-minimal      - 启动 Sandbox Server (最小配置)"
	@echo ""
	@echo "  RAG Synthesis:"
	@echo "    make synthesis           - 运行 RAG 合成流程"
	@echo ""
	@echo "  维护:"
	@echo "    make clean               - 清理临时文件"
	@echo "    make test                - 运行测试"
	@echo "    make kill-server         - 清理端口 18890 的进程"
	@echo ""
	@echo "  示例:"
	@echo "    make server                                    # 启动开发服务器"
	@echo "    make server-dev                                # 启动开发服务器"
	@echo "    make server-prod PORT=8080                     # 生产模式，端口 8080"
	@echo "    make synthesis CONFIG=config.json SEEDS=seeds.jsonl"
	@echo ""

# ============================================================================
# Sandbox Server 命令
# ============================================================================

# 默认启动（开发模式）
server: server-dev

# 开发环境
server-dev:
	@echo "🚀 Starting Sandbox Server (Dev Mode)..."
	@bin/sandbox-server.py --config dev.json $(if $(PORT),--port $(PORT),) $(if $(HOST),--host $(HOST),)

# 生产环境
server-prod:
	@echo "🚀 Starting Sandbox Server (Production Mode)..."
	@bin/sandbox-server.py --config production.json $(if $(PORT),--port $(PORT),) $(if $(HOST),--host $(HOST),)

# 最小配置
server-minimal:
	@echo "🚀 Starting Sandbox Server (Minimal Mode)..."
	@bin/sandbox-server.py --config minimal.json $(if $(PORT),--port $(PORT),) $(if $(HOST),--host $(HOST),)

# 自定义配置
server-custom:
	@if [ -z "$(CONFIG)" ]; then \
		echo "❌ 请指定配置文件: make server-custom CONFIG=path/to/config.json"; \
		exit 1; \
	fi
	@echo "🚀 Starting Sandbox Server (Custom Config: $(CONFIG))..."
	@bin/sandbox-server.py --config $(CONFIG) $(if $(PORT),--port $(PORT),) $(if $(HOST),--host $(HOST),)

# 显示配置信息
server-show-config:
	@bin/sandbox-server.py --config $(if $(CONFIG),$(CONFIG),dev.json) --show-config

# ============================================================================
# RAG Synthesis 命令
# ============================================================================

synthesis:
	@if [ -z "$(CONFIG)" ]; then \
		echo "❌ 请指定配置文件: make synthesis CONFIG=config.json SEEDS=seeds.jsonl"; \
		exit 1; \
	fi
	@if [ -z "$(SEEDS)" ]; then \
		echo "❌ 请指定种子文件: make synthesis CONFIG=config.json SEEDS=seeds.jsonl"; \
		exit 1; \
	fi
	@echo "🚀 Running RAG Synthesis Pipeline..."
	@PYTHONPATH=$(shell pwd):$(PYTHONPATH) python3 rag_synthesis/pipeline.py --config $(CONFIG) --seeds $(SEEDS) $(if $(OUTPUT),--output-dir $(OUTPUT),)

# ============================================================================
# 维护命令
# ============================================================================

clean:
	@echo "🧹 Cleaning temporary files..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

test:
	@echo "🧪 Running tests..."
	@PYTHONPATH=$(shell pwd)/sandbox:$(PYTHONPATH) python3 -m pytest tests/ -v
	@PYTHONPATH=$(shell pwd)/sandbox:$(PYTHONPATH) python3 -m pytest sandbox/tests/ -v

# ============================================================================
# 进程管理命令
# ============================================================================

# 清理 Sandbox Server 进程
kill-server:
	@echo "🧹 清理端口 $(if $(PORT),$(PORT),18890) 的进程..."
	@bin/kill-server.sh $(if $(PORT),$(PORT),) $(if $(FORCE),--force,)

# 重启服务器
restart-server: kill-server
	@sleep 1
	@echo "🔄 重启服务器..."
	@$(MAKE) server

# ============================================================================
# 开发辅助命令
# ============================================================================

# 检查环境
check-env:
	@echo "🔍 Checking environment..."
	@echo "   Python: $$(python3 --version)"
	@echo "   Project Root: $(shell pwd)"
	@echo "   PYTHONPATH: $$PYTHONPATH"
	@echo ""
	@echo "   Checking dependencies..."
	@python3 -c "import fastapi; print('   ✅ fastapi')" 2>/dev/null || echo "   ❌ fastapi (pip install fastapi)"
	@python3 -c "import uvicorn; print('   ✅ uvicorn')" 2>/dev/null || echo "   ❌ uvicorn (pip install uvicorn)"
	@python3 -c "import aiohttp; print('   ✅ aiohttp')" 2>/dev/null || echo "   ❌ aiohttp (pip install aiohttp)"

# 安装依赖（如果有 requirements.txt）
install:
	@if [ -f requirements.txt ]; then \
		echo "📦 Installing dependencies..."; \
		pip install -r requirements.txt; \
	else \
		echo "⚠️  No requirements.txt found"; \
	fi

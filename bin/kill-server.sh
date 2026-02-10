#!/usr/bin/env bash
# 清理指定端口的进程及其所有子进程
# 默认端口: 18890

set -e

# 默认端口
DEFAULT_PORT=18890
PORT="${1:-$DEFAULT_PORT}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🧹 清理端口 ${PORT} 的进程${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 查找占用端口的进程
find_port_process() {
    local port=$1
    # 使用 lsof 或 netstat 查找进程
    if command -v lsof &> /dev/null; then
        lsof -ti:$port 2>/dev/null
    elif command -v ss &> /dev/null; then
        ss -lptn "sport = :$port" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1
    elif command -v netstat &> /dev/null; then
        netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1
    else
        echo -e "${RED}❌ 错误: 未找到 lsof, ss 或 netstat 命令${NC}"
        exit 1
    fi
}

# 获取进程的所有子进程（递归）
get_all_children() {
    local pid=$1
    local children=$(pgrep -P $pid 2>/dev/null || true)

    echo "$children"

    for child in $children; do
        get_all_children $child
    done
}

# 显示进程信息
show_process_info() {
    local pid=$1
    if [ -n "$pid" ] && kill -0 $pid 2>/dev/null; then
        local cmd=$(ps -p $pid -o cmd= 2>/dev/null || echo "未知")
        local user=$(ps -p $pid -o user= 2>/dev/null || echo "未知")
        echo -e "  ${YELLOW}PID${NC}: $pid"
        echo -e "  ${YELLOW}用户${NC}: $user"
        echo -e "  ${YELLOW}命令${NC}: $cmd"
    fi
}

# 杀死进程树
kill_process_tree() {
    local pid=$1
    local signal=${2:-TERM}

    if [ -z "$pid" ]; then
        return
    fi

    # 获取所有子进程
    local all_pids=($pid)
    local children=$(get_all_children $pid)

    if [ -n "$children" ]; then
        all_pids+=($children)
    fi

    # 去重
    local unique_pids=($(echo "${all_pids[@]}" | tr ' ' '\n' | sort -u))

    echo -e "${YELLOW}📋 找到以下进程:${NC}"
    for p in "${unique_pids[@]}"; do
        if kill -0 $p 2>/dev/null; then
            show_process_info $p
            echo ""
        fi
    done

    # 询问确认
    if [ "$FORCE" != "true" ]; then
        echo -e "${YELLOW}⚠️  将要杀死 ${#unique_pids[@]} 个进程${NC}"
        read -p "确认继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}❌ 已取消${NC}"
            exit 0
        fi
    fi

    # 先尝试 SIGTERM（优雅关闭）
    echo -e "${BLUE}📤 发送 SIGTERM 信号...${NC}"
    for p in "${unique_pids[@]}"; do
        if kill -0 $p 2>/dev/null; then
            kill -TERM $p 2>/dev/null && echo -e "  ${GREEN}✓${NC} 已发送 SIGTERM 到 PID $p" || true
        fi
    done

    # 等待进程退出
    echo -e "${BLUE}⏳ 等待进程退出 (最多 5 秒)...${NC}"
    local waited=0
    local all_dead=false
    while [ $waited -lt 5 ]; do
        all_dead=true
        for p in "${unique_pids[@]}"; do
            if kill -0 $p 2>/dev/null; then
                all_dead=false
                break
            fi
        done

        if [ "$all_dead" = true ]; then
            break
        fi

        sleep 1
        waited=$((waited + 1))
        echo -e "  ${YELLOW}⏳${NC} 已等待 ${waited}s..."
    done

    # 如果还有进程存活，使用 SIGKILL 强制杀死
    if [ "$all_dead" = false ]; then
        echo -e "${RED}⚠️  部分进程未响应，使用 SIGKILL 强制杀死...${NC}"
        for p in "${unique_pids[@]}"; do
            if kill -0 $p 2>/dev/null; then
                kill -KILL $p 2>/dev/null && echo -e "  ${RED}✓${NC} 已发送 SIGKILL 到 PID $p" || true
            fi
        done
        sleep 1
    fi

    # 验证所有进程已被杀死
    local remaining=0
    for p in "${unique_pids[@]}"; do
        if kill -0 $p 2>/dev/null; then
            remaining=$((remaining + 1))
            echo -e "  ${RED}✗${NC} PID $p 仍在运行"
        fi
    done

    if [ $remaining -eq 0 ]; then
        echo -e "${GREEN}✅ 所有进程已成功清理${NC}"
        return 0
    else
        echo -e "${RED}❌ 有 $remaining 个进程清理失败${NC}"
        return 1
    fi
}

# 主逻辑
main() {
    # 查找占用端口的主进程
    echo -e "${BLUE}🔍 查找占用端口 ${PORT} 的进程...${NC}"
    MAIN_PID=$(find_port_process $PORT)

    if [ -z "$MAIN_PID" ]; then
        echo -e "${GREEN}✅ 端口 ${PORT} 未被占用${NC}"
        exit 0
    fi

    echo -e "${YELLOW}📍 找到主进程 PID: ${MAIN_PID}${NC}"
    echo ""

    # 显示主进程信息
    show_process_info $MAIN_PID
    echo ""

    # 杀死进程树
    kill_process_tree $MAIN_PID

    # 再次检查端口
    echo ""
    echo -e "${BLUE}🔍 验证端口状态...${NC}"
    VERIFY_PID=$(find_port_process $PORT)

    if [ -z "$VERIFY_PID" ]; then
        echo -e "${GREEN}✅ 端口 ${PORT} 已释放${NC}"
    else
        echo -e "${RED}❌ 端口 ${PORT} 仍被占用 (PID: ${VERIFY_PID})${NC}"
        exit 1
    fi
}

# 帮助信息
show_help() {
    cat << EOF
用法: $0 [PORT] [OPTIONS]

清理指定端口的进程及其所有子进程

参数:
  PORT              要清理的端口号 (默认: 18890)

选项:
  -f, --force       强制清理，不询问确认
  -h, --help        显示此帮助信息

示例:
  $0                # 清理端口 18890
  $0 8080           # 清理端口 8080
  $0 18890 --force  # 强制清理端口 18890，不询问确认

EOF
}

# 解析参数
FORCE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        [0-9]*)
            PORT=$1
            shift
            ;;
        *)
            echo -e "${RED}❌ 未知参数: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
done

# 执行主逻辑
main

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🎉 清理完成！${NC}"
echo -e "${BLUE}========================================${NC}"

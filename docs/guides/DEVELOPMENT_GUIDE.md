# AgentFlow 开发指南

本文档概述 AgentFlow 项目的目录结构、开发步骤与常用工作流，帮助你快速上手并进行功能扩展。

## 1. 项目结构概览

```
AgentFlow/
├─ src/
│  ├─ run_osworld.py          # 主入口，负责解析参数、运行 Benchmark
│  ├─ envs/                   # 各类 Environment 定义及基类
│  │  ├─ enviroment.py        # Environment 与 Tool 基类
│  │  ├─ osworld_environment.py
│  │  ├─ ...
│  ├─ utils/
│  │  ├─ desktop_env/         # OSWorld 桌面环境相关实现
│  │  ├─ osworld-settings/    # 迁移自 OSWorld 的配置模板
│  ├─ data/                   # 示例 Benchmark 数据
│  └─ ...
├─ ENVIRONMENT_DEVELOPMENT_GUIDE.md  # 环境扩展指南
├─ DEVELOPMENT_GUIDE.md (本文)
└─ README / 日志等
```

## 2. 开发流程

1. **准备环境**
   - 推荐在 Conda 或虚拟环境中安装依赖（详见 README）。
   - 确保你有 OSWorld 所需的云账号 / VNC 访问权限。

2. **选择或创建环境**
   - 所有环境都通过 `envs.factory.create_environment()` 创建。
   - 新增环境请参考 `ENVIRONMENT_DEVELOPMENT_GUIDE.md`。

3. **编写或修改任务数据**
   - 基准数据使用 JSONL，每行一个任务，存放在 `src/data/`。
   - OSWorld 任务通常来自原始 `OSWorld/evaluation_examples`，可以按需转换。

4. **运行 Benchmark**
   ```bash
   python src/run_osworld.py \
     --mode osworld \
     --data src/data/osworld_examples.jsonl \
     --provider-name aliyun \
     --output-dir results \
     [其他参数]
   ```
   - `--parallel` 和 `--max-workers` 控制多进程。
   - `--action-space`、`--observation-type` 等参数会透传给环境。

5. **查看结果**
   - 日志输出在终端。
   - 每个任务在 `results/<mode>/<task_id>/<model>/` 下有 `trajectory.json`、`conversation.json`、录屏等文件。
   - 总体评估写入 `result_*.jsonl.jsonl` 与 `evaluation_*.json`。

## 3. 常用开发点

- **环境工厂**：`src/envs/factory.py`，支持 `register_environment()` 注册新环境。
- **多进程执行**：`run_osworld.py` 中的 `run_env_tasks_agentflow()` 负责 worker 逻辑。
- **结果评估**：`src/benchmark/benchmark.py`，可自定义指标。
- **代理配置**：`src/utils/desktop_env/controllers/setup.py` 读取 `src/utils/osworld-settings/proxy/dataimpulse.json`。

## 4. 代码规范与测试

- 遵循现有代码风格（PEP8）。
- 重要逻辑推荐添加单元测试或回归脚本。
- 修改 OSWorld 相关代码时，确保多进程/并行模式能正常运行。

## 5. 文档与支持

- 环境扩展细节：`ENVIRONMENT_DEVELOPMENT_GUIDE.md`
- OSWorld 原始文档：`OSWorld/README` 及 `evaluation_examples`
- 需要疑难排查时，可查看 `results/*` 中的轨迹与日志，或调试 `src/utils/desktop_env`。

欢迎根据项目演进补充更多开发经验和规范。

# 并行数据合成快速开始

## 快速开始示例

### 1. 串行模式（默认）

```bash
cd /home/a1/work/AgentFlow/src/data_synthesis

# 使用默认配置（max_workers=1，串行处理）
./run_parallel_synthesis.sh web example_seed_entities.json
```

### 2. 并行模式（推荐）

**步骤1**: 修改配置文件，设置并行度

```bash
# 编辑配置文件
nano configs/web_config.json
```

添加或修改 `max_workers` 参数：

```json
{
  "environment_mode": "web",
  ...
  "max_workers": 4
}
```

**步骤2**: 运行并行合成

```bash
./run_parallel_synthesis.sh web example_seed_entities.json
```

### 3. 使用预配置的并行配置

我们已经创建了一个示例并行配置文件：

```bash
# 使用 max_workers=4 的并行配置
./run_parallel_synthesis.sh custom configs/web_config_parallel.json example_seed_entities.json
```

## 性能对比测试

### 测试场景: 10个seeds

**串行模式** (max_workers=1):
```bash
# 修改配置: max_workers=1
./run_parallel_synthesis.sh web example_seed_entities.json

# 预计时间: ~10分钟（假设每个seed需要1分钟）
```

**并行模式** (max_workers=4):
```bash
# 修改配置: max_workers=4
./run_parallel_synthesis.sh web example_seed_entities.json

# 预计时间: ~3分钟（理论加速比 3-4x）
```

## 配置建议

### 根据CPU核心数选择并行度

```bash
# 查看CPU核心数
nproc

# 建议配置
# 4核CPU -> max_workers: 2-4
# 8核CPU -> max_workers: 4-8
# 16核CPU -> max_workers: 8-12
```

### 根据API限制调整

如果你的OpenAI API有限流：
- **免费账户**: `max_workers: 1-2`
- **付费账户**: `max_workers: 4-8`
- **企业账户**: `max_workers: 8-16`

## 实时监控

运行时你会看到类似输出：

```
==========================================
🚀 通用Agent数据合成 Pipeline 启动
==========================================
环境模式: web
并行度: 4 workers
总Seed数量: 10
==========================================

⚡ 使用并行处理模式（4 workers）

################################################################################
Worker处理 Seed 1
Source ID: src_20251031005703_0001_a1b2c3d4
内容: Tesla Inc
################################################################################

📊 步骤 1/3: Trajectory Sampling
🎯 步骤 2/3: Trajectory Selection
✨ 步骤 3/3: QA Synthesis
✅ Seed 1 完成! 生成了 3 个QA对

📊 进度: 1/10 seeds 已完成
📊 进度: 2/10 seeds 已完成
...
📊 进度: 10/10 seeds 已完成

==========================================
🎉 数据合成完成!
==========================================
总共处理: 10 个 Seed
成功生成: 28 个QA对
==========================================
```

## 常见问题

### Q1: 并行处理时如何知道哪个seed失败了？

A: 每个seed都有唯一的 `source_id`，失败时会在日志中显示。你也可以检查输出的QA文件，看哪些source_id缺失。

### Q2: 可以中断并行处理吗？

A: 可以使用 `Ctrl+C` 中断。已完成的QA对会保存，未完成的会丢失。

### Q3: 并行处理的结果顺序会乱吗？

A: 是的，结果按完成顺序保存，不是输入顺序。但每个QA都有 `source_id` 追溯来源。

### Q4: 如何只重新处理失败的seeds？

A: 创建一个新的seed文件，只包含失败的seeds，然后重新运行。

## 完整示例流程

```bash
# 1. 进入工作目录
cd /home/a1/work/AgentFlow/src/data_synthesis

# 2. 准备seeds文件（如果还没有）
cat > my_seeds.json << 'EOF'
[
  "Apple Inc",
  "Google LLC",
  "Microsoft Corporation",
  "Amazon.com",
  "Tesla Inc"
]
EOF

# 3. 复制并修改配置文件
cp configs/web_config.json configs/my_config.json
# 编辑 my_config.json，设置 "max_workers": 4

# 4. 运行并行合成
./run_parallel_synthesis.sh custom configs/my_config.json my_seeds.json my_results

# 5. 查看结果
ls -lh my_results/
cat my_results/synthesized_qa_*.jsonl | head -20
```

## 下一步

- 阅读 [PARALLEL_PROCESSING.md](PARALLEL_PROCESSING.md) 了解详细配置
- 调整配置文件中的其他参数（max_depth, branching_factor等）
- 准备更多seeds，批量生成数据


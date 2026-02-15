<div align="center">
  <img src="assets/overall.png">

[![Datasets](https://img.shields.io/badge/Datasets-5EDDD2?style=for-the-badge&logo=huggingface&logoColor=yellow)](https://huggingface.co/collections/OpenDCAI/agentflow-models)
[![Models](https://img.shields.io/badge/Models-4285F4?style=for-the-badge&logo=huggingface&logoColor=yellow)](https://huggingface.co/collections/OpenDCAI/agentflow-models)
[![GITHUB](https://img.shields.io/badge/Github-24292F?style=for-the-badge&logo=github&logoColor=white)](https://github.com/OpenDCAI/AgentFlow)
[![Docmutation](https://img.shields.io/badge/Docmutation-red?style=for-the-badge&logo=google-chrome&logoColor=white)](https://opendcai.github.io/AgentFlow-Doc/en/)
 </div>

<p align="center">
  <a href="README.md">English</a> | <b>中文</b>
</p>

**首个统一的 Agent 数据合成框架**，为自定义任务提供一体化环境。

## 🚀 概览

**AgentFlow** 是**首个统一的、大规模 Agent 数据合成框架**，能够系统性地生成高质量的训练和评估数据——无论是在**单一专用环境**中，还是跨**异构 Agent 环境**——涵盖 📚 RAG（检索增强生成）、🖼️ MM-Doc（多模态文档理解）、🔍 深度研究 Agent、🖱️ GUI / 工具使用 Agent、📊 数据分析 Agent、🤖 具身 Agent 等。

不同于以往针对特定任务或单一环境的解决方案，AgentFlow 提供了一个**统一的一体化环境**——通用、可扩展、可规模化——用于合成 Agent 轨迹、推理链、工具交互和环境反馈。

通过构建多样化、贴近真实场景的环境，AgentFlow 能够训练**工业级 Agent 基础模型**——通过数据级或参数级的 Agent 整合，实现跨多领域的无缝运行。

> **一个框架，所有 Agent 世界。**

## ✨ 核心特性

### 🧠 统一的 Agent 数据合成范式

AgentFlow 提供了一个**统一的抽象层**，通过单一、一致的接口实现跨异构 Agent 环境的无缝数据合成。

**支持的环境：**
- 📚 **RAG** — 多跳推理的检索增强生成
- 🖼️ **MM-Doc** — 多模态文档理解与视觉问答
- 🔍 **深度研究** — 网络级信息收集与综合
- 💻 **代码** — 带执行反馈的编程任务
- 🖱️ **GUI** — 桌面和 Web UI 交互
- 🤖 **具身** — 物理世界仿真与导航

**核心优势：**
- **一次编写，处处合成** — 定义一次合成逻辑，无需重写流水线即可应用
- **环境无关的工具链** — 共享的任务生成、轨迹记录和质量控制工具
- **无缝扩展** — 通过单一协调工作流跨领域生成海量多样化轨迹

这种统一方法消除了为每个 Agent 领域维护独立、不兼容数据流水线的传统障碍，使基础模型团队能够高效地大规模训练**通用 Agent 模型**。

### 探索 Agent 整合：从专家到通才

随着 Agent 在不同环境中趋于专业化，一个关键挑战随之而来：**如何将异构能力整合到单一的基础 Agent 模型中？** 我们系统性地研究了两种主要策略：

- **数据级整合：** 在所有领域的混合轨迹上联合训练统一模型。作为强大、稳定的基线，但面临较高的重训练成本。
- **参数级整合：** 在参数空间中合并独立训练的专家模型。计算效率高，但需要精心设计以缓解任务间的干扰。

## 🛠️ 快速开始

以 WebAgent 数据合成为例。

**第一步：** 使用 WebAgent 沙箱配置启动沙箱。

```bash
./sandbox-server.sh --config configs/sandbox-server/web_config.json \
    --port 18890 \
    --host 0.0.0.0
```

**第二步：** 使用 WebAgent 合成配置合成 QA。

```python
from synthesis import synthesize

synthesize(config_path="configs/synthesis/web_config.json")
```

**第三步：** 使用 WebAgent 轨迹配置合成轨迹。

```python
from rollout import pipeline

pipeline(config_path="configs/rollout/rag_benchmark.json")
```

**第四步：** 模型训练完成后，使用 vLLM 部署模型。

```bash
vllm serve \
    --model YOUR_TRAINED_MODEL \
    --served-model-name webagent \
    --tensor-parallel-size 8 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --port 8222
```

**第五步：** 使用推理配置对训练好的 Agent 模型进行推理。

```python
from rollout import pipeline

pipeline(config_path="configs/infer/web_infer.json")
```

## ⚙️ 配置说明

| 用途 | 配置路径 |
| ---- | ------- |
| 🖥️ 启动沙箱 | [`configs/sandbox-server/`](https://github.com/OpenDCAI/AgentFlow/tree/main/configs/sandbox-server/) |
| 🧪 合成 QA | [`configs/synthesis/`](https://github.com/OpenDCAI/AgentFlow/tree/main/configs/synthesis/) |
| 🔄 轨迹合成 | [`configs/trajectory/`](https://github.com/OpenDCAI/AgentFlow/tree/main/configs/trajectory/) |
| 🚀 模型推理 | [`configs/infer/`](https://github.com/OpenDCAI/AgentFlow/tree/main/configs/infer/) |

## 🌟 AgentFlow Agent 系列

### 论文

AgentFlow 拥有丰富的 Agent 系列，更多信息请参阅以下论文：

[1] [DocDancer: Towards Agentic Document-Grounded Information Seeking](https://arxiv.org/pdf/2601.05163)

[2] [RAGShaper: Eliciting Sophisticated Agentic RAG Skills via Automated Data Synthesis](https://arxiv.org/pdf/2601.08699)

[3] [Exploring Information Seeking Agent Consolidation](https://www.arxiv.org/pdf/2602.00585)

### 模型

| Agent | 🤗 HuggingFace |
| ----- | -------------- |
| MM-Doc | [DocDancer](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-DocDancer) |
| RAG | [RAGShaper](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-RAGShaper) |
| DeepResearch | [DeepResearch Agent](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-Web) |
| General-datamix | [Agent-datamix](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-DataMix) |
| General-RegMeanpp | [Agent-RegMeanpp](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-RegMeanpp) |

### 数据集

| Agent | 🤗 HuggingFace |
| ----- | -------------- |
| MM-Doc | [DocDancer](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-DocDancer) |
| RAG | [RAGShaper](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-RAGShaper) |
| DeepResearch | [DeepResearch Agent](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-Web) |

## 🧪 整体性能

### Qwen3-30B-A3B-Think

| 层级 | **策略** | **Web: GAIA (Acc.)** | **Web: BC (Acc.)** | **Web: BC-zh (Acc.)** | **Doc: MMBD (Acc.)** | **Doc: DocB (Acc.)** | **RAG: HotPotQA (EM/F1)** | **RAG: AmbigQA (F1/EM)** | **RAG: Bamboogle (F1/EM)** |
| ---- | ------- | -------------------- | ------------------ | --------------------- | -------------------- | -------------------- | ------------------------- | ------------------------ | -------------------------- |
| **数据级** | Data Mixing | **64.08** | **28.00** | **34.00** | 63.59 | **83.29** | 38.00 / 42.53 | 49.50 / 58.84 | 53.10 / 60.20 |
| **参数级** | RegMean++ | 60.19 | 22.50 | 28.00 | 64.66 | 80.76 | 45.50 / 58.27 | 58.80 / 69.36 | **52.80 / 66.48** |

### 🔗 RAG Agent 案例与性能

Agentic RAG 是一种方法，自主 Agent 主动决定如何以及何时检索信息，并在此基础上进行推理以完成任务。

| 模型 | Bamboogle EM | Bamboogle F1 | PopQA EM | PopQA F1 | NQ EM | NQ F1 | AmbigQA EM | AmbigQA F1 | Avg EM | Avg F1 |
| ---- | ------------ | ------------ | -------- | -------- | ----- | ----- | ---------- | ---------- | ------ | ------ |
| **基于提示词的方法** | | | | | | | | | | |
| IR-COT | 16.0 | 27.9 | 32.4 | 39.9 | 19.3 | 35.5 | 24.5 | 40.6 | 23.1 | 36.0 |
| RECOMP | 21.7 | 28.6 | 40.5 | 45.8 | – | – | – | – | – | – |
| Search-o1 | 30.4 | 39.9 | 47.0 | 50.0 | 30.3 | 40.7 | 42.5 | 53.4 | 37.6 | 46.0 |
| **基于学习的方法** | | | | | | | | | | |
| Search-R1 | 30.4 | 43.2 | 41.3 | 46.4 | 36.0 | 45.0 | 49.2 | 60.4 | 39.2 | 48.8 |
| ReasonRAG | 22.4 | 29.1 | 41.1 | 44.4 | 28.1 | 38.9 | 39.7 | 51.9 | 32.8 | 41.1 |
| HL-Data 4.5k | 50.4 | 67.5 | 35.2 | 48.3 | 31.5 | 47.4 | 52.1 | 69.0 | 42.3 | 58.0 |
| **Ours** | | | | | | | | | | |
| **RAGShaper 4.5k** | 58.5 | 70.3 | 37.4 | 47.8 | 38.3 | 50.0 | **61.3** | **71.4** | 48.8 | 59.8 |
| **RAGShaper 6.5k** | **60.0** | **72.6** | 38.9 | 49.6 | **41.3** | **54.8** | 61.1 | 71.1 | **50.3** | **62.0** |

```
🙋 问题

一部由神圣罗马帝国皇帝（其统治始于 1508 年）委托创作的重要文学作品，是其宏大艺术遗产的一部分。
尽管这位赞助者在此期间委托创作了著名的手稿合集，但这部特定的寓言史诗是专为印刷机设计的，
以确保更广泛的受众。**其初版的确切出版年份是什么？**

💡 答案
1517
```

### 🔬 文档 Agent 案例与性能

文档 Agent 通过导航、提取和推理异构内容（包括文本、表格、图表和图像）来回答跨多页文档的复杂问题。

### 基准测试结果对比

| 方法 | 模型 | MMLongBench-Doc acc | F1 | LasJ | DocBench LasJ |
| ---- | ---- | ------------------- | -- | ---- | ------------- |
| **基于 OCR 的基线** | | | | | |
| Tesseract | GPT-4o | 30.1 | 30.5 | — | — |
| Tesseract | Gemini-2.0-Flash | 39.6 | 37.2 | — | — |
| **基于 RAG 的基线** | | | | | |
| VisRAG | GPT-4o | 29.0 | 27.8 | — | — |
| RAGAnything | GPT-4o-mini | 42.8 | — | — | 63.4 |
| **基于提示词的 Agent** | | | | | |
| Doc-React | GPT-4o | 38.1 | 38.3 | — | — |
| MDocAgent | GPT-4o | 42.0 | — | — | — |
| SimpleDoc | Claude-4-Sonnet | — | — | 58.6 | — |
| DocLens | Claude-4-Sonnet | — | — | 63.3 | — |
| **Ours** | | | | | |
| DocDancer | Qwen3-4B (ft) | 48.4 | 49.2 | 59.4 | 79.8 |
| DocDancer | Qwen3-30B-A3B (ft) | 54.4 | 53.9 | 65.3 | 81.2 |
| **人类基线** | — | 65.8 | 66.0 | — | 81.2 |

```
🙋 问题

柱状图中前测与后测分数的总体均分提升，与百分比表中报告的 TIC 原则概念的提升之间，
百分点差异是多少？

💡 答案
14.92%
```

### 🖱️ 数据分析 Agent 案例

```
🙋 问题

根据随机森林模型，哪个特征在预测 'time / retired' 方面具有最高的重要性？

💡 答案
laps
```

### 🖱️ NL2SQL Agent 案例

```
查找消费高于总体平均水平的客户，并显示他们消费最多的前 2 个音乐流派及每个流派的消费金额。
```

```sql
WITH CustomerTotal AS (
    SELECT c.CustomerId, SUM(il.UnitPrice * il.Quantity) AS TotalSpent
    FROM Customer c
    JOIN Invoice i ON c.CustomerId = i.CustomerId
    JOIN InvoiceLine il ON i.InvoiceId = il.InvoiceId
    GROUP BY c.CustomerId
),
AverageSpending AS (
    SELECT AVG(TotalSpent) AS AvgSpent FROM CustomerTotal
),
GenreSpending AS (
    SELECT c.CustomerId, g.Name AS GenreName, SUM(il.UnitPrice * il.Quantity) AS GenreSpent
    FROM Customer c
    JOIN Invoice i ON c.CustomerId = i.CustomerId
    JOIN InvoiceLine il ON i.InvoiceId = il.InvoiceId
    JOIN Track t ON il.TrackId = t.TrackId
    JOIN Genre g ON t.GenreId = g.GenreId
    GROUP BY c.CustomerId, g.GenreId
),
TopGenres AS (
    SELECT gs.CustomerId, gs.GenreName, gs.GenreSpent,
           ROW_NUMBER() OVER (PARTITION BY gs.CustomerId ORDER BY gs.GenreSpent DESC) as rn
    FROM GenreSpending gs
)
SELECT
    c.FirstName || ' ' || c.LastName AS CustomerName,
    tg.GenreName,
    tg.GenreSpent
FROM Customer c
JOIN CustomerTotal ct ON c.CustomerId = ct.CustomerId
JOIN AverageSpending avg ON ct.TotalSpent > avg.AvgSpent
JOIN TopGenres tg ON c.CustomerId = tg.CustomerId
WHERE tg.rn <= 2
ORDER BY ct.TotalSpent DESC, tg.GenreSpent DESC;
```

### 🖱️ GUI Agent 案例

<div align="center">
    <h3>GUI Agent 案例</h3>
    <video src="https://github.com/user-attachments/assets/526a870b-c18b-4af7-9134-5f84b5ebeb46" />
</div>

```
🙋 指令
我想审计这台 Ubuntu 机器上的所有命令别名，请从 GUI 启动终端，识别与 shell 启动相关的主目录配置文件，
然后生成一个整洁、排序的列表，结合当前活跃的别名和配置文件中隐藏的别名，
以便我可以看到 alert 或 ll 等命令的完整定义。
```

### 🖱️ 具身 Agent 案例

<table>
  <tr>
    <td align="center" width="40%" style="padding:6px;">
      <div><b>将鼠标放在黄色垫子上</b></div>
      <img src="assets/step1.gif" width="100%" style="border-radius:14px; margin-top:6px;" />
    </td>
    <td align="center" width="40%" style="padding:6px;">
      <div><b>打开笔记本电脑</b></div>
      <img src="assets/step2.gif" width="100%" style="border-radius:14px; margin-top:6px;" />
    </td>
  </tr>
  <tr>
    <td align="center" width="40%" style="padding:6px;">
      <div><b>将杯子放在蓝色盒子上</b></div>
      <img src="assets/step3.gif" width="100%" style="border-radius:14px; margin-top:6px;" />
    </td>
    <td align="center" width="40%" style="padding:6px;">
      <div><b>将小车放入篮子中</b></div>
      <img src="assets/step4.gif" width="100%" style="border-radius:14px; margin-top:6px;" />
    </td>
  </tr>
</table>


## 📦 安装

```bash
git clone https://github.com/OpenDCAI/AgentFlow
cd AgentFlow
pip install -e .
```

## 🧭 路线图

* [ ] 公开大规模合成数据集
* [ ] 扩展到更多领域
* [ ] 构建强大的 Agent 基础模型

## 📜 许可证

Apache 2.0

## ✍️ 贡献者

项目负责人：

核心贡献者：

贡献者：

顾问：

通讯作者与指导老师：

## 🌍 引用

如果您在研究中使用了 AgentFlow，请引用：

```bibtex
@misc{omniagentsynth2026,
  title={AgentFlow: Unified Agent Data Synthesis Framework},
  author={AgentFlow Team},
  year={2026},
  howpublished={\url{https://github.com/OpenDCAI/AgentFlow}}
}
```

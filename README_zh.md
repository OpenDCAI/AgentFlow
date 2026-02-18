<div align="center">
  <img src="assets/intro.png">

[![Datasets](https://img.shields.io/badge/Datasets-5EDDD2?style=for-the-badge&logo=huggingface&logoColor=yellow)](https://huggingface.co/collections/OpenDCAI/agentflow-models)
[![Models](https://img.shields.io/badge/Models-4285F4?style=for-the-badge&logo=huggingface&logoColor=yellow)](https://huggingface.co/collections/OpenDCAI/agentflow-models)
[![GITHUB](https://img.shields.io/badge/Github-24292F?style=for-the-badge&logo=github&logoColor=white)](https://github.com/OpenDCAI/AgentFlow)
[![Docmutation](https://img.shields.io/badge/Docmutation-red?style=for-the-badge&logo=google-chrome&logoColor=white)](https://opendcai.github.io/AgentFlow-Doc/en/)
 </div>

<p align="center">
  <a href="README.md">English</a> | <b>中文</b>
</p>

**首个统一的 Agent 数据合成框架**，为自定义任务提供 all-in-one 环境。

## 🚀 概览

**AgentFlow** 是**首个统一的 Agent 数据合成框架**，能够跨异构 Agent 环境生成高质量的训练与评估数据——涵盖 📚 RAG、🖼️ MM-Doc、🔍 Deep Research、🖱️ GUI、🟰 Text2SQL、📊 Data Analysis、🤖 Embodied Agent 等。

AgentFlow 提供了一个**统一、可扩展的 all-in-one 环境**，用于合成 agent trajectory、reasoning trace、tool interaction 和 environment feedback。

AgentFlow 还深入探索了 agent 数据合成与模型训练的内在机制，助力构建能够跨领域无缝运行的**工业级 Agentic Foundation Model**。

除了合成训练数据，AgentFlow 还提供高质量的人工标注与合成 benchmark，用于评估新兴 agent 能力并探索其边界。

> **One framework. All agent worlds.**

## ✨ 核心特性

### 统一的 Agent 数据合成范式

- 仅需几行代码即可合成复杂的 agent 训练数据。
- 提供**统一的抽象层**，实现跨异构 agent 环境的无缝数据合成。

### All-in-One Sandbox

- 内置支持 📚 RAG、🖼️ MM-Doc、🔍 Deep Research、💻 Code、🟰 SQL Database、🖱️ GUI、🤖 Embodied 等环境。
- 通过**模块化后端设计**，可轻松扩展至新环境。

### 探索 Agent 数据合成与训练的机制

- **Agentic Model Consolidation：** 在来自所有领域的混合 trajectory 上联合且稳定地训练统一模型。

### 创新性高价值 Agent Benchmark

- 提供一系列专为评估 agentic 能力而设计的高质量 benchmark。
- 旨在揭示现有 benchmark 未能覆盖的真实挑战，推动 agent 研究的实质性进展。

## ⚙️ 数据合成方法

<div align="center">
  <img src="assets/method.png">
</div>

AgentFlow 通过三阶段 pipeline 合成高质量的 agent 训练数据：**Trajectory Sampling → Trajectory Selection → QA Synthesis**。

1. **Trajectory Sampling.** 由 LLM 驱动的 agent 从 seed input 出发，在 sandbox 环境中迭代探索。每一步提出一次 tool call、执行并记录 observation，通过并发扩展和 action 去重构建分支 trajectory tree。

2. **Trajectory Selection.** 对所有 root-to-leaf 路径按深度、信息丰富度和工具多样性打分，然后通过策略筛选，确保高质量内容。

3. **QA Synthesis.** 对每条选中的路径，LLM 基于收集到的 observation 生成 multi-hop、factoid QA pair，并内置质量检查。

## 📦 安装

```bash
git clone https://github.com/OpenDCAI/AgentFlow
cd AgentFlow
pip install -e .
```

## 🛠️ 快速开始

以 WebAgent 数据合成为例。

**Step 1：** 使用 WebAgent sandbox 配置启动 sandbox。

```bash
./sandbox-server.sh --config configs/sandbox-server/web_config.json \
    --port 18890 \
    --host 0.0.0.0
```

**Step 2：** 使用 WebAgent synthesis 配置合成 QA。

```python
from synthesis import synthesize

synthesize(config_path="configs/synthesis/web_config.json")
```

**Step 3：** 使用 WebAgent trajectory 配置合成 trajectory。

```python
from rollout import pipeline

pipeline(config_path="configs/trajectory/web_trajectory.json")
```

**Step 4：** 模型训练完成后，使用 vLLM 部署模型。

```bash
vllm serve \
    --model YOUR_TRAINED_MODEL \
    --served-model-name webagent \
    --tensor-parallel-size 8 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --port 8222
```

**Step 5：** 使用 infer 配置对训练好的 Agent 模型进行推理。

```python
from rollout import pipeline

pipeline(config_path="configs/infer/web_infer.json")
```

## ⚙️ 配置说明

| 用途 | 配置路径 |
| ---- | ------- |
| 🖥️ 启动 Sandbox | [`configs/sandbox-server/`](https://github.com/OpenDCAI/AgentFlow/tree/main/configs/sandbox-server/) |
| 🧪 合成 QA | [`configs/synthesis/`](https://github.com/OpenDCAI/AgentFlow/tree/main/configs/synthesis/) |
| 🔄 Trajectory Rollout | [`configs/trajectory/`](https://github.com/OpenDCAI/AgentFlow/tree/main/configs/trajectory/) |
| 🚀 模型推理 | [`configs/infer/`](https://github.com/OpenDCAI/AgentFlow/tree/main/configs/infer/) |

## 🌟 AgentFlow Agent Family

### Papers

AgentFlow 拥有丰富的 agent 系列，更多信息请参阅以下论文：

[1] [DocDancer: Towards Agentic Document-Grounded Information Seeking](https://arxiv.org/pdf/2601.05163)

[2] [RAGShaper: Eliciting Sophisticated Agentic RAG Skills via Automated Data Synthesis](https://arxiv.org/pdf/2601.08699)

[3] [Exploring Information Seeking Agent Consolidation](https://www.arxiv.org/pdf/2602.00585)

[4] [BrowseComp-V3: A Visual, Vertical, and Verifiable Benchmark for Multimodal Browsing Agents](https://arxiv.org/pdf/2602.12876)

### Models

| Agent | 🤗 HuggingFace |
| ----- | -------------- |
| MM-Doc | [DocDancer](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-DocDancer) |
| RAG | [RAGShaper](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-RAGShaper) |
| DeepResearch | [DeepResearch Agent](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-Web) |
| General-datamix | [Agent-datamix](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-DataMix) |
| General-RegMeanpp | [Agent-RegMeanpp](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-RegMeanpp) |

### Datasets

| Agent | 🤗 HuggingFace |
| ----- | -------------- |
| MM-Doc | [DocDancer](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-DocDancer) |
| RAG | [RAGShaper](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-RAGShaper) |
| DeepResearch | [DeepResearch Agent](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-Web) |

### Benchmarks
#### BrowseComp-V3

A challenging benchmark of 300 hand-crafted multimodal questions for evaluating web browsing agents. It features deep multi-hop, cross-modal reasoning across diverse domains, with publicly searchable evidence and expert-validated subgoal-driven process evaluation. Even SOTA models like GPT-5.2 achieve only 36% accuracy. Includes **OmniSeeker**, a general multimodal browsing agent framework, along with full rollout and LLM-judge evaluation pipelines.

📄 [Project Page](https://halcyon-zhang.github.io/BrowseComp-V3/) · 🤗 [Dataset](https://huggingface.co/datasets/Halcyon-Zhang/BrowseComp-V3) · 💻 [GitHub](https://github.com/Halcyon-Zhang/BrowseComp-V3)


## 🧪 Overall Performance

### Qwen3-30B-A3B-Think

| Level | **Strategy** | **Web: GAIA (Acc.)** | **Web: BC (Acc.)** | **Web: BC-zh (Acc.)** | **Doc: MMBD (Acc.)** | **Doc: DocB (Acc.)** | **RAG: HotPotQA (EM/F1)** | **RAG: AmbigQA (F1/EM)** | **RAG: Bamboogle (F1/EM)** |
| ---- | ------- | -------------------- | ------------------ | --------------------- | -------------------- | -------------------- | ------------------------- | ------------------------ | -------------------------- |
| **Data-level** | Data Mixing | **64.08** | **28.00** | **34.00** | 63.59 | **83.29** | 38.00 / 42.53 | 49.50 / 58.84 | 53.10 / 60.20 |
| **Parameter-level** | RegMean++ | 60.19 | 22.50 | 28.00 | 64.66 | 80.76 | 45.50 / 58.27 | 58.80 / 69.36 | **52.80 / 66.48** |

### 🔗 RAG Agent Case and Performance

Agentic RAG is an approach where an autonomous agent actively decides how and when to retrieve information and reason over it to accomplish a task.

| Models | Bamboogle EM | Bamboogle F1 | PopQA EM | PopQA F1 | NQ EM | NQ F1 | AmbigQA EM | AmbigQA F1 | Avg EM | Avg F1 |
| ---- | ------------ | ------------ | -------- | -------- | ----- | ----- | ---------- | ---------- | ------ | ------ |
| **Prompt-Based Methods** | | | | | | | | | | |
| IR-COT | 16.0 | 27.9 | 32.4 | 39.9 | 19.3 | 35.5 | 24.5 | 40.6 | 23.1 | 36.0 |
| RECOMP | 21.7 | 28.6 | 40.5 | 45.8 | – | – | – | – | – | – |
| Search-o1 | 30.4 | 39.9 | 47.0 | 50.0 | 30.3 | 40.7 | 42.5 | 53.4 | 37.6 | 46.0 |
| **Learning-Based Methods** | | | | | | | | | | |
| Search-R1 | 30.4 | 43.2 | 41.3 | 46.4 | 36.0 | 45.0 | 49.2 | 60.4 | 39.2 | 48.8 |
| ReasonRAG | 22.4 | 29.1 | 41.1 | 44.4 | 28.1 | 38.9 | 39.7 | 51.9 | 32.8 | 41.1 |
| HL-Data 4.5k | 50.4 | 67.5 | 35.2 | 48.3 | 31.5 | 47.4 | 52.1 | 69.0 | 42.3 | 58.0 |
| **Ours** | | | | | | | | | | |
| **RAGShaper 4.5k** | 58.5 | 70.3 | 37.4 | 47.8 | 38.3 | 50.0 | **61.3** | **71.4** | 48.8 | 59.8 |
| **RAGShaper 6.5k** | **60.0** | **72.6** | 38.9 | 49.6 | **41.3** | **54.8** | 61.1 | 71.1 | **50.3** | **62.0** |

```python
🙋 Question

A major literary work commissioned by the Holy Roman Emperor whose reign began in 1508 was part of his grand artistic legacy. While this patron commissioned famous manuscript anthologies during this period, this specific allegorical epic was distinctively designed for the printing press to ensure a wider audience. **What is the exact publication year of its first edition?**

💡 Answer
1517
```

### 🔬 Document Agent Case and Performance

Document agent answers complex questions over multi-page documents by navigating, extracting, and reasoning across heterogeneous content—including text, tables, charts, and images.

### Benchmark Results Comparison

| Method | Model | MMLongBench-Doc acc | F1 | LasJ | DocBench LasJ |
| ---- | ---- | ------------------- | -- | ---- | ------------- |
| **OCR-based Baseline** | | | | | |
| Tesseract | GPT-4o | 30.1 | 30.5 | — | — |
| Tesseract | Gemini-2.0-Flash | 39.6 | 37.2 | — | — |
| **RAG-based Baseline** | | | | | |
| VisRAG | GPT-4o | 29.0 | 27.8 | — | — |
| RAGAnything | GPT-4o-mini | 42.8 | — | — | 63.4 |
| **Prompt-based Agent** | | | | | |
| Doc-React | GPT-4o | 38.1 | 38.3 | — | — |
| MDocAgent | GPT-4o | 42.0 | — | — | — |
| SimpleDoc | Claude-4-Sonnet | — | — | 58.6 | — |
| DocLens | Claude-4-Sonnet | — | — | 63.3 | — |
| **Ours** | | | | | |
| DocDancer | Qwen3-4B (ft) | 48.4 | 49.2 | 59.4 | 79.8 |
| DocDancer | Qwen3-30B-A3B (ft) | 54.4 | 53.9 | 65.3 | 81.2 |
| **Human Baseline** | — | 65.8 | 66.0 | — | 81.2 |

```python
🙋 Question

What is the difference in percentage-point increase between the overall mean score improvement shown in the bar chart of pre-test versus post-test scores and the improvement for the TIC Principle concept reported in the percentages table?

💡 Answer
14.92%
```

### 🖱️ Data Analysis Agent Case

```python
🙋 Question

Which feature has the highest importance in predicting 'time / retired' according to the Random Forest model?

💡 Answer
laps
```

### 🖱️ NL2SQL Agent Case

```python
Find customers whose spending is above the overall average, and show their top 2 most spent music genres along with the amount spent on each.
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

### 🖱️ GUI Agent Case

<div align="center">
    <h3>GUI Agent Case</h3>
    <video src="https://github.com/user-attachments/assets/526a870b-c18b-4af7-9134-5f84b5ebeb46" />
</div>

```python
🙋 Instruction
I want to audit all command aliases on this Ubuntu machine, so please launch the terminal from the GUI, identify any home directory config files related to shell startup, and then generate a clean, sorted list that combines both currently active aliases and those hidden in your configuration files so I can see the full definitions of commands like alert or ll.
```

### 🖱️ Embodied Agent Case

<table>
  <tr>
    <td align="center" width="40%" style="padding:6px;">
      <div><b>Place the mouse on the yellow pad</b></div>
      <img src="assets/step1.gif" width="100%" style="border-radius:14px; margin-top:6px;" />
    </td>
    <td align="center" width="40%" style="padding:6px;">
      <div><b>Open the laptop</b></div>
      <img src="assets/step2.gif" width="100%" style="border-radius:14px; margin-top:6px;" />
    </td>
  </tr>
  <tr>
    <td align="center" width="40%" style="padding:6px;">
      <div><b>Place the cup on the blue box</b></div>
      <img src="assets/step3.gif" width="100%" style="border-radius:14px; margin-top:6px;" />
    </td>
    <td align="center" width="40%" style="padding:6px;">
      <div><b>Store the car in the basket</b></div>
      <img src="assets/step4.gif" width="100%" style="border-radius:14px; margin-top:6px;" />
    </td>
  </tr>
</table>

## 📜 License

Apache 2.0

## ✍️ Contributors

| Role | Members |
| :---: | :--- |
| **🎯 Project Leader** | Zhengwei Tao (tttzw@pku.edu.cn), Jialong Wu (wujialongml@gmail.com) |
| **🌟 Core Contributor** | Bo Li, Guochen Yan, Qintong Zhang, Huanyao Zhang |
| **💡 Contributor** | Xinjie Lv, Haishan Lu, Yuan Xu, Haoyang Yao, Xingdi Ding |
| **📣 Advisor** | Kuan Li ([UniPat.ai](https://unipat.ai/)) |
| **🏫 Supervisor** | Wentao Zhang, Bin Cui |

## 🌍 Citation

如果您在研究中使用了 AgentFlow，请引用：

```bibtex
@misc{omniagentsynth2026,
  title={AgentFlow: Unified Agent Data Synthesis Framework},
  author={AgentFlow Team},
  year={2026},
  howpublished={\url{https://github.com/OpenDCAI/AgentFlow}}
}
```

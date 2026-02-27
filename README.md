<div align="center">
  <img src="assets/intro.png">

[![Datasets](https://img.shields.io/badge/Datasets-5EDDD2?style=for-the-badge&logo=huggingface&logoColor=yellow)](https://huggingface.co/collections/OpenDCAI/datasets-for-agentflow)
[![Models](https://img.shields.io/badge/Models-4285F4?style=for-the-badge&logo=huggingface&logoColor=yellow)](https://huggingface.co/collections/OpenDCAI/agentflow-models)
[![GITHUB](https://img.shields.io/badge/Github-24292F?style=for-the-badge&logo=github&logoColor=white)](https://github.com/OpenDCAI/AgentFlow)
[![Docmutation](https://img.shields.io/badge/Docmutation-red?style=for-the-badge&logo=google-chrome&logoColor=white)](https://opendcai.github.io/AgentFlow-Doc/en/)
 </div>

 <p align="center">
  <a href="./assets/wechatshow.png">WeChat (微信)</a>
</p>

<p align="center">
  <b>English</b> | <a href="README_zh.md">中文</a>
</p>

**The First Unified Agent Data Synthesis Framework** for Custom Task with all-in-one envrionment.

## 🚀 Overview

**AgentFlow** is the **first unified agent data synthesis framework** that generates high-quality training and evaluation data across heterogeneous agent environments — including 

+ 📚 RAG

+ 🖼️ MM-Doc

+ 🔍 Deep Research

+ 🖱️ GUI

+ 🟰 Text2SQL

+ 📊 Data Analysis

+ 🤖 Embodied Agents

+ and more.

It provides a **unified, extensible, all-in-one environment** for synthesizing agent trajectories, reasoning traces, tool interactions, and environment feedback.

AgentFlow also explores the underlying mechanisms of agent data synthesis and model training, enabling the development of **industrial-grade agentic foundation models** that operate seamlessly across domains.

Beyond synthetic training data, AgentFlow also offers high-quality human-annotated and synthetic benchmarks for evaluating emerging agent capabilities and exploring their boundaries.

> **One framework. All agent worlds.**

## ✨ Key Features

### Unified Agent Data Synthesis Paradigm

- Synthesize complex agent training data with just a few lines of code.
- Provide a **unified abstraction layer** for seamless data synthesis across heterogeneous agent environments.

### All-in-One Sandbox

- Built-in support for 📚 RAG, 🖼️ MM-Doc, 🔍 Deep Research, 💻 Code, 🟰 SQL database, 🖱️ GUI, 🤖 Embodied and more.
- Easily extensible to new environments via a **modular backend design**.

### Exploring Mechanisms of Agent Data Synthesis and Training

- **Agentic Model Consolidation:** Jointly and Stably train a unified model on mixed trajectories from all domains. 


### Innovative High-Value Agent Benchmarks

- Offer a suite of novel, high-quality benchmarks purpose-built for evaluating agentic capabilities.
- Designed to expose real-world challenges that existing benchmarks overlook, driving meaningful progress in agent research.


## ⚙️ Data Synthesis Method

<div align="center">
  <img src="assets/method.png">
</div>

AgentFlow synthesizes high-quality agent training data through a three-stage pipeline: **Trajectory Sampling → Trajectory Selection → QA Synthesis**.

1. **Trajectory Sampling.** An LLM-driven agent iteratively explores a sandbox environment starting from seed inputs. At each step it proposes a tool call, executes it, and records the observation, building a branching trajectory tree with concurrent expansion and action de-duplication.

2. **Trajectory Selection.** All root-to-leaf paths are scored by depth, information richness, and tool diversity, then selected with strategies, ensuring high-quality content.

3. **QA Synthesis.** For each selected path, the LLM generates a multi-hop, factoid QA pair grounded in the collected observations, with built-in quality checks.

## 📦 Installation

```bash
git clone https://github.com/your-org/AgentFlow
cd AgentFlow
pip install -e .
```

## 🛠️ QuickStart

We take WebAgent data synthesis as an example.

**Step 1:** Launch the sandbox with WebAgent sandbox config.

```bash
./sandbox-server.sh --config configs/sandbox-server/web_config.json \
    --port 18890 \
    --host 0.0.0.0
```

**Step 2:** Synthesize QA with WebAgent synthesis config.

```python
from synthesis import synthesize

synthesize(config_path="configs/synthesis/web_config.json")
```

**Step 3:** Synthesize trajectory with WebAgent trajectory config.

```python
from rollout import pipeline

pipeline(config_path="configs/trajectory/web_trajectory.json")
```

**Step 4:** After training the model, serve it with vLLM.

```bash
vllm serve \
    --model YOUR_TRAINED_MODEL \
    --served-model-name webagent \
    --tensor-parallel-size 8 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --port 8222
```

**Step 5:** Infer on trained Agentic model with infer config.

```python
from rollout import pipeline

pipeline(config_path="configs/infer/web_infer.json")
```

## ⚙️ Configuration

| Purpose | Config Path |
| ------- | ----------- |
| 🖥️ Launching Sandbox | [`configs/sandbox-server/`](https://github.com/OpenDCAI/AgentFlow/tree/main/configs/sandbox-server/) |
| 🧪 Synthesizing QA | [`configs/synthesis/`](https://github.com/OpenDCAI/AgentFlow/tree/main/configs/synthesis/) |
| 🔄 Trajectory Rollout | [`configs/trajectory/`](https://github.com/OpenDCAI/AgentFlow/tree/main/configs/trajectory/) |
| 🚀 Model Inference | [`configs/infer/`](https://github.com/OpenDCAI/AgentFlow/tree/main/configs/infer/) |


## 🌟 AgentFlow Agent Family
### Papers
AgentFlow also has an extensive agent family. You can find more information in the following paper:

[1] [DocDancer: Towards Agentic Document-Grounded Information Seeking](https://arxiv.org/pdf/2601.05163)

[2] [RAGShaper: Eliciting Sophisticated Agentic RAG Skills via Automated Data Synthesis](https://arxiv.org/pdf/2601.08699)

[3] [Exploring Information Seeking Agent Consolidation](https://www.arxiv.org/pdf/2602.00585)

[4] [BrowseComp-V3: A Visual, Vertical, and Verifiable Benchmark for Multimodal Browsing Agents](https://arxiv.org/pdf/2602.12876)
### Models

| Agent      | 🤗 HuggingFace | 
| ---------- | ----------- |
| MM-Doc  |     [DocDancer](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-DocDancer)     | 
| RAG |  [RAGShaper](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-RAGShaper)           | 
| DeepResearch   |  [DeepResearch Agent](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-Web)        | 
| General-datamix  | [Agent-datamix](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-DataMix)           |
| General-RegMeanpp  | [Agent-RegMeanpp](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-RegMeanpp)           |

### Datasets

| Agent      | 🤗 HuggingFace | 
| ---------- | ----------- |
| MM-Doc  |     [DocDancer](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-DocDancer)     | 
| RAG |  [RAGShaper](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-RAGShaper)           | 
| DeepResearch   |  [DeepResearch Agent](https://huggingface.co/OpenDCAI/AgentFlow-Qwen3-30B-A3B-Think-Web)    |


### Benchmarks
#### BrowseComp-V3

A challenging benchmark of 300 hand-crafted multimodal questions for evaluating web browsing agents. It features deep multi-hop, cross-modal reasoning across diverse domains, with publicly searchable evidence and expert-validated subgoal-driven process evaluation. Even SOTA models like GPT-5.2 achieve only 36% accuracy. Includes **OmniSeeker**, a general multimodal browsing agent framework, along with full rollout and LLM-judge evaluation pipelines.

📄 [Project Page](https://halcyon-zhang.github.io/BrowseComp-V3/) · 🤗 [Dataset](https://huggingface.co/datasets/Halcyon-Zhang/BrowseComp-V3) · 💻 [GitHub](https://github.com/Halcyon-Zhang/BrowseComp-V3)


## 🧪 Overall Performance
### Qwen3-30B-A3B-Think

| Level               | **Strategy** | **Web: GAIA (Acc.)** | **Web: BC (Acc.)** | **Web: BC-zh (Acc.)** | **Doc: MMBD (Acc.)** | **Doc: DocB (Acc.)** | **RAG: HotPotQA (EM/F1)** | **RAG: AmbigQA (EM/F1)** | **RAG: Bamboogle (EM/F1)** |
| ------------------- | ------------ | -------------------- | ------------------ | --------------------- | -------------------- | -------------------- | ------------------------- | ------------------------ | -------------------------- |
| **Data-level**      | Data Mixing  | **64.08**            | **28.00**          | **34.00**             | 63.59                | **83.29**            | 38.00 / 42.53             | 49.50 / 58.84            | 53.10 / 60.20              |
| **Parameter-Level**                | RegMean++    | 60.19                | 22.50              | 28.00                 | 64.66                | 80.76                | 45.50 / 58.27             | 58.80 / 69.36            | **52.80 / 66.48**          |

### 🔗 RAG Agent Case and Performance
Agentic RAG is an approach where an autonomous agent actively decides how and when to retrieve information and reason over it to accomplish a task.

| Models                     | Bamboogle EM | Bamboogle F1 | PopQA EM | PopQA F1 | NQ EM    | NQ F1    | AmbigQA EM | AmbigQA F1 | Avg EM   | Avg F1   |
| -------------------------- | ------------ | ------------ | -------- | -------- | -------- | -------- | ---------- | ---------- | -------- | -------- |
| **Prompt-Based Methods**   |              |              |          |          |          |          |            |            |          |          |
| IR-COT                     | 16.0         | 27.9         | 32.4     | 39.9     | 19.3     | 35.5     | 24.5       | 40.6       | 23.1     | 36.0     |
| RECOMP                     | 21.7         | 28.6         | 40.5     | 45.8     | –        | –        | –          | –          | –        | –        |
| Search-o1                  | 30.4         | 39.9         | 47.0     | 50.0     | 30.3     | 40.7     | 42.5       | 53.4       | 37.6     | 46.0     |
| **Learning-Based Methods** |              |              |          |          |          |          |            |            |          |          |
| Search-R1                  | 30.4         | 43.2         | 41.3     | 46.4     | 36.0     | 45.0     | 49.2       | 60.4       | 39.2     | 48.8     |
| ReasonRAG                  | 22.4         | 29.1         | 41.1     | 44.4     | 28.1     | 38.9     | 39.7       | 51.9       | 32.8     | 41.1     |
| HL-Data 4.5k               | 50.4         | 67.5         | 35.2     | 48.3     | 31.5     | 47.4     | 52.1       | 69.0       | 42.3     | 58.0     |
| **Ours**                   |              |              |          |          |          |          |            |            |          |          |
| **RAGShaper 4.5k**         | 58.5         | 70.3         | 37.4     | 47.8     | 38.3     | 50.0     | **61.3**   | **71.4**   | 48.8     | 59.8     |
| **RAGShaper 6.5k**         | **60.0**     | **72.6**     | 38.9     | 49.6     | **41.3** | **54.8** | 61.1       | 71.1       | **50.3** | **62.0** |

```python
🙋 Question

A major literary work commissioned by the Holy Roman Emperor whose reign began in 1508 was part of his grand artistic legacy. While this patron commissioned famous manuscript anthologies during this period, this specific allegorical epic was distinctively designed for the printing press to ensure a wider audience. **What is the exact publication year of its first edition?**

💡 Answer
1517
```


### 🔬 Document Agent Case and Performance
Document agent answers complex questions over multi-page documents by navigating, extracting, and reasoning across heterogeneous content—including text, tables, charts, and images.

### Benchmark Results Comparison

| Method                                 | Model              | MMLongBench-Doc acc | F1       | LasJ     | DocBench LasJ |
| -------------------------------------- | ------------------ | ------------------- | -------- | -------- | ------------- |
| **VLM
| **OCR-based Baseline**                 |                    |                     |          |          |               |
| Tesseract       | GPT-4o             | 30.1                | 30.5     | —        | —             |
| Tesseract       | Gemini-2.0-Flash   | 39.6                | 37.2     | —        | —             |
| **RAG-based Baseline**                 |                    |                     |          |          |               |
| VisRAG           | GPT-4o             | 29.0                | 27.8     | —        | —             |
| RAGAnything    | GPT-4o-mini        | 42.8                | —        | —        | 63.4          |
| **Prompt-based Agent**                 |                    |                     |          |          |               |
| Doc-React        | GPT-4o             | 38.1                | 38.3     | —        | —             |
| MDocAgent        | GPT-4o             | 42.0                | —        | —        | —             |
| SimpleDoc       | Claude-4-Sonnet    | —                   | —        | 58.6     | —             |
| DocLens          | Claude-4-Sonnet    | —                   | —        | 63.3     | —             |
| **Ours**                               |                    |                     |          |          |               |
| DocDancer                              | Qwen3-4B (ft)      | 48.4                | 49.2     | 59.4     | 79.8          |
| DocDancer                              | Qwen3-30B-A3B (ft) | 54.4                | 53.9     | 65.3     | 81.2          |
| **Human Baseline**                     | —                  | 65.8                | 66.0     | —        | 81.2          |

```python
🙋 Question

What is the difference in percentage-point increase between the overall mean score improvement shown in the bar chart of pre-test versus post-test scores and the improvement for the TIC Principle concept reported in the percentages table?

💡 Answer

14.92%
```

### 🖱️ Data Analysis Agent Case

Example input table (CSV preview, e.g. `race_results.csv`):

| **Rank** | **Driver**         | **Team**           | **Laps** | **Time / Retire** | **Grid** | **Points** |
|---------:|--------------------|--------------------|---------:|-------------------|---------:|-----------:|
| 1        | sébastien bourdais | n / h / 1 racing   | 96       | 45:42.0           | 2        | 33         |
| 2        | justin wilson      | rsports            | 96       | + 3.9 secs        | 3        | 27         |
| 3        | graham rahal       | n / h / 1 racing   | 96       | + 6.6 secs        | 4        | 25         |
| 4        | simon pagenaud     | team australia     | 96       | + 24.8 secs       | 7        | 23         |
| 5        | paul tracy         | forsythe racing    | 96       | + 28.1 secs       | 14       | 22         |
| ...      | ...                | ...                | ...      | ...               | ...      | ...        |

```python
🙋 Question

Which feature has the highest importance in predicting 'time / retired' according to the Random Forest model?

💡 Answer
laps
```

### 🖱️ NL2SQL Agent Case

#### Table Structure

*actor* Table (200 rows)

| actor_id | first_name | last_name | last_update |
|----------|------------|-----------|-------------|
| 1 | PENELOPE | GUINESS | 2026-02-05 16:18:42 |
| 2 | NICK | WAHLBERG | 2026-02-05 16:18:42 |
| 3 | ED | CHASE | 2026-02-05 16:18:42 |

*film_actor* Table (5,462 rows)

| actor_id | film_id | last_update |
|----------|---------|-------------|
| 1 | 1 | 2026-02-05 16:18:45 |
| 1 | 23 | 2026-02-05 16:18:45 |
| 1 | 25 | 2026-02-05 16:18:45 |

*film* Table (1,000 rows)

| film_id | title | description | release_year | rental_rate | length | rating |
|---------|-------|-------------|--------------|-------------|--------|--------|
| 1 | ACADEMY DINOSAUR | A Epic Drama of a Feminist... | 2006 | 0.99 | 86 | PG |
| 2 | ACE GOLDFINGER | A Astounding Epistle of a... | 2006 | 4.99 | 48 | G |
| 3 | ADAPTATION HOLES | A Astounding Reflection of... | 2006 | 2.99 | 50 | NC-17 |

*film_category* Table (1,000 rows)

| film_id | category_id | last_update |
|---------|-------------|-------------|
| 1 | 6 | 2026-02-05 16:18:48 |
| 2 | 11 | 2026-02-05 16:18:48 |
| 3 | 6 | 2026-02-05 16:18:48 |

*category* Table (16 rows)

| category_id | name | last_update |
|-------------|------|-------------|
| 1 | Action | 2026-02-05 16:18:42 |
| 2 | Animation | 2026-02-05 16:18:42 |
| 3 | Children | 2026-02-05 16:18:42 |

*inventory* Table (4,581 rows)

| inventory_id | film_id | store_id | last_update |
|--------------|---------|----------|-------------|
| 1 | 1 | 1 | 2026-02-05 16:18:42 |
| 2 | 1 | 1 | 2026-02-05 16:18:42 |
| 3 | 1 | 1 | 2026-02-05 16:18:42 |

*rental* Table (16,044 rows)

| rental_id | rental_date | inventory_id | customer_id | return_date | staff_id |
|-----------|-------------|--------------|-------------|-------------|----------|
| 1 | 2005-05-24 22:53:30 | 367 | 130 | 2005-05-26 22:04:30 | 1 |
| 2 | 2005-05-24 22:54:33 | 1525 | 459 | 2005-05-28 19:40:33 | 1 |
| 3 | 2005-05-24 23:03:39 | 1711 | 408 | 2005-06-01 22:12:39 | 1 |


#### Synthesized Question

```
Which film categories have more than 10 actors who have appeared in popular films, 
and how many such actors are there in each category?
```


#### Answer SQL

```sql
WITH film_popularity AS (
    SELECT f.film_id, COUNT(r.rental_id) AS rental_count 
    FROM film f 
    JOIN inventory i ON f.film_id = i.film_id 
    JOIN rental r ON i.inventory_id = r.inventory_id 
    GROUP BY f.film_id
), 
top_popular_films AS (
    SELECT film_id 
    FROM film_popularity 
    WHERE rental_count > (SELECT AVG(rental_count) FROM film_popularity)
), 
actor_film_count AS (
    SELECT a.actor_id, COUNT(f.film_id) AS film_count 
    FROM actor a 
    JOIN film_actor fa ON a.actor_id = fa.actor_id 
    JOIN film f ON fa.film_id = f.film_id 
    GROUP BY a.actor_id
), 
top_actors AS (
    SELECT actor_id 
    FROM actor_film_count 
    WHERE film_count > (SELECT AVG(film_count) FROM actor_film_count)
), 
actor_category_data AS (
    SELECT fa.actor_id, c.name AS category_name 
    FROM film_actor fa 
    JOIN film_category fc ON fa.film_id = fc.film_id 
    JOIN category c ON fc.category_id = c.category_id
) 
SELECT c.name AS category_name, COUNT(a.actor_id) AS actor_count 
FROM top_actors ta 
JOIN actor_category_data acd ON ta.actor_id = acd.actor_id 
JOIN category c ON acd.category_name = c.name 
GROUP BY c.name 
HAVING COUNT(a.actor_id) > 10 
ORDER BY actor_count DESC;
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

## 🤝 Community & Support
💬 Join the AgentFlow open-source community to ask questions, share ideas, and collaborate with other developers!

<br>

<div align="center">
<a name="wechat-group"></a>
<img src="./assets/wechat.jpg" alt="AgentFlow WeChat Community" width="200"/>
<br>
<sub>👆 Scan to join the community WeChat group 🎉</sub>
</div>


## 🌍 Citation

If you use AgentFlow in your research, please cite:

```bibtex
@misc{omniagentsynth2026,
  title={AgentFlow: Unified Agent Data Synthesis Framework},
  author={AgentFlow Team},
  year={2026},
  howpublished={\url{https://github.com/OpenDCAI/AgentFlow}}
}
```

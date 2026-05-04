# 🗄️ Text2SQL: Agentic SQL Query Synthesis

This guide walks through the full pipeline of using the AgentFlow framework with **Text2SQL**, from data synthesis to model inference.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Pipeline Overview](#pipeline-overview)
- [Step 1: Prepare Databases](#step-1-prepare-databases)
- [Step 2: Start the Sandbox Server](#step-2-start-the-sandbox-server)
- [Step 3: Synthesize QA Data](#step-3-synthesize-qa-data)
- [Step 4: Model Training & Deployment](#step-4-model-training--deployment)
- [Step 5: Inference & Evaluation](#step-5-inference--evaluation)
- [Configuration Reference](#configuration-reference)
- [FAQ](#faq)

---

## Overview

Text2SQL is a **SQL Query Generation agent** that translates natural language questions into executable SQL queries. The pipeline has five stages:

```
Database Setup → Sandbox Setup → QA Synthesis → Model Training → Inference & Evaluation
```

AgentFlow provides three core tools for Text2SQL:

| Tool | Description | Parameters |
|------|-------------|------------|
| `sql:list_databases` | List all available databases that can be queried | None |
| `sql:get_schema` | Get table structures (tables, columns, foreign keys) of a database | `db_id`: database ID (required), `table_names`: optional filter |
| `sql:execute` | Execute a SQL query on a specific database (SELECT/WITH/PRAGMA only) | `db_id`: database ID (required), `query`: SQL string (required) |

---

## Prerequisites

1. **Install AgentFlow**

```bash
git clone https://github.com/OpenDCAI/AgentFlow
cd AgentFlow
bash install.sh
```

> **Options:** `bash install.sh --ml` to include ML/DL dependencies (torch, transformers), `--all` for everything. See `bash install.sh --help` for details.

2. **Prepare API Keys**

The Text2SQL pipeline requires:
- **OpenAI-compatible API Key**: For LLM calls (supports OpenRouter and other compatible endpoints)

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_BASE="https://openrouter.ai/api/v1"  # or your preferred endpoint
```

3. **Prepare SQLite Databases**

Download or create SQLite database files (`.sqlite` or `.db`). Example databases:
- **Chinook**: Music store database
- **Sakila**: DVD rental database  
- **AdventureWorks**: Sales and inventory database

---

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     AgentFlow Text2SQL Pipeline                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Step 1: Database Preparation                                       │
│  ┌─────────────────┐                                                │
│  │  *.sqlite files │──▶ Place in sample_databases/sqlite/           │
│  └─────────────────┘                                                │
│          │                                                          │
│          ▼                                                          │
│  Step 2: Sandbox Server                                             │
│  ┌─────────────────────┐                                            │
│  │ text2sql_config.json│──▶ Start sql:* tool service                │
│  └─────────────────────┘                                            │
│          │                                                          │
│          ▼                                                          │
│  Step 3: QA Synthesis                                               │
│  ┌─────────────────────┐    ┌──────────┐    ┌───────────────────┐   │
│  │ text2sql_config.json│──▶ │  Seeds   │──▶ │  synthesized_qa   │   │
│  └─────────────────────┘    └──────────┘    │  + trajectories   │   │
│                                              └───────────────────┘   │
│          │                                                          │
│          ▼                                                          │
│  Step 4: Model Training & Serving (vLLM)                            │
│                                                                     │
│          │                                                          │
│          ▼                                                          │
│  Step 5: Inference & Evaluation                                     │
│  ┌──────────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │  text2sql_infer  │──▶ │  benchmark   │──▶ │  infer_results   │   │
│  └──────────────────┘    └──────────────┘    │  + evaluation    │   │
│                                              └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Prepare Databases

### Database Configuration

Place your SQLite database files in a directory (e.g., `sample_databases/sqlite/`):

```
sample_databases/
└── sqlite/
    ├── chinook.sqlite
    ├── sakila.sqlite
    └── adventureworks.sqlite
```

### Sandbox Server Configuration

Configure the sandbox server to load your databases in `configs/sandbox-server/text2sql_config.json`:

```json
{
  "server": {
    "title": "Sandbox HTTP Service (Text2SQL)",
    "description": "SQL backend for text2sql synthesis",
    "session_ttl": 300
  },
  "resources": {
    "sql": {
      "enabled": true,
      "backend_class": "sandbox.server.backends.resources.database.DatabaseBackend",
      "description": "SQLite read-only backend for text2sql",
      "config": {
        "databases": {
          "chinook": "/path/to/sample_databases/sqlite/chinook.sqlite",
          "sakila": "/path/to/sample_databases/sqlite/sakila.sqlite",
          "adventureworks": "/path/to/sample_databases/sqlite/adventureworks.sqlite"
        }
      }
    }
  },
  "apis": {}
}
```

**Key config fields:**

| Field | Description |
|-------|-------------|
| `databases` | Map of database ID → absolute path to SQLite file |
| Database IDs | Used in `sql:get_schema` and `sql:execute` calls |

---

## Step 2: Start the Sandbox Server

The Sandbox server provides the SQL tool execution environment for the agent.

**Command:**

```bash
python3 -m sandbox.cli.sandbox-server --config configs/sandbox-server/text2sql_config.json
```

**Expected output:**

```
================================================================================
🚀 Sandbox Server starting...
================================================================================
📁 Project root: /path/to/AgentFlow
⚙️  Config file: configs/sandbox-server/text2sql_config.json
🌐 Server address: http://127.0.0.1:18890
================================================================================

INFO:ResourceRouter:Registered resource type: sql
INFO:HTTPServiceServer:Registered tool: sql:execute
INFO:HTTPServiceServer:Registered tool: sql:get_schema
INFO:HTTPServiceServer:Registered tool: sql:list_databases
================================================================================
✅ Server Ready！
🌐 Visit URL: http://127.0.0.1:18890
🔍 Health Check: http://127.0.0.1:18890/health
================================================================================
```

**Verification:**

```bash
curl http://127.0.0.1:18890/health
# Expected: {"status": "healthy"}
```

---

## Step 3: Synthesize QA Data

### Prepare Seed Data

Seed data defines the exploration starting points. Each seed specifies a target database and exploration intent.

**Seed file format** (`seeds/text2sql/seeds.jsonl`):

```jsonl
{"content": "Database: chinook", "kwargs": {"focus_tables": ["Customer", "Invoice", "InvoiceLine", "Track", "Album", "Artist", "Genre"], "exploration_mode": "hard_customer_revenue_and_genre_mix"}}
{"content": "Database: sakila", "kwargs": {"focus_tables": ["film", "film_actor", "actor", "film_category", "category", "inventory", "rental", "payment"], "exploration_mode": "hard_category_revenue_and_actor_depth"}}
{"content": "Database: adventureworks", "kwargs": {"focus_tables": ["SalesOrderHeader", "SalesOrderDetail", "Product", "ProductSubcategory", "ProductCategory"], "exploration_mode": "hard_category_revenue_and_region_mix"}}
```

| Field | Required | Description |
|-------|----------|-------------|
| `content` | ✅ Yes | Database identifier (e.g., `"Database: chinook"`) |
| `kwargs.focus_tables` | Optional | List of tables to focus exploration |
| `kwargs.exploration_mode` | Optional | Exploration strategy hint |

---

### Synthesis Configuration

Configure the synthesis pipeline in `configs/synthesis/text2sql_config.json`:

```json
{
  "model_name": "openai/gpt-4o",
  "api_key": "${OPENAI_API_KEY}",
  "base_url": "${OPENAI_API_BASE}",

  "max_depth": 4,
  "branching_factor": 1,
  "depth_threshold": 2,

  "min_depth": 2,
  "max_selected_traj": 1,
  "path_similarity_threshold": 0.8,

  "target_qa_count": 100,

  "resource_types": ["sql"],
  "sandbox_server_url": "http://127.0.0.1:18890",
  "sandbox_auto_start": true,
  "sandbox_config_path": "/path/to/AgentFlow/configs/sandbox-server/text2sql_config.json",

  "available_tools": ["sql:list_databases", "sql:get_schema", "sql:execute"],

  "sampling_tips": [
    "First use sql:list_databases to confirm database IDs.",
    "Then use sql:get_schema to view tables, fields, and foreign key relationships.",
    "Finally, use sql:execute to repeatedly verify SQL, ensuring it is executable and returns non-empty results.",
    "Prioritize generating complex questions with multi-table joins, group statistics, threshold filtering, subqueries, or CTEs.",
    "",
    "## Difficulty Requirements",
    "- All problems should be hard difficulty: nested subqueries, window functions, complex JOINs (3+ tables), or multiple aggregations.",
    "- Avoid generating only Top-1/max-value questions; prioritize group statistics, comparison, threshold filtering, Top-N, range analysis."
  ],

  "synthesis_tips": [
    "Generate all hard difficulty Text2SQL.",
    "JSON output must include question/sql/reasoning_steps/difficulty.",
    "question must be expressed in business semantics, without directly showing table/column names.",
    "sql must be executable and return non-empty results.",
    "If results are empty, first relax filter conditions then gradually tighten."
  ],

  "seeds_file": "/path/to/AgentFlow/seeds/text2sql/seeds.jsonl",
  "output_dir": "results/text2sql"
}
```

**Key config parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `model_name` | - | LLM model for synthesis (OpenAI-compatible format) |
| `max_depth` | `4` | Max exploration depth of the trajectory tree |
| `branching_factor` | `1` | Number of branches per node |
| `min_depth` | `2` | Min depth for a trajectory to be selected |
| `target_qa_count` | - | Target number of QA pairs to generate |
| `sampling_tips` | - | Hints guiding the agent's database exploration |
| `synthesis_tips` | - | Hints guiding QA generation |
| `description_path` | `None` | (Optional) Instruction markdown path — alternative to inline tips |
| `seeds_file` | - | Path to seed data file (JSONL) |
| `sandbox_server_url` | `http://127.0.0.1:18890` | Sandbox server address |

> **Tip — Instruction Markdown with LLM Fallback:** Instead of specifying `sampling_tips` / `selecting_tips` / `synthesis_tips` inline in the JSON config, you can point `description_path` to a markdown file containing all guidance in free-form natural language. The pipeline uses a two-stage parser (regex + LLM fallback) to automatically extract structured fields. This is especially useful when guidance is long or written in prose.

### If You Enable Skills

If you want to enable skill selection and injection for QA synthesis, add the skill-related fields to `configs/synthesis/text2sql_config.json`:

```json
{
  "description_path": "configs/synthesis/instructions/text2sql_instruction.md",
  "skills_root": "synthesis/skills",
  "skill_group": "sql",
  "skill": {
    "enabled": true,
    "min_global_skills": 5,
    "max_global_skills": 10
  }
}
```

When `skill.enabled=true`, markdown structured extraction is recommended but not mandatory. If extraction is incomplete, pipeline still runs and falls back to full markdown text for global skill selection, then injects selected skills into phase prompts.

---

### Run QA Synthesis

**Method 1: Python API**

```python
from synthesis import synthesize

synthesize(config_path="configs/synthesis/text2sql_config.json")
```

**Method 2: CLI**

```bash
python3 run_text2sql.py
```

**Core flow:**

```
Seed → Trajectory Tree Sampling (TrajectorySampler)
     → Trajectory Selection (TrajectorySelector)
     → QA Synthesis (QASynthesizer)
     → Output QA pairs + trajectories
```

**Output files:**

| File | Description |
|------|-------------|
| `results/text2sql/synthesized_qa.jsonl` | Synthesized QA pairs (one JSON per line) |
| `results/text2sql/trajectories.jsonl` | Corresponding agent exploration trajectories |

**Sample output:**

```jsonl
{"question": "Which film categories have more than 10 actors who have appeared in popular films?", "sql": "WITH film_popularity AS (...) SELECT ...", "reasoning_steps": [...], "difficulty": "hard"}
```

---

## Step 4: Model Training & Deployment

After training a model with data from Step 3, deploy it using vLLM.

**Deploy with vLLM:**

```bash
vllm serve \
    --model YOUR_TRAINED_MODEL \
    --served-model-name text2sql-agent \
    --tensor-parallel-size 8 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes \
    --port 8222
```

**Parameters:**

| Parameter | Description |
|-----------|-------------|
| `--model` | Path to trained model or HuggingFace model name |
| `--served-model-name` | Model name exposed by the service |
| `--tensor-parallel-size` | Tensor parallelism size (based on GPU count) |
| `--enable-auto-tool-choice` | Enable automatic tool selection (required for agents) |
| `--tool-call-parser` | Tool call parser format (`hermes` recommended) |

Once deployed, the model serves an OpenAI-compatible API at `http://localhost:8222`.

---

## Step 5: Inference & Evaluation

Run inference on benchmark data with the trained model.

**Usage:**

```python
from rollout import pipeline

pipeline(config_path="configs/infer/text2sql_infer.json")
```

**Config file** `configs/infer/text2sql_infer.json`:

```json
{
  "benchmark_name": "text2sql_infer",
  "model_name": "text2sql-agent",
  "api_key": "<YOUR_API_KEY>",
  "base_url": "http://localhost:8222/v1",

  "max_turns": 20,
  "max_retries": 3,

  "available_tools": ["sql:list_databases", "sql:get_schema", "sql:execute"],

  "system_prompt": [
    "You are an expert SQL assistant.",
    "Translate natural language questions into executable SQL queries.",
    "Always verify your SQL is executable before responding."
  ],

  "evaluate_results": true,
  "evaluation_metric": "execution_accuracy",
  "data_path": "benchmark/text2sql_benchmark.jsonl",
  "output_dir": "infer_results/text2sql"
}
```

**Output:**

| File | Description |
|------|-------------|
| `results_text2sql_infer_{timestamp}.jsonl` | Inference results for each task |
| `evaluation_text2sql_infer_{timestamp}.json` | Evaluation metrics |

---

## Configuration Reference

### Synthesis Config

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | `str` | - | LLM model name |
| `api_key` | `str` | `""` | API key (supports env vars like `${OPENAI_API_KEY}`) |
| `base_url` | `str` | `""` | API base URL |
| `available_tools` | `list[str]` | `[]` | Available tools for the agent |
| `seeds_file` | `str` | - | Seed file path (JSONL) |
| `output_dir` | `str` | - | Output directory |
| `max_depth` | `int` | `4` | Max trajectory tree depth |
| `branching_factor` | `int` | `1` | Branching factor per node |
| `min_depth` | `int` | `2` | Min trajectory depth for selection |
| `target_qa_count` | `int` | - | Target number of QA pairs |
| `sandbox_server_url` | `str` | `http://127.0.0.1:18890` | Sandbox server address |
| `sandbox_auto_start` | `bool` | `true` | Auto-start sandbox if not running |

### Skill Config for Synthesis

Use these fields in synthesis config (for example `configs/synthesis/text2sql_config.json`):

```json
{
  "description_path": "configs/synthesis/instructions/text2sql_instruction.md",
  "skills_root": "synthesis/skills",
  "skill_group": "sql",
  "skill": {
    "enabled": true,
    "max_category_count": 1,
    "min_global_skills": 5,
    "max_global_skills": 10,
    "max_desc_chars": 800,
    "max_ref_chars": 3000,
    "temperature": 0.2,
    "max_skill_examples": 8,
    "max_total_qa_examples": 24
  }
}
```

### Instruction Markdown Format Requirements

Instruction markdown (for example `configs/synthesis/instructions/text2sql_instruction.md`) supports these blocks:
- `description`
- `sampling_tips`
- `selecting_tips`
- `synthesis_tips`
- `qa_examples`

#### Two-stage Parsing with LLM Fallback

The instruction markdown is parsed in two stages:

1. **Regex-based parsing** (zero-cost, deterministic): Extracts structured blocks using `key: value` line format. Works best when the markdown follows the strict key-block format above.
2. **LLM fallback** (triggered automatically): When regex parsing is incomplete (missing required blocks) and model credentials (`api_key` + `base_url`) are configured, the pipeline automatically calls the LLM to extract structured fields from free-form / colloquial markdown.

This means you can write instruction markdown in **natural language prose** (headings, paragraphs, bullet points) without strict `key: value` formatting — the LLM fallback will intelligently extract the required fields.

> **Note:** The LLM fallback uses a single API call with a structured-data extraction prompt. If the provider does not support `response_format={"type": "json_object"}`, the pipeline automatically retries without that constraint.

#### Behavior by Skill Mode

- `skill.enabled=false`: strict mode. All blocks above are required after parsing (regex + LLM fallback combined); if still incomplete, synthesis terminates with an error.
- `skill.enabled=true`: tolerant mode. Structured extraction is recommended but not mandatory. If extraction is incomplete even after LLM fallback, pipeline falls back to full markdown text for global skill selection, continues synthesis, and uses skill guidance as phase injection.

Meaning of key fields:

| Field | Default | Description |
|------|---------|-------------|
| `description_path` | `null` | Instruction markdown path. Recommended blocks: `description`, `sampling_tips`, `selecting_tips`, `synthesis_tips`, `qa_examples`. |
| `skills_root` | `synthesis/skills` | Skill library root path. Relative path is resolved from project root. |
| `skill_group` | inferred from `resource_types` | Optional fixed category. For Text2SQL, set `"sql"` for strict category scoping. |
| `skill.enabled` | `false` | Whether to enable global skill selection and prompt injection. |
| `skill.max_category_count` | `2` | Max skill categories selected in stage-1 category selection. |
| `skill.min_global_skills` | `5` | Minimum skills selected in one global selection run. |
| `skill.max_global_skills` | `10` | Maximum skills selected in one global selection run. |
| `skill.max_desc_chars` | `800` | Max description length per skill when shown to selector LLM. |
| `skill.max_ref_chars` | `3000` | Max injected reference length per phase per skill. |
| `skill.temperature` | `0.2` | Temperature for skill-selection LLM calls. |
| `skill.max_skill_examples` | `8` | Max QA examples collected from selected `SKILL.md` files. |
| `skill.max_total_qa_examples` | `24` | Max merged QA examples finally passed to synthesizer prompt. |
| `skill.include` | `[]` | Optional explicit skill IDs to force include (bypass LLM selection). |
| `skill.exclude` | `[]` | Optional skill IDs to block from candidate pool. |

`selection_mode` in `skills_used.json`:

| Value | Meaning |
|------|---------|
| `disabled` | Skill is turned off; original tips/examples path is used. |
| `explicit_include` | Skills are taken from `skill.include` after validation. |
| `llm_global` | One-time LLM global selection (category -> skills) is applied. |

### Skill Library Structure

Default root:

`AgentFlow/synthesis/skills`

Expected layout:

```text
synthesis/skills/
  sql/                                   # 一级类别（Agent 类型）
    <skill-id>/
      SKILL.md                           # skill 定义（name/description + capability）
      references/
        EXPLORATION.md                   # sampler 阶段注入
        SELECTION.md                     # selector 阶段注入
        SYNTHESIS.md                     # synthesizer 阶段注入
```

### How to Upload Your Own SQL Skills

1. Create a new folder under `synthesis/skills/sql/<your-skill-id>/`.
2. Add `SKILL.md` with frontmatter fields `name` and `description`.
3. In `SKILL.md`, optionally provide reusable QA demos as paired lines:
   - `**Real Question**: ...`
   - `**Real Answer**: ...`
4. Add `references/EXPLORATION.md`, `references/SELECTION.md`, `references/SYNTHESIS.md`.

### Sandbox Server Config

| Parameter | Type | Description |
|-----------|------|-------------|
| `server.title` | `str` | Server title |
| `server.session_ttl` | `int` | Session TTL in seconds |
| `resources.sql.enabled` | `bool` | Enable SQL backend |
| `resources.sql.config.databases` | `dict` | Map of database ID → file path |

---

## FAQ

### Q: How do I add a new database?

**A:** Add the database file path to `configs/sandbox-server/text2sql_config.json`:

```json
"databases": {
  "my_db": "/path/to/my_database.sqlite"
}
```

Then restart the sandbox server.

### Q: How do I generate harder SQL queries?

**A:** Modify `sampling_tips` in the synthesis config to emphasize:
- Multi-table JOINs (3+ tables)
- Nested subqueries and CTEs
- Window functions
- Complex aggregations with HAVING

### Q: Why are my generated SQL queries returning empty results?

**A:** The synthesis pipeline includes validation:
1. SQL must be executable
2. Results must be non-empty
3. If empty, the agent retries with relaxed conditions

Check your database has sufficient data for the query patterns.

### Q: How do I use a different LLM provider?

**A:** Set the environment variables:

```bash
export OPENAI_API_KEY="your-key"
export OPENAI_API_BASE="https://your-provider.com/v1"
```

Or configure directly in `text2sql_config.json`:

```json
{
  "model_name": "your-model-name",
  "api_key": "your-key",
  "base_url": "https://your-provider.com/v1"
}
```

---

## Example: Complex SQL Generation

Here's an example of a complex SQL query generated by the pipeline:

**Question:**
> Which film categories have more than 10 actors who have appeared in popular films, and how many such actors are there in each category?

**Generated SQL:**

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

**Features:**
- 5 CTEs (Common Table Expressions)
- 8 JOINs across 7 tables
- Multiple aggregation levels
- Subqueries for dynamic thresholds

---

## License

MIT License - See [LICENSE](../LICENSE) for details.

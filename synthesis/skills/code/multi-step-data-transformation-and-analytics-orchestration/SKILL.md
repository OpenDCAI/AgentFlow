---
name: multi-step-data-transformation-and-analytics-orchestration
description: Use this skill when the user wants code-agent data for realistic end-to-end data engineering, analytics, or ELT (Extract, Load, Transform) tasks spanning infrastructure configurations, multiple tools, and intermediate files. Trigger it for requests like 'create a full ELT workflow from Postgres to Snowflake', 'generate DBT-style models', 'make multi-step analytics tasks', 'set up Airbyte and Terraform pipelines', or 'chain SQL and Python across a complex project'. Do not use for single-query SQL authoring.
---

# Skill: multi-step-data-transformation-and-analytics-orchestration

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to architect and complete enterprise data-workflow and ELT tasks by configuring infrastructure-as-code (e.g., Airbyte via Terraform), orchestrating data movements across heterogeneous sources, and authoring complex transformation logic using modeling tools (e.g., DBT). This involves navigating project codebases, resolving connection-layer discrepancies, sequencing multi-step dependencies, tracking synchronous/asynchronous states, and verifying final artifact correctness.
* **Dimension Hierarchy**: Data and ML Workflow Engineering->Enterprise Data Workflow Coding->multi-step-data-transformation-and-analytics-orchestration

### Real Case
**[Case 1]**
* **Initial Environment**: A project workspace containing DBT-style project files, warehouse interfaces, schema docs, and existing macros. The business requires a daily dashboard combining raw transaction tables, lead events, and status definitions.
* **Real Question**: Implement the required project-level transformation so the daily sales activity output can be generated correctly from the existing project context using DBT.
* **Real Trajectory**: The agent inspects upstream macros and intermediate models. It adds a staging file for cleanup. It drafts the final fact-table model joining intermediate models. It executes target query steps locally via dbt run, inspects partial outputs to fix a grain-explosion bug caused by a fan-out join, and finalizes the transformed pipeline.
* **Real Answer**: A completed multi-layer DBT transformation pipeline producing the accurate daily aggregated sales artifacts out of raw warehouse layers.
* **Why this demonstrates the capability**: The final answer emerges from sequential workflow orchestration managing cascading cumulative transformations and intermediate debugging schemas, proving advanced data analysis.
---
**[Case 2]**
* **Initial Environment**: A multi-source infrastructure project base comprising Airbyte Terraform manifests, a destination Snowflake cloud warehouse, and a source Postgres database credentials file with mismatched provider keys.
* **Real Question**: Build an end-to-end pipeline loading Postgres data into Snowflake via Airbyte Terraform configuration, then authoring a SQL model to rank top performers.
* **Real Trajectory**: The agent maps credential inputs logically against the Terraform provider docs. It drafts Terraform manifesting files, triggers an execution, and utilizes a monitoring utility to await Airbyte ingestion confirmation. Observing successful physical replication, it implements complex dimensional ranking window functions within DBT and confirms output matching.
* **Real Answer**: A resilient configuration executing extraction, asynchronous monitoring, and complex data-modeling transformation uniformly integrated.
* **Why this demonstrates the capability**: Tests the complete 'Extract, Load, Transform' lifecycle, demanding infrastructure schema audits alongside database engineering and ensuring multi-application tool synchronization.

## Pipeline Execution Instructions
To synthesize data for this capability, you must strictly follow a 3-phase pipeline. **Do not hallucinate steps.** Read the corresponding reference file for each phase sequentially:

1. **Phase 1: Environment Exploration**
   Read the exploration guidelines to discover raw knowledge seeds:
   `references/EXPLORATION.md`

2. **Phase 2: Trajectory Selection**
   Once Phase 1 is complete, read the selection criteria to evaluate the trajectory:
   `references/SELECTION.md`

3. **Phase 3: Data Synthesis**
   Once a trajectory passes Phase 2, read the synthesis instructions to generate the final data:
   `references/SYNTHESIS.md`

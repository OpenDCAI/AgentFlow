---
name: multi-hop-join-reasoning-data-synthesis
description: Use this skill when the user wants SQL data where the answer requires connecting several tables rather than reading one table directly. Trigger it for requests like “make the model connect the dots”, “it should need multiple hops”, “the answer should come from combining several relations”, or “the agent should have to chain joins before it can rank or filter anything.” Example trigger: “I want multi-hop SQL questions.” Example trigger: “The agent should need to connect several relations before answering.” Example trigger: “Make the answer depend on a chain of joins, not one obvious table.”
---

# Skill: Multi-Hop Join Reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to compose a correct multi-table reasoning chain in SQL, where answering the question requires traversing several relational hops in the right order and preserving the intended semantics at each step.
* **Dimension Hierarchy**: Query Reasoning->Relational and Logical Composition->Multi-Hop Join Reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A biomedical knowledge base links diseases, genes, expression measurements, tissues, and statistical evidence across different tables. No single table directly states the final answer.
* **Real Question**: Which tissues are genes associated with Parkinson’s disease most significantly expressed in?
* **Real Trajectory**: Find Parkinson’s-associated genes, join to gene-expression records, join to tissue annotations, apply the appropriate statistical ranking, and then return the highest-ranked tissues.
* **Real Answer**: The final answer is obtained only after a four-step relational chain over disease, gene, expression, and tissue information.
* **Why this demonstrates the capability**: This question explicitly requires a relational path, not a single lookup. The agent must preserve meaning across every hop, because each intermediate join changes which entities remain eligible for the final ranking. A shortcut or omitted hop produces a semantically wrong SQL query even if the syntax is valid.

---
**[Case 2]**
* **Initial Environment**: An enterprise database spans multiple schemas and nested structures. The user asks for an analytic result whose evidence is scattered across several linked tables.
* **Real Question**: Produce a daily report on key sales activities covering tasks completed, events held, leads generated, and the status of opportunities.
* **Real Trajectory**: Build a date spine, join event activity, join opportunity creation and closure records, derive opportunity status, and aggregate the per-day metrics.
* **Real Answer**: The correct result is a composed daily view that only emerges after several coordinated joins and derived-status logic.
* **Why this demonstrates the capability**: This is a multi-hop join task because the daily report is not stored as a ready-made table. The agent must connect separate operational sources and align them on date semantics before computing the requested output. The difficulty therefore lies in relational composition rather than isolated filtering.

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

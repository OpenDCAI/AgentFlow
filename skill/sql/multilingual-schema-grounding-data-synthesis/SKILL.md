---
name: multilingual-schema-grounding-data-synthesis
description: Use this skill when the user wants SQL training data in more than one language or wants the same task re-expressed across languages without changing its meaning. Trigger it for requests like “make multilingual SQL questions”, “translate the schema too”, “keep the logic identical across languages”, or “test whether the agent can ground non-English wording to the same database semantics.” Example trigger: “I want the same SQL capability tested across several languages.” Example trigger: “Translate the schema and values, not just the question.” Example trigger: “Make multilingual wording preserve the same SQL semantics.”
---

# Skill: Multilingual Schema Grounding

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to map user questions and schema/value inventories across languages while preserving the same executable SQL semantics and avoiding translation-induced grounding errors.
* **Dimension Hierarchy**: Robustness and Adaptation->Interface Adaptation->Multilingual Schema Grounding

### Real Case
**[Case 1]**
* **Initial Environment**: A localized enterprise database has translated table and column names, translated enumerations, and preserved canonical IDs. The question is presented in one of several target languages.
* **Real Question**: For each visitor, days between the first transaction and the first visit in Feb 2017; also report the device category.
* **Real Answer**: The SQL semantics must remain identical after localization, including the time interval logic and the device-category grounding.
* **Why this demonstrates the capability**: This case demonstrates that multilingual grounding is not just sentence translation. The schema, value inventory, and question must all stay semantically aligned so the same executable query is recovered in another language. That makes it a direct probe of multilingual schema grounding.

---
**[Case 2]**
* **Initial Environment**: A multilingual benchmark preserves canonical product identities while localizing question text and database snapshots. Entity strings can become ambiguous after translation.
* **Real Question**: Show me top-selling product among customers who bought YouTube Men’s Vintage Henley in July 2017 (exclude that product).
* **Real Answer**: A correct multilingual answer must preserve the canonical product mention while still producing the same exclusion and ranking semantics.
* **Why this demonstrates the capability**: Translation can easily damage entity identity here by partially translating or over-normalizing the product name. The agent must therefore ground the localized text back to the preserved canonical entity representation. This is a core multilingual grounding challenge, not just a ranking problem.

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

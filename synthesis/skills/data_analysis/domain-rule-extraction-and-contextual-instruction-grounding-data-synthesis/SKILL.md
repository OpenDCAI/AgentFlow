---
name: domain-rule-extraction-and-contextual-instruction-grounding-data-synthesis
description: Use this skill when the user wants questions that are easy to misread unless the agent follows the domain rules correctly. Trigger it for requests such as “make it obey the business logic in the docs,” “make it read the fine print,” “make it use the rules hidden in the manual,” or “make it answer wrong if it ignores the context.” Plain-language examples: “Ask something where the dataset alone is not enough,” “make it use the rulebook,” “make the trick be in the instructions, not in the math.”
---

# Skill: Domain-Rule Extraction And Contextual Instruction Grounding

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to identify and apply domain-specific rules, implicit business logic, or contextual constraints that are described in accompanying documentation rather than encoded directly in the raw data. It focuses on translating textual rules into correct analytical operations and answer formatting.
* **Dimension Hierarchy**: Data Grounding->Contextual Knowledge Grounding->domain-rule extraction and contextual instruction grounding

### Real Case
**[Case 1]**
* **Initial Environment**: Transaction data and cost documentation are available, together with domain-specific definitions of authorization indicators and fraud-related costs. The environment supports iterative analysis in code.
* **Real Question**: For the year 2023, focusing on the merchant Growth Funds, if we aimed to reduce fraudulent transactions by encouraging users to switch to a different Authorization Characteristic Indicator through incentives, which option would be the most cost-effective?
* **Real Trajectory**: Read the documentation that defines the Authorization Characteristic Indicator options and the associated cost logic; filter the merchant and year in the transaction data; estimate the fraud-reduction effect for each switch option under the documented rule; compare total cost under the incentive assumption; report the cheapest option and value.
* **Real Answer**: B=34.49
* **Why this demonstrates the capability**: The raw data does not tell the agent how to compare options unless the textual rulebook is applied correctly. The capability therefore lies in extracting the relevant business rule and turning it into executable analytical logic. A model that skips the contextual rule may still compute something, but it will compute the wrong thing.

---
**[Case 2]**
* **Initial Environment**: Multiple structured files are accompanied by business documentation that defines how category changes should affect fees. The answer depends on interpreting the documentation rather than merely reading a fee column.
* **Real Question**: If merchant X changed its business category, how would that affect fees?
* **Why this demonstrates the capability**: This task directly tests whether the agent can translate a textual business rule into a fee-impact analysis. It requires understanding that the effect of a category change is mediated by documented fee logic, not just by the raw transaction table. The capability is therefore contextual instruction grounding rather than ordinary aggregation.

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

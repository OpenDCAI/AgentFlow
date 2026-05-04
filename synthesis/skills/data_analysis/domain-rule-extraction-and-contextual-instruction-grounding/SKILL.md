---
name: domain-rule extraction and contextual instruction grounding
description: Use this skill when the user wants questions that are easy to misread unless the agent follows the domain rules correctly. Trigger it for requests such as “make it obey the business logic in the docs,” “make it map vague business terms to exact system IDs,” “make it read the fine print,” or “make it answer wrong if it ignores the context.” Plain-language examples: “Ask something where the dataset alone is not enough,” “make it look up what this acronym means first,” “make the trick be in the instructions, not in the math.”
---

# Skill: domain-rule extraction and contextual instruction grounding

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to identify and apply domain-specific rules, implicit business logic, or contextual dictionary mappings that are described in accompanying documentation rather than encoded directly in the raw tabular data. It focuses on translating textual rules into correct analytical operations, mapping fuzzy natural language concepts to explicit database schemas, and adapting programmatic formulas securely.
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
* **Real Trajectory**: Look up fee application rules across category types. Find X's old category, compute potential fees if shifted to the query's target category based strictly on paragraph rules in the context map.
* **Real Answer**: Ignore specific value, report the derived delta.
* **Why this demonstrates the capability**: This task directly tests whether the agent can translate a textual business rule into a fee-impact analysis. It requires understanding that the effect of a category change is mediated by documented fee logic, not just by the raw transaction table.
---
**[Case 3]**
* **Initial Environment**: A sandbox containing generic transaction APIs/Logs and a policy string database (Markdown/JSON dictionary) defining fiscal quarters and mapping regional codes for a global conglomerate.
* **Real Question**: Compare the total revenue for the 'target zone' during the 'previous peak period' vs current levels.
* **Real Trajectory**: Identify context-dependent variables 'target zone' and 'previous peak period'; query internal metadata rulebooks to discover 'target zone' legally maps to 'Region_ID 402' and 'peak period' is textually defined as 'Q4 2023'; build explicit filtering code extracting these precise constraints.
* **Real Answer**: Revenue in Region 402 decreased from $5.2M (Q4 2023) to $4.8M (current).
* **Why this demonstrates the capability**: The query contains fuzzy business placeholders that are entirely untraceable against base data frames unless the agent physically grounds the terms against domain dictionaries. The agent proves its capability by translating text-based logic mapping rules into the explicit numeric parameters necessary for code generation.

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

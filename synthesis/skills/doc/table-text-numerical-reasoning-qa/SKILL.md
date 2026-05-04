---
name: table-text numerical reasoning qa
description: Use this skill when the user wants the agent to perform document-grounded math, execute multi-step financial formulas, or perform 'intrinsic fact-checking' to recover masked or missing numerical values from tables. Trigger it for requests like 'calculate the ROI', 'verify if this revenue figure is consistent with the balance sheet', 'find the year-over-year growth rate', 'recover the missing value in this report', or 'perform latent variable inference to find the equity investment'. This skill is essential for detecting numerical hallucinations and ensuring calculated values are strictly faithful to the provided document context.
---

# Skill: table-text numerical reasoning qa

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform high-fidelity quantitative reasoning by resolving symbolic variables and numerical fields across prose, single tables, or multi-table structures, while maintaining strict 'intrinsic faithfulness' to the context. This capability encompasses four levels of reasoning: (1) Direct Lookup (cell extraction), (2) Comparative Calculation (temporal/category change), (3) Bivariate Calculation (ratios/functions of two metrics), and (4) Multivariate Calculation (latent variable inference and chained arithmetic). It specifically targets the mitigation of 'intrinsic hallucinations'—errors where the output contradicts the input context—by enforcing rigorous unit/scale normalization and multi-step evidence binding.
* **Dimension Hierarchy**: Document Grounding & Reasoning->Evidence Use->table-text numerical reasoning qa

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-page financial filing for 'The Priceline Group' containing a table labeled 'Comparative Stock Performance' with rows for 2010 through 2015.
* **Real Question**: What was the percent of the growth of The Priceline Group Inc. from 2014 to 2015?
* **Real Trajectory**: The agent scans the document for 'Priceline Group', locates the correct table, identifies the measurement point rows for 2014 (value 285.37) and 2015 (value 319.10), and then applies the percentage growth formula: ((Current - Prior) / Prior) * 100.
* **Real Answer**: 11.82%
* **Why this demonstrates the capability**: This illustrates 'Comparative Calculation' (Scenario B) where the agent must correctly bind two temporally distinct values from a table and execute a derived growth calculation not explicitly stated in the text.
---
**[Case 2]**
* **Initial Environment**: A technical financial report containing details on unconsolidated ventures and a specific table for 'Investment Property Debt' where pro-rata shares are listed.
* **Real Question**: Fund V acquired a 90% interest in an unconsolidated venture for a shopping center, Mohawk Commons, which was purchased for $62.1 million. Based on the debt table, how much was the total equity investment for Fund V?
* **Real Trajectory**: The agent identifies 'Mohawk Commons' in the table. It extracts the pro-rata debt ($7.2M) and ownership percentage (18.1%). It calculates the total mortgage debt by dividing pro-rata debt by ownership ($7.2 / 0.181 = $39.7M). It then subtracts this total debt from the purchase price ($62.1M - $39.7M = $22.4M equity) and applies the Fund's 90% interest to find the final value.
* **Real Answer**: $20.2 million
* **Why this demonstrates the capability**: This represents the 'Multivariate Calculation' (Scenario D) or 'Latent Variable Inference'. The agent must synthesize information across text (purchase price, % interest) and tables (pro-rata debt, ownership %) to infer a missing variable through a multi-step logical chain.
---
**[Case 3]**
* **Initial Environment**: A long-context financial report containing multiple fragmented tables and an XBRL formula for 'Return on Investment (ROI)'.
* **Real Question**: Based on the provided formula for ROI and the financial tables, calculate the ROI for the fiscal year ending December 31.
* **Real Trajectory**: The agent identifies the variables in the ROI formula (Net Income / Total Investment). It then navigates to the 'Consolidated Statement of Operations' to find Net Income and jumps to the 'Balance Sheet' on a different page to locate Total Investment. Finally, it executes the division and normalizes the resulting decimal into a percentage.
* **Real Answer**: 15.4
* **Why this demonstrates the capability**: This illustrates 'Bivariate Calculation' (Scenario C) combined with multi-table navigation. The agent maps an abstract equation to discrete numerical operands located in different document sections.

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

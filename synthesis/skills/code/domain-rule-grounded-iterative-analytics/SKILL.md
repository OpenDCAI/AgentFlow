---
name: domain-rule-grounded-iterative-analytics
description: Use this skill when an analytics or data transformation task requires combining structured data (CSVs, databases) with unstructured domain logic found in manuals, project handbooks, regulatory guidelines, or business documentation. It is triggered by plain-language requests such as 'calculate our fraud rates using the risk manual', 'harmonize clinical lab data across our medical centers using the conversion guide', 'check if these transactions follow the scheme fee rules', or 'perform a multi-step financial audit'. It is specifically meant for cases where the agent cannot write the code until it first understands complex, implicit rules or industry standard operating procedures (SOPs) buried in text files.
---

# Skill: domain-rule-grounded-iterative-analytics

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform multi-step, iterative data analysis and workflow automation by grounding technical code execution (SQL/Python) in domain-specific business rules, regulatory frameworks, and standard operating procedures (SOPs) extracted from heterogeneous documentation. This involves planning a sequential workflow that alternates between reading unstructured knowledge sources (e.g., Markdown manuals, PDFs) and manipulating structured datasets to resolve implicit constraints, apply domain-specific transformations, and produce strictly compliant data artifacts.
* **Dimension Hierarchy**: Data and ML Workflow Engineering->Enterprise Data Workflow Coding->domain-rule-grounded-iterative-analytics

### Real Case
**[Case 1]**
* **Initial Environment**: The environment contains a large payment transaction record (transactions.csv) and a domain dictionary (risk_manual.md) which defines specific fraud thresholds for different card categories and regions.
* **Real Question**: Identify which card scheme had the highest average fraud rate in 2023 according to the definitions in our manual.
* **Real Trajectory**: The agent first reads the manual to identify the technical definition of 'fraud rate' and the specific flag codes used in the transaction data. It then loads the transactions.csv file using a data library, filters the records for the year 2023, and performs a group-by operation to calculate the mean of the identified fraud flags per scheme. Finally, it compares the calculated averages and identifies the top scheme.
* **Real Answer**: Visa
* **Why this demonstrates the capability**: This demonstrates the capability because the agent could not solve the task with a simple query alone. It had to first consult unstructured documentation to discover the semantic meaning of 'fraud' within that specific business context before executing the analytical code.
---
**[Case 2]**
* **Initial Environment**: The workspace includes a merchant database (merchants.json), a fee structure table (fees_config.csv), and a 50-page processing handbook (manual.md) explaining how Merchant Category Codes (MCC) influence interchange costs.
* **Real Question**: If Merchant X changed its business category from Retail to Food Services, how would that affect its average monthly interchange fees based on current scheme rules?
* **Real Trajectory**: The agent starts by identifying Merchant X's current traffic profile in the merchant data and calculating its baseline fees. It then searches the manual for the rules governing the 'Food Services' category and cross-references these with the fee config table to find the new rates. It simulates the monthly volume under the new rate structure, subtracts the baseline, and reports the specific value difference.
* **Real Answer**: 1245.50
* **Why this demonstrates the capability**: Success requires multi-step reasoning across three distinct data formats. The agent must bridge the gap between a hypothetical business change and the concrete numerical impact by interpreting high-level category rules found in the manual.
---
**[Case 3]**
* **Initial Environment**: A healthcare analytics environment contains multiple clinical lab datasets where unit measurements (e.g., mg/dL vs. mmol/L) vary across different medical center identifiers. A conversion reference manual in PDF format is provided alongside the raw CSV files.
* **Real Question**: Harmonize the clinical lab unit data across the entire healthcare system to ensure all measurements follow the project's standard internal reporting units as strictly defined in the conversion manual.
* **Real Trajectory**: The agent performs a diagnostic scan of the mismatched identifiers and cross-references them with the provided conversion manual. It identifies the specific SOP formulas required for each lab test type (e.g., glucose vs. cholesterol) and implements a robust Python transformation script. During execution, it encounters a data record with an undefined unit; it uses a secondary lookup logic from an appendix to infer the correct conversion factor based on the measurement range. It then executes a validation pass to ensure numerical consistency across the harmonized columns.
* **Real Answer**: A unified clinical dataset where all laboratories provide measurement values in identical standardized units as dictated by the domain manual, allowing for valid comparative medical research.
* **Why this demonstrates the capability**: Success requires the agent to ground technical code in professional industry standards. It tests the ability to resolve domain-specific dependencies (unit conversion rules from procedural literature) while maintaining data integrity across disparate database silos.

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

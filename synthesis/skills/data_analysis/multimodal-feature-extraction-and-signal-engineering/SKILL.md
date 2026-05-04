---
name: multimodal feature extraction and signal engineering
description: Use this skill when the user wants to pull specific insights or features out of diverse, non-tabular sources—like scanned PDF receipts, time-series telemetry (e.g., sensor logs, vital signs), or short narrative logs—and combine them with standard tables. This skill is critical when you need to turn raw 'unstructured' signals into clean numbers for a model or a report. Trigger it for requests like "get the line items from these scanned bills," "calculate the trend of these sensor readings over 10 days," or "count how many times the status notes say 'improved' or 'ready'." Plain-language examples: "Look through the PDF invoices and add a column for laboratory costs," "tell me if the patient's heart rate is getting better or worse based on the logs," or "summarize the daily notes into a 'positivity' score before doing the math."
---

# Skill: multimodal feature extraction and signal engineering

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability involves the synthesis of analytical features from heterogeneous data modalities—including scanned documents (via text-based extraction), high-frequency sequential telemetry, and short-form unstructured narratives—to enhance structured predictive or descriptive models. It emphasizes task-specific signal engineering, such as applying statistical regression slopes to time-series sequences, mapping specific domain identifiers (e.g., CPT or SKU codes) from documents via regex, and using keyword-driven temporal aggregation for sparse text logs where traditional NLP methods like TF-IDF fail. Success requires the agent to derive physiologically or operationally meaningful composite scores (e.g., stability indicators, cost-per-unit ratios) that bridge the gap between raw unstructured data and structured analytical targets.
* **Dimension Hierarchy**: Analytical Transformation -> Data Preparation -> multimodal feature extraction and signal engineering

### Real Case
**[Case 1]**
* **Initial Environment**: A folder contains a structured spreadsheet of prior patient visitation history and a sub-directory of scanned PDF billing receipts. The agent has access to standard CSV tools and a PDF text-extraction library like PyPDF2.
* **Real Question**: Calculate the ratio of imaging costs to total billed costs for each patient by extracting line-item details from their PDF receipts and joining them with the visitation records.
* **Real Trajectory**: Load the structured visitation table as a primary index; initialize a PDF parsing loop to iterate through each patient's billing receipt; use regular expressions to isolate CPT codes in the imaging range (70000-79999) and their associated costs; aggregate the imaging-specific costs and total billed amounts per patient; join these extracted features back to the main table; compute the final 'imaging_cost_ratio' column.
* **Real Answer**: Patient_01: 0.15, Patient_02: 0.22, ...
* **Why this demonstrates the capability**: The agent must perform multimodal extraction by mapping a specific domain identifier (CPT range) from a non-tabular source (PDF) and then conduct cross-source feature engineering to derive a new analytical ratio that does not exist in the raw data.
---
**[Case 2]**
* **Initial Environment**: A data sandbox provides a large table of hospital stay records (unit type, age) and a secondary 'telemetry' file containing 10-day sequences of heart rate and temperature readings for each stay.
* **Real Question**: Which unit type has the highest percentage of patients whose heart rate trend was 'improving' (defined as a negative linear slope over 10 days)?
* **Real Trajectory**: Load the heart rate time-series data; group the sequences by patient identifier; apply a linear regression function to the 10-day heart rate array for each patient to extract the slope (trend); create a binary 'improving' flag for all patients with a negative slope; join this flag with the 'unit type' metadata from the structured stay table; aggregate the percentage of improving patients per unit; identifying the top unit.
* **Real Answer**: ICU Unit (68% improving)
* **Why this demonstrates the capability**: This case requires transforming raw sequential telemetry into a high-level statistical signal (the slope) and grounding that engineered feature in a structured metadata context to answer a comparative question.
---
**[Case 3]**
* **Initial Environment**: The environment holds a dataset of daily operational logs (short 10-20 word text snippets) and a structured table of facility performance metrics. Traditional TF-IDF analysis is too sparse for the short snippets.
* **Real Question**: Assess facility readiness based on the trend of 'readiness keywords' (e.g., 'cleared', 'functional', 'ready') in the daily logs from the last 3 days.
* **Real Trajectory**: Inspect the log structure and determine that TF-IDF is unsuitable for the short entries; load a predefined dictionary of readiness-related keywords; count keyword occurrences in each daily log for the target window (last 3 days); calculate the daily count trend (rolling average or slope); merge the trend score with the facility table; flag facilities with an upward readiness trajectory.
* **Real Answer**: Facility_Alpha: Improving (Score +0.5), Facility_Beta: Stable (Score 0.0)
* **Why this demonstrates the capability**: The agent identifies the failure of standard text processing for short logs and pivots to keyword-driven temporal aggregation, successfully engineering a 'readiness trend' signal from narrative fragments.

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

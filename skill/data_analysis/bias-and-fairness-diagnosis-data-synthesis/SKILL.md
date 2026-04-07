---
name: bias-and-fairness-diagnosis-data-synthesis
description: Use this skill when the user wants fairness or bias questions over structured data. Trigger it for requests such as “make it detect bias in the dataset,” “make it check whether two demographic features are linked unfairly,” “make it diagnose skew or unfair allocation,” or “make it explain bias levels with charts.” Plain-language examples: “Ask whether race and insurance are influencing each other,” “make it spot unfair patterns,” “make it measure how biased the data is.”
---

# Skill: Bias And Fairness Diagnosis

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to detect, quantify, and explain bias or unfairness patterns in structured data by selecting suitable metrics and analyses for the relevant data types and relationships. It includes distribution bias, correlation bias, implication bias, severity labeling, visualization, and recommendation generation.
* **Dimension Hierarchy**: Analytical Transformation->Data Preparation->bias and fairness diagnosis

### Real Case
**[Case 1]**
* **Initial Environment**: A structured dataset is available together with a bias-detection toolkit and method library covering different combinations of data type and bias type. The agent can preprocess data, run bias analyses, visualize results, and produce a report.
* **Real Question**: I need your assistance to see if race and insurance type might be influencing each other in this dataset. Could there be a link here?
* **Real Trajectory**: Load and preprocess the relevant columns; classify the task as a correlation-bias problem over categorical features; retrieve appropriate bias-detection methods; execute the selected tests; summarize the bias level; create visualizations and a report.
* **Why this demonstrates the capability**: The task demonstrates that bias diagnosis is not one metric but a method-selection problem driven by data type and relationship type. The agent must choose appropriate analyses, not just compute a generic summary. That is exactly the intended fairness-diagnosis capability.

---
**[Case 2]**
* **Initial Environment**: The environment contains structured healthcare-related data and a method library that supports both high-level and metric-specific bias questions. The agent can generate both numerical results and natural-language summaries.
* **Real Question**: Does insurance type influence the allocation of medical resources?
* **Why this demonstrates the capability**: The question is phrased at a general level, but answering it rigorously requires turning the abstract fairness concern into measurable comparisons or causal-effect style analyses. This makes the capability about diagnosing bias from structured data with suitable metrics and clear interpretation. It is therefore a strong example of bias and fairness diagnosis.

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

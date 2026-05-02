---
name: data-cleaning-and-normalization-data-synthesis
description: Use this skill when the user wants messy-data questions where the agent has to clean first and analyze later. Trigger it for requests such as “make it handle dirty columns,” “make it find bad rows,” “make it normalize before computing,” or “ask something where cleaning is the key move.” Plain-language examples: “Give me a question with outliers,” “make it fix formatting or missing data first,” “make it preprocess before answering.”
---

# Skill: Data Cleaning And Normalization

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to detect, correct, standardize, and normalize imperfections in raw data so that downstream analysis is valid. It includes outlier handling, missing-value treatment, recoding, unit normalization, and other preprocessing steps that align the data with an explicit analytical rule.
* **Dimension Hierarchy**: Analytical Transformation->Data Preparation->data cleaning and normalization

### Real Case
**[Case 1]**
* **Initial Environment**: A realistic CSV file is provided together with a closed-form analysis prompt. The question specifies a concrete outlier-detection method and threshold, so the agent must preprocess and standardize the target column before counting outliers.
* **Real Question**: Identify any outliers in the "Limit" column of the Credit.csv file using the Z-score method.
* **Real Trajectory**: Load Credit.csv; isolate the Limit column; compute mean and standard deviation; standardize each value into a Z-score; count points with absolute Z-score greater than 3; return the outlier count in the required format.
* **Real Answer**: 1
* **Why this demonstrates the capability**: The core challenge is not complex modeling but method-faithful preprocessing and normalization. The agent must apply a precise statistical rule to raw values and avoid ad hoc thresholding. That is a canonical cleaning-and-normalization behavior.

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

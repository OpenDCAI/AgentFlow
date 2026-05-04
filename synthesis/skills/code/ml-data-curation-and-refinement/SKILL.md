---
name: ml-data-curation-and-refinement
description: Use this skill when the user wants to prepare, clean, or label datasets for machine learning using specialized code and automated models. Trigger it for requests like 'fill in the missing gaps in my data', 'automatically label this dataset based on our rules', 'impute the null values in my training set', or 'fix the data quality before training'. It is specifically designed for complex ML engineering tasks involving model-based imputation (like recovering sensor readings) and weak supervision pipelines (like heuristic-based labeling) rather than simple SQL data transformations.
---

# Skill: ml-data-curation-and-refinement

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to architect and implement data-centric engineering workflows for machine learning, specifically focusing on the automation of data imputation and weak supervision pipelines to enhance dataset quality and model readiness. This involves performing a diagnostic analysis of dataset missingness distributions, implementing iterative quality-refinement loops using specialized algorithms (e.g., diffusion-based imputation), and utilizing programmatic labeling functions to transform raw or corrupted datasets into high-fidelity training assets while maintaining statistical and semantic integrity.
* **Dimension Hierarchy**: Data and ML Workflow Engineering->Machine Learning Engineering->ml-data-curation-and-refinement

### Real Case
**[Case 1]**
* **Initial Environment**: A machine learning workspace contains a weather sensor dataset (PM2.5) with 40% missing entries and a repository for the CSDI (Conditional Score-based Diffusion) imputation model. The environment includes a configuration file defining the temporal and spatial coordinates of the sensor network.
* **Real Question**: Implement and execute the CSDI imputation pipeline to recover the missing PM2.5 values in the weather dataset, ensuring the resulting Mean Absolute Error (MAE) is minimized according to the project's baseline.
* **Real Trajectory**: The agent first performs a diagnostic scan of the CSV files to identify the distribution of null values across time-steps and sensor locations. It then navigates to the CSDI repository, configures the model's noise schedule and batch size to match the provided sensor dimensions, and initializes the training process on the available non-missing data. After the diffusion model converges, the agent executes the reverse sampling process to impute the gaps and calculates the MAE by comparing a held-out subset of the ground-truth data against the generated values.
* **Real Answer**: A completed dataset where all null values are replaced by model-generated estimates, achieving a Mean Absolute Error of 13.5.
* **Why this demonstrates the capability**: This demonstrates the capability because the agent had to perform a sophisticated engineering loop: diagnosing missingness patterns, configuring a complex generative model (CSDI), and verifying numerical fidelity (MAE) of the imputed data rather than performing simple mean-filling.
---
**[Case 2]**
* **Initial Environment**: A healthcare repository contains 20,000 unlabeled ECG signal recordings and a documentation manual providing expert rules for detecting heart arrhythmias (e.g., 'R-peak distance < 0.2s implies Class A'). A skeleton script for weak supervision labeling is available.
* **Real Question**: Develop a weak supervision pipeline to label the ECG dataset. Use the heuristic rules found in the manual to assign initial labels and then refine them into a unified training set.
* **Real Answer**: A labeled dataset where each signal is assigned an arrhythmia category based on a consensus of the implemented heuristic rules, validated against an expert-labeled 1% sample set with 85% accuracy.
* **Why this demonstrates the capability**: The agent must bridge the gap between abstract domain rules and executable labeling functions. Success requires transforming unstructured heuristic descriptions into a programmatic pipeline that labels large-scale data automatically, satisfying the 'Weak Supervision' engineering requirement.

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

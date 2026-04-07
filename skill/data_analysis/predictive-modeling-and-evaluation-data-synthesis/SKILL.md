---
name: predictive-modeling-and-evaluation-data-synthesis
description: Use this skill when the user wants model-building or model-scoring tasks rather than simple statistics. Trigger it for requests such as “make it train or apply a model,” “make it generate predictions,” “make it compare model quality,” or “make it produce a submission file.” Plain-language examples: “Give me a forecasting or prediction task,” “make it output the model result file,” “make it evaluate how good the model is.”
---

# Skill: Predictive Modeling And Evaluation

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to construct, fit, or apply predictive models and to evaluate their quality using the metric specified by the task. It includes choosing appropriate features, training or parameter application, generating outputs in the required artifact format, and validating the model with explicit metrics or benchmark targets.
* **Dimension Hierarchy**: Analytical Transformation->Analytical Inference->predictive-modeling-and-evaluation

### Real Case
**[Case 1]**
* **Initial Environment**: A data-science prompt is paired with CSV files and an evaluation function. The task expects code that reads model parameters or data files and writes the required output artifact.
* **Real Question**: Implement the desired _marketing_expenditure function, which returns the required amount of money that needs to be invested in a new marketing campaign to sell the desired number of units.
* **Real Trajectory**: Load model_parameters.csv; interpret the coefficients needed by the required function; compute the expenditure for the target number of units; write the result to required_expenditure.txt in the required format; verify that the output artifact exists and contains a single float value.
* **Why this demonstrates the capability**: The task goes beyond descriptive analysis because it requires applying a predictive relationship and producing an executable artifact in the exact format expected by evaluation. It therefore tests both modeling logic and output compliance.

---
**[Case 2]**
* **Initial Environment**: The agent receives train.csv, test.csv, sample_submission.csv, and optional domain knowledge. The objective is to write end-to-end code that produces submission.csv for automated evaluation.
* **Real Question**: An end-to-end Python script that produces 'submission.csv'.
* **Real Trajectory**: Read the train and test data with pandas; select and engineer features based on the task description and any vetted side information; fit a predictive model; generate predictions on the test set; write submission.csv in the specified format.
* **Why this demonstrates the capability**: This is a direct predictive-modeling task because the core output is a prediction artifact rather than a descriptive statistic. The agent must combine modeling, format compliance, and task-specific evaluation awareness. Those are the defining properties of predictive modeling and evaluation.

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

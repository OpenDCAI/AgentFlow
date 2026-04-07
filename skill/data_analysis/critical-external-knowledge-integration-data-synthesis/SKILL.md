---
name: critical-external-knowledge-integration-data-synthesis
description: Use this skill when the user wants the agent to judge advice instead of following every hint. Trigger it for requests such as “make it tell good tips from bad tips,” “make the docs partly helpful and partly misleading,” “make it use outside advice carefully,” or “make it resist wrong feature ideas.” Plain-language examples: “Give me a question where some hints are traps,” “make it filter bad advice,” “make it read notes but not trust all of them.”
---

# Skill: Critical External-Knowledge Integration

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to use external guidance, hints, notebooks, or side information selectively rather than blindly. It requires distinguishing beneficial domain knowledge from harmful, irrelevant, or adversarial advice and then integrating only the guidance that improves the end-to-end analytical pipeline.
* **Dimension Hierarchy**: Data Grounding->Contextual Knowledge Grounding->critical external-knowledge integration

### Real Case
**[Case 1]**
* **Initial Environment**: The agent receives tabular train and test files, a sample submission format, and optional domain knowledge bundled as side information. Some hints are helpful and some are adversarial, and the goal is to generate end-to-end Python code that produces a valid submission file.
* **Real Question**: You will be provided with corresponding information about the data, including the task description, submission format, and evaluation metrics; the dataset; and optional domain knowledge that may help improve your solution. You should decide whether to use these domain knowledge.
* **Real Trajectory**: Read the task description and the train/test schema; inspect the side information bundle; test which hints align with the feature semantics and target type; ignore hints that would remove core predictive variables or violate split logic; generate code that reads the CSV files and writes submission.csv.
* **Why this demonstrates the capability**: The task explicitly asks the agent to decide whether to use the provided domain knowledge. Correct behavior therefore requires selective integration rather than blanket adoption. This makes it a direct test of critical external-knowledge use in automated data science.

---
**[Case 2]**
* **Initial Environment**: A tabular prediction task includes feature descriptions such as Location, Decoration, House Age, and School Quality, along with bundled guidance from outside sources. Some guidance recommends adding useful features, while some guidance recommends removing predictive ones.
* **Real Question**: Produce an end-to-end Python script that generates submission.csv using the provided data and optional domain knowledge.
* **Real Trajectory**: Inspect the feature space and target format; compare helpful hints such as adding School Quality or House Age against adversarial hints such as removing Location; keep the hints that improve a plausible predictive signal; reject the hints that weaken core semantics; output a valid submission file.
* **Why this demonstrates the capability**: This case demonstrates that external knowledge can be mixed-quality and that strong agents must evaluate it critically. The task is not just about modeling but about deciding which outside advice deserves to influence the pipeline. That judgment is the capability under test.

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

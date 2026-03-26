---
name: visualization-grounded-insight-reporting-data-synthesis
description: Use this skill when the user wants the agent not only to compute but also to present the result clearly with charts or report-style insights. Trigger it for requests such as “make it create a figure and explain it,” “make it summarize the chart,” “make it turn analysis into clear takeaways,” or “make it produce a report from the data.” Plain-language examples: “Give me a question where it has to plot and explain,” “make it write the key insights after the graph,” “make it present the findings, not just the number.”
---

# Skill: Visualization-Grounded Insight Reporting

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to translate analytical outputs into human-readable insights that remain grounded in computed data and, where relevant, associated figures or charts. It includes producing visualizations, saving the required artifacts, and writing concise interpretations that faithfully reflect the underlying quantitative evidence.
* **Dimension Hierarchy**: Agentic Execution & Communication->Result Communication->visualization-grounded insight reporting

### Real Case
**[Case 1]**
* **Initial Environment**: A business question, database schema, and raw data are available in a sandbox. The workflow requires code generation, offline code execution, a saved chart, saved extracted data, and short textual insights.
* **Real Question**: Please save the plot to "figure.pdf" and save the label and value shown in the graph to "data.txt".
* **Real Trajectory**: Generate Python code that extracts the relevant data and plots the requested chart; execute the code; save the figure as figure.pdf; save the chart data as data.txt; feed the question and extracted data into the analysis step; generate five grounded bullet-point insights.
* **Why this demonstrates the capability**: The task explicitly couples visualization artifacts with textual interpretation. A correct agent must not only compute and plot but also ensure that its written insights are aligned with the extracted data. That makes the capability about visualization-grounded reporting rather than bare computation.

---
**[Case 2]**
* **Initial Environment**: A structured dataset and fairness-analysis toolkit are available, and the agent is expected to produce not only metric results but also visualizations and a user-facing report. The workflow includes preprocessing, bias analysis, chart generation, and report summarization.
* **Real Question**: I need your assistance to see if race and insurance type might be influencing each other in this dataset. Could there be a link here?
* **Real Trajectory**: Run the relevant bias analyses for race and insurance type; summarize the detected bias level; create visualizations that expose the relationship; compile a report containing bias types, relevant features, detection metrics, and suggestions; return the user-facing summary.
* **Why this demonstrates the capability**: This task demonstrates that insight reporting must remain grounded in the actual analytical result rather than generic commentary. The agent has to transform measured bias evidence into charts and recommendations that a user can act on. That is exactly the presentation skill this capability captures.

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

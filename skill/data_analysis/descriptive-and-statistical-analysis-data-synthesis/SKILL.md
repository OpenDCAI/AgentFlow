---
name: descriptive-and-statistical-analysis-data-synthesis
description: Use this skill when the user wants classic stats questions rather than retrieval or modeling-heavy tasks. Trigger it for requests such as “make it run a correlation,” “make it compute a regression score,” “make it compare distributions,” or “ask something statistical but still code-based.” Plain-language examples: “Give me a question about whether two columns are related,” “make it summarize patterns numerically,” “make it produce a statistic and interpret it.”
---

# Skill: Descriptive And Statistical Analysis

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to compute and interpret descriptive statistics or classical statistical relationships from data once the relevant variables are available. It includes summaries, correlations, regressions, distributional comparisons, and similar inference-lite analyses that produce direct numerical or categorical conclusions.
* **Dimension Hierarchy**: Analytical Transformation->Analytical Inference->descriptive and statistical analysis

### Real Case
**[Case 1]**
* **Initial Environment**: A CSV file containing country-level indicators is provided in a code-execution environment. The question fixes both the variables of interest and the evaluation statistic.
* **Real Question**: Is there a linear relationship between the GDP per capita and the life expectancy score in the Happiness_rank.csv? Conduct linear regression and use the resulting coefficient of determination (R-squared) to evaluate the model's goodness of fit.
* **Real Trajectory**: Load Happiness_rank.csv; extract GDP per capita and life expectancy; fit a linear regression model; compute the predicted values and the R-squared score; map the score to the requested qualitative fit judgment; output the final answer.
* **Real Answer**: The R-squared value is approximately 0.67, which indicates a poor fit for the linear regression model.
* **Why this demonstrates the capability**: The task tests whether the agent can execute a concrete statistical procedure and tie the numeric result to an interpretation. It is neither just plotting nor just code completion; it is faithful descriptive-statistical analysis under explicit instructions.

---
**[Case 2]**
* **Initial Environment**: A notebook environment contains biological differential-expression outputs for several strains. The agent must derive a descriptive statistic over sets of genes after loading and comparing the relevant results.
* **Real Question**: What percentage of genes differentially expressed in strain 97 are also differentially expressed in strain 99?
* **Real Trajectory**: Load the relevant strain-specific result files; construct the gene sets that meet the differential-expression criterion for strains 97 and 99; compute the overlap as a percentage of the strain-97 set; submit the percentage.
* **Why this demonstrates the capability**: This case demonstrates descriptive analysis in a scientific setting where the computation is a set-based summary statistic rather than a model fit. The agent must still convert raw outputs into a quantitatively interpretable relationship. That is squarely within descriptive and statistical analysis.

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

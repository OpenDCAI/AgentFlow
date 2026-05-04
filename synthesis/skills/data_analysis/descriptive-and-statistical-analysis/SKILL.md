---
name: descriptive and statistical analysis
description: Use this skill when the user wants classic stats questions, formal hypothesis testing, or interpretation of patterns like clusters and groupings. Trigger it for requests such as “run a correlation,” “check if results are significant,” “run a t-test,” “explain the main groups in the data,” or “find out what the main axes in the plot mean.” Plain-language examples: “Is there a real difference between these two categories?”, “What are the strongest groups in the dataset?”, “Tell me how these numbers relate to each other,” or “Explain which variables drive the separation in the chart.”
---

# Skill: descriptive and statistical analysis

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to compute and interpret descriptive statistics, classical statistical relationships, formal hypothesis tests (t-tests, ANOVA, Chi-square), and unsupervised pattern extractions (Clustering, Dimensionality Reduction) once the relevant variables are available. It encompasses the mapping of numerical or latent results (p-values, R-squared, PCA loadings, cluster labels) to qualitative biological or business insights, while ensuring the analysis is calibrated for the specific data modality and platform context.
* **Dimension Hierarchy**: Analytical Transformation->Analytical Inference->descriptive and statistical analysis

### Real Case
**[Case 1]**
* **Initial Environment**: A high-dimensional data environment (such as an AnnData object or a matrix) is provided, containing feature measurements and observation labels. The environment supports dimensionality reduction tools like PCA.
* **Real Question**: After performing dimensionality reduction, which cell populations are primarily separated along the first principal component (PC1)?
* **Real Trajectory**: Load the dataset; compute principal components (PCA); extract the loadings for PC1 to identify top contributing features; examine the distribution of existing labels along the PC1 axis; identify that Category A has high positive scores while Category B has negative scores; conclude that PC1 separates Category A from Category B.
* **Real Answer**: PC1 primarily separates Category A and Category B.
* **Why this demonstrates the capability**: The agent must go beyond simple calculation by interpreting a latent statistical axis and grounding it in known metadata categories. Success requires relating mathematical variance to descriptive labels, which is a core part of advanced statistical analysis.
---
**[Case 2]**
* **Initial Environment**: A spatial data sandbox is provided, containing coordinate-aware measurements (x, y) and estimated sub-population abundances. The task requires identifying localized tissue structures.
* **Real Question**: Identify the bone-formation niche (area of active growth) and determine which 5 marker genes are most significantly enriched there.
* **Real Trajectory**: Cluster the data based on local sub-population composition; identify the cluster that corresponds to the 'bone-formation' signature; perform a differential expression test (e.g., t-test or Wilcoxon) comparing this cluster to all others; rank genes by significance and fold-change; return the top 5 genes.
* **Real Answer**: The bone-formation niche is enriched for COL1A1, SPP1, SPARC, BGLAP, and IBSP.
* **Why this demonstrates the capability**: This case demonstrates clustering-based inference and comparative differential analysis. The agent must identify an unsupervised group (niche) and derive a statistical signature (markers) that defines its unique characteristics relative to the rest of the data.
---
**[Case 3]**
* **Initial Environment**: A longitudinal or multi-condition dataset is provided with pre-annotated groups. The agent has access to statistical comparison tools in Python.
* **Real Question**: How does the proportion of 'Injured' cells relative to 'Healthy' cells change across the 12-hour, 24-hour, and 48-hour time points?
* **Real Trajectory**: Filter the dataset for the relevant sub-populations; aggregate the cell counts for each category at each temporal index; compute the percentage of 'Injured' cells relative to the total for each time point; identify the trend (e.g., peak at 24h); report the final distribution.
* **Real Answer**: The proportion of 'Injured' cells is 15% at 12h, 45% at 24h, and 30% at 48h.
* **Why this demonstrates the capability**: The agent performs distributional comparison over a specific metadata index (time). This shows the ability to conduct descriptive trend analysis and derive comparative metrics from structured partitions of a larger dataset.

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

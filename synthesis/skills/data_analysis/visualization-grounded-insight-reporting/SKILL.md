---
name: visualization-grounded insight reporting
description: Use this skill when the user wants the agent not only to compute but also to present the result clearly with charts or report-style insights. Trigger it for requests such as “make it create a figure and explain it,” “make it summarize the chart,” “make it turn analysis into clear takeaways,” or “make it produce a report from the data.” Use this especially when a high degree of text-chart consistency is required—preventing cases where the text and graph don't match. Plain-language examples: “Give me a question where it has to plot and explain,” “make it write the key insights after the graph,” “make it present the findings, not just the number,” or “ensure the text directly proves the point using the chart.”
---

# Skill: visualization-grounded insight reporting

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability is the ability to translate analytical outputs into human-readable narratives that are bi-directionally aligned with visual evidence (charts/figures). It emphasizes 'writing-time evidence construction'—an interleaved generation paradigm where narrative claims and visualizations are produced co-dependently to ensure strict 'Text-Chart Consistency' and 'Informative Depth.' The agent must go beyond surface-level descriptions (e.g., merely stating axis labels) to generate decision-oriented insights grounded in the specific patterns, anomalies, and statistical distributions revealed by the visualization.
* **Dimension Hierarchy**: Agentic Execution & Communication->Result Communication->visualization-grounded insight reporting

### Real Case
**[Case 1]**
* **Initial Environment**: A dataset containing global life expectancy, infant mortality, and historical records for various countries and regions. A data analysis sandbox with plotting libraries is available.
* **Real Question**: Why do women live longer than men? Create a data-driven report exploring the global and historical drivers of this phenomenon.
* **Real Trajectory**: Plan a hierarchical outline covering the global longevity gap, regional patterns, and drivers like infant mortality. Begin writing the introduction; pause to request a world map of the life expectancy gap to 'set the scene.' Use the generated map to identify 'Eastern Europe' as a high-gap region in the text. Transition to the 'Drivers' section; request a side-by-side bar chart of infant mortality by sex. Use the visual evidence that 'male bars are consistently higher' to synthesize the insight that biological vulnerability in infancy is the primary driver. Ground subsequent claims about adult mortality by requesting a violin plot and noting the 'blue violin (female) is positioned lower,' confirming lower mortality rates across all regions.
* **Real Answer**: A text-chart interleaved report where every visual (World Map, Regional Bar Chart, Infant Mortality Plot) directly anchors a corresponding analytical segment (Regional Disparity, Biological Foundations).
* **Why this demonstrates the capability**: This demonstrates 'writing-time evidence construction.' The agent does not generate all text first or all charts first; it interleaves them so the narrative is conditioned on the actual visual output, achieving 1:1 text-figure alignment and high informational depth.
---
**[Case 2]**
* **Initial Environment**: A dataset regarding global energy access (electricity and clean cooking) and CO2 emissions per capita across different GDP levels.
* **Real Question**: Analyze the dual energy crisis of emissions and inequality in the global energy landscape.
* **Real Trajectory**: Draft an outline for the 'Energy Injustice' section. Request a chart comparing electricity access vs. clean cooking access. Upon receiving the chart, perform 'Deep Quantitative Interpretation': instead of just listing numbers, observe that the 'clean cooking transition is lagging behind electrification' in the visual. Continue to the 'Emissions' section; request a scatter plot of GDP vs. CO2. Identify and describe high-income, high-emission outliers directly from the dots in the figure to prove that industrial efficiency, not just income, drives local emissions.
* **Real Answer**: An analytical report that turns visual patterns (like the gap between two types of energy access) into decision-oriented takeaways regarding policy lag.
* **Why this demonstrates the capability**: It illustrates 'Decision-oriented Insight Depth.' The agent identifies that the global average is a 'misleading abstraction' by pointing to the specific regional spreads in the chart, proving it can synthesize system-level stories rather than isolated comments.

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

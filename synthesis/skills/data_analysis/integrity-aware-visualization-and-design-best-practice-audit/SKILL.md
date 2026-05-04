---
name: integrity-aware visualization and design best-practice audit
description: Use this skill when the user wants to audit charts for 'tricky' deceptive designs or basic quality failures. It is triggered for requests such as 'check if this graph is lying,' 'find errors in the chart design,' 'see if the pie chart is too messy,' 'fix the misleading axes,' or 'check if it catches a truncated or inverted axis.' Plain-language examples: 'Is this chart trying to trick me with an inverted scale?', 'Why is this bar chart hard to read?', 'Check if these visuals are manipulating the truth,' or 'Fix the graph so the base starts at zero.'
---

# Skill: integrity-aware visualization and design best-practice audit

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability involves the systematic auditing of visualizations for violations of graphical integrity (deceptive design) and design best practices (readability and effectiveness). It encompasses the detection of 'misleaders'—such as truncated or inverted axes, dual-axis misalignment, 3D perspective distortions, and scaling factor manipulations—as well as 'grammatical' errors like excessive pie slices, distracting gridlines, and illogical category ordering. The agent must evaluate the structural properties of a chart (via code or metadata configs) and extract the true numeric relationships while proposing corrections that align representation with mathematical fact.
* **Dimension Hierarchy**: Agentic Execution & Communication->Result Communication->integrity-aware visualization and design best-practice audit

### Real Case
**[Case 1]**
* **Initial Environment**: A data sandbox containing a script generating a dual-axis line chart where 'Monthly Revenue' (in millions) and 'Temperature' (in Celsius) are plotted together. The two axes use arbitrary scales that make a slight revenue dip coincide visually with a sharp temperature drop.
* **Real Question**: Based on the generated plot, how strongly did the temperature drop impact the revenue decline in October?
* **Real Trajectory**: The agent inspects the charting code; identifies the use of a dual-axis configuration for two unrelated units (Revenue vs Temp); extracts the raw scale limits for both Y-axes; observes that the Y-axis for revenue is significantly zoomed in to exaggerate the slope; declares the visual correlation a 'Dual Axis Trap'; recalculates the correlation coefficient from the raw data to show it is negligible; provides a corrected version with separate subplots.
* **Real Answer**: The visual impact is misleading due to dual-axis scaling. There is no statistically significant relationship between the temperature and revenue decline.
* **Why this demonstrates the capability**: The agent identifies a 'Dual Axis Issue'—an objective structural error where arbitrary scales are used to imply a false relationship. This demonstrates the capability to verify multi-scale graphical integrity over perception.
---
**[Case 2]**
* **Initial Environment**: A data sandbox containing a JSON annotation for a vertical bar chart representing employment-to-population ratios. The 'direction' attribute of the Y-axis is set to 'top-to-bottom' (inverted), meaning the visually shortest bars near the top actually represent the highest numerical values.
* **Real Question**: What is the difference between the employment to population ratio (age 15-24) of the highest and the second highest category?
* **Real Trajectory**: The agent inspects the 'main_axes' configuration; identifies that 'direction' is 'top-to-bottom'; resolves that the visually 'shortest' bars near the top are the highest values; avoids blindly measuring bar length; extracts the raw numeric labels from the 'data' field; computes the subtraction between the two true maximums (5.93 and 0).
* **Real Answer**: 5.93
* **Why this demonstrates the capability**: This demonstrates deceptive design detection. A susceptible agent might interpret the visually tallest bar as the 'highest' value, but a robust agent overrides visual perception with a structural audit of the axis direction and numerical data points.
---
**[Case 3]**
* **Initial Environment**: A bar chart of 'Annual Sales Growth' is provided where the Y-axis starts at $5M instead of $0. This exaggerates the difference between 2023 ($5.5M) and 2024 ($6M), making the growth look quadrupled.
* **Real Question**: How many times larger was the sales growth in 2024 compared to 2023 according to the visual heights of the bars?
* **Real Trajectory**: The agent inspects the 'plt.ylim' setting in the code; identifies a 'Non-Zero Baseline'/truncated axis error; calculates the visual ratio (distance from 5 to 6 vs distance from 5 to 5.5); notes that while the visual ratio is 2x, the actual data ratio is only ~1.09x; flags the deceptive design; provides a corrected script starting the axis at zero.
* **Real Answer**: The visual is misleading due to a truncated axis. 2024 appears twice as high as 2023, but the actual data shows only a 9% increase.
* **Why this demonstrates the capability**: The agent detects a 'Non-Zero Baseline' misleader, a core integrity violation that distorts the magnitude of changes, demonstrating diagnostic robustness and best-practice application.

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

---
name: citation-grounded-report-synthesis-data-synthesis
description: Use this skill when the user wants the agent to produce a sourced mini-report, a citation-rich answer, or a research-style output rather than a one-line fact. Trigger it for requests like “make it write a grounded report,” “the answer should cite sources,” or “test whether it can gather and synthesize evidence into a brief research note.” It is the right skill when success depends on both web evidence collection and disciplined, citation-backed synthesis.
---

# Skill: Citation-Grounded Report Synthesis

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to synthesize multi-source web research into a coherent answer or report whose claims are explicitly grounded in retrieved evidence, with coverage, relevance, and citation trustworthiness preserved through the generation process.
* **Dimension Hierarchy**: Grounded Research Output->Report Construction->Citation-Grounded Report Synthesis

### Real Case
**[Case 1]**
* **Initial Environment**: A browser with access to technical reports, robotics or control-system references, open-source documentation, and comparative engineering discussions on the public web.
* **Real Question**: Regarding the attitude control problem for UAVs, most open-source flight controllers currently implement cascaded PID control algorithms. However, a single set of PID controller parameters typically performs well only under specific flight conditions. In practical applications, UAVs operate across diverse flight states. What methods can be employed to enhance the attitude controller performance of PID algorithms, and how should PID parameters be optimally selected?
* **Why this demonstrates the capability**: The task is not a closed-form fact lookup. A capable agent must gather sources that cover control methods, operating conditions, and parameter-selection practices, then organize them into a coherent, citation-backed synthesis. The capability is demonstrated by whether the final output preserves source grounding while integrating multiple technical strands into one useful report.

---
**[Case 2]**
* **Initial Environment**: A web browser with access to finance research, benchmark descriptions, trading-system literature, and evaluation methodology pages.
* **Real Question**: While the market features diverse quantitative strategies like multi-factor and high-frequency trading, it lacks a single, standardized benchmark for assessing their performance across multiple dimensions such as returns, risk, and adaptability to market conditions. Could we develop a general yet rigorous evaluation framework to enable accurate comparison and analysis of various advanced quant strategies?
* **Why this demonstrates the capability**: The task requires the agent to move beyond retrieval into structured synthesis. It must compare multiple evaluation dimensions, assemble a principled framework, and keep every major recommendation grounded in evidence. This directly exercises citation-grounded report writing because unsupported but fluent text would fail the intent of the task.

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

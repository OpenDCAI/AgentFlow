---
name: bridge-based-multi-hop-reasoning-data-synthesis
description: Use this skill when the user wants 'connect the dots' questions, 'multi-hop' questions, or cases where one clue leads to another through a shared person, place, topic, or concept. Trigger it for natural-language requests like 'make the answer require hopping across articles' or 'force the model to follow a shared thread across docs'. This skill targets bridge-based reasoning rather than plain slot concatenation.
---

# Skill: Bridge-Based Multi-Hop Reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to answer by traversing a bridge entity or bridge topic that links separate pieces of evidence across documents. The agent must not only collect multiple facts, but explicitly use the shared bridge to connect them into a reasoning chain.
* **Dimension Hierarchy**: Multi-Source Evidence Composition->Cross-Document Synthesis->Bridge-Based Multi-Hop Reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A bounded news corpus containing one article about the Federal Reserve raising interest rates after booming home prices and another article about future Federal Reserve rate decisions depending on incoming economic data. The shared bridge entity is the Federal Reserve.
* **Real Question**: Does the article from Fortune suggest that the Federal Reserve’s interest rate hikes are a response to past conditions, such as booming home prices, while The Sydney Morning Herald article indicates that the Federal Reserve’s future interest rate decisions will be based on incoming economic data?
* **Real Answer**: Yes
* **Why this demonstrates the capability**: The answer emerges only after the agent notices that both articles talk about the same bridge entity and then compares the two bridged claims. Neither article alone settles the combined question. This is a canonical bridge-based multi-hop reasoning case.
---
**[Case 2]**
* **Initial Environment**: A bounded article set about folklore, U.S. geography, and state capitals. The query links the canonical age needed for a Groundhog Day predictor to the state containing the U.S. capital, requiring multiple retrieved facts and an intermediate reasoning bridge.
* **Real Question**: How many years earlier would Punxsutawney Phil have to be canonically alive to have made a Groundhog Day prediction in the same state as the US capitol?
* **Real Answer**: A numeric answer derived by combining the predictor’s canonical start date with the state-capital bridge and a year-difference calculation.
* **Why this demonstrates the capability**: This case shows that multi-hop reasoning often combines bridging with a follow-on computation. The agent must follow the shared thread across articles before it can even set up the final calculation. The bridge is therefore the structural backbone of the reasoning path.

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

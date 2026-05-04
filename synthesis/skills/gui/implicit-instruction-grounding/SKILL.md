---
name: implicit-instruction-grounding
description: Use this skill when the user wants to test how an Agent handles instructions that are worded differently but mean the same thing (Instruction Unification) or when picking the right button out of many similar options in a single screen (Action Matching). Trigger it for requests like "make the button description vague," "use several different ways to ask for the same thing," "can the agent tell the 'Filter' icon from the 'Sort' icon?" or "test if it knows to pick a size before clicking Add to Cart." This skill ensures the agent maps natural language intents to the correct GUI widgets through semantic understanding, structural siblings, and topological dependencies rather than just matching words.
---

# Skill: implicit-instruction-grounding

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to resolve user intent against GUI elements in complex environments where the mapping is non-literal, redundant, or many-to-one. This involves (1) Semantic Unification (UWIU): the ability to recognize that diverse linguistic command expressions (e.g., 'Reset,' 'Wipe filters,' 'Start again') converge to the same functional target widget; (2) Discriminative Action Matching (MWAM): the ability to correctly isolate the target widget among a dense set of functional neighbors in a single state when multiple distinct tasks are possible; and (3) Topological Relationship Reasoning: understanding sequential dependencies where a terminal action is blocked until a prerequisite widget is configured.
* **Dimension Hierarchy**: GUI Perception and Environment Modeling->Element Grounding->implicit-instruction-grounding

### Real Case
**[Case 1]**
* **Initial Environment**: A filtering pane is open in a fashion shopping application with several active filters currently selected, such as 'Size: Large' and 'Color: Blue'. A single button at the bottom is labeled 'Clear All'.
* **Real Question**: I want to start my search over with no filters.
* **Real Trajectory**: 1. Perform a semantic analysis of the goal 'start over with no filters'. 2. Map this intent to the 'Clear All' button despite the instruction avoiding words like 'Clear' or 'Reset'. 3. Target the coordinates of the 'Clear All' widget and execute a CLICK.
* **Real Answer**: All active filters are removed and the search results refresh to the default state.
* **Why this demonstrates the capability**: This illustrates 'Uni-Widget Instruction Unification' (UWIU). The agent must comprehend that a casual, semantically diverse command ('start over') converges to the same underlying functional UI action as the literal label 'Clear All', demonstrating robustness to natural language variation.
---
**[Case 2]**
* **Initial Environment**: A shopping application category page is open. The top header contains three small icons in a row: a funnel icon (Filter), two arrows icon (Sort), and a heart icon (Wishlist).
* **Real Question**: Sort products by cheapest first.
* **Real Trajectory**: 1. Identify that the current state contains multiple interactive options in the header. 2. Evaluate the instruction 'cheapest first' against the three icons. 3. Reject the 'Filter' and 'Wishlist' widgets as semantically mismatched. 4. Locate the 'Sort' icon and execute a CLICK to open the price ordering menu.
* **Real Answer**: The products are successfully sorted by 'Price: Low to High'.
* **Why this demonstrates the capability**: This demonstrates 'Multi-Widget Action Matching' (MWAM). The agent must distinguish the correct functional widget from a dense cluster of similar neighbors in a single state, ensuring the instruction is precisely discriminated and mapped to the right action.
---
**[Case 3]**
* **Initial Environment**: A pizza ordering screen is open. The 'Add to Basket' button is visible at the bottom, but the 'Choose Size' radio buttons (Small, Medium, Large) are all currently unselected.
* **Real Question**: Add the large pizza to my basket.
* **Real Trajectory**: 1. Analyze the instruction 'Add the large pizza'. 2. Identify that the 'Add to Basket' button is functionally dependent on the size selection. 3. Locate the 'Size' radio group and click the 'Large' option first. 4. Only after the state change is verified, click the 'Add to Basket' button.
* **Real Answer**: A large pizza is successfully added to the cart.
* **Why this demonstrates the capability**: This demonstrates 'Action Topology Reasoning'. The agent must understand the sequential dependency (pre-conditions) between widgets in a single state, prioritizing the logical precursor over the terminal command mentioned in the instruction to avoid task failure.

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

---
name: long-horizon-composite-execution
description: Use this skill when you have a big task that needs many steps to finish, like a long-term plan or a complex project. Trigger it for requests like “follow this long list of steps,” “help me reproduce this bug from the report,” “do a long sequence of chores across different screens,” or “figure out how to finish this multi-step task even if the instructions are messy.” It helps the agent group steps into clusters, look up help in manuals or wikis, and use expert shortcuts like commands to make sure the whole long plan works without getting lost.
---

# Skill: long-horizon-composite-execution

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to execute and verify complex GUI workflows by decomposing high-level, potentially underspecified goals into a structured sequence (DAG) of essential milestones, often requiring the integration of external domain knowledge (RAG). The agent must maintain temporal and semantic consistency over extended interactions—exceeding 30 discrete steps—while employing 'Reliability-First Shortcut Logic' to substitute error-prone physical interactions with direct programmatic commands (e.g., console commands) where permitted. It utilizes hierarchical step-clustering to prevent context decay and employs continuous causal reflection to bridge the gap between initial unstructured intent and terminal success verification.
* **Dimension Hierarchy**: Goal-Directed GUI Workflow Execution->Verified Task Completion->long-horizon-composite-execution

### Real Case
**[Case 1]**
* **Initial Environment**: A web browser is open at the home page of a major e-commerce platform (e.g., Amazon). The agent is logged in and the landing page shows various categories.
* **Real Question**: Search for an 'Omron blood pressure monitor' on Amazon, filter the results by 4+ stars and Prime eligibility, compare the top 3 models based on customer reviews, and add the best one to the cart.
* **Real Trajectory**: 1. Type 'Omron blood pressure monitor' in the search bar and press Enter. 2. Locate the 'Customer Reviews' filter on the sidebar and select '4 Stars & Up'. 3. Find the 'Prime' checkbox in the filter section and activate it. 4. Iterate through the top 3 results, opening each product page to scan the review distribution (e.g., clicking the '85% 5-star' button to expand detailed feedback). 5. Evaluate the '24-hour memory' and 'user-friendliness' mentions in the reviews for each model. 6. Select the model with the highest positive frequency, return to its page, and click 'Add to Cart'.
* **Real Answer**: The Omron 10 Series monitor is added to the cart after a 12-step comparison and filtering workflow.
* **Why this demonstrates the capability**: This case requires maintaining a 10+ step interaction horizon where early filtering actions (4+ stars) and deep-page extraction (review comparisons) directly constrain the final terminal action. The agent must successfully navigate from a broad search state to a highly specific purchase state without losing the 'top 3 models' comparison context, exhibiting long-horizon consistency.
---
**[Case 2]**
* **Initial Environment**: A sandbox game environment (e.g., Minecraft) is open at the main menu. The agent has access to a technical wiki or knowledge base.
* **Real Question**: Reproduce this reported crash: 'Game crashes when opening the survival inventory while under both Invisibility and Glowing effects.'
* **Real Trajectory**: 1. Launch the game in the specific version mentioned in the report (e.g., 24w37a). 2. Create a new creative world to ensure access to all entities. 3. Open the chat console and execute a command to apply the 'Invisibility' effect. 4. Execute a second command to apply the 'Glowing' effect. 5. Open the survival inventory to trigger the entity rendering. 6. Observe the environment for a crash or terminal error state.
* **Real Answer**: The game client crashes immediately upon opening the inventory with both effects active, successfully reproducing the reported bug.
* **Why this demonstrates the capability**: This case demonstrates 'Workflow Reconstruction' and 'Substitutive Command Logic.' The agent must resolve an unstructured natural language report into a technical sequence, using commands (shortcuts) to bypass the unreliability of manual item searching or potion brewing. It proves the ability to execute long-horizon plans where technical accuracy and specific order-of-operations are critical for outcome verification.

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

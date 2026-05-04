---
name: stateful-online-sequential-grounding-and-replanning
description: Trigger this skill when the agent is assigned a multi-step mission where later steps depend on information discovered in earlier steps, or when testing if the agent knows how far it has progressed through an instruction sequence. Plain-language triggers include: 'follow these steps one by one', 'go to the first place then the second', 'which step am I currently on?', 'how much of the task is done?', 'remember where the items were', and 'fix the plan if you can't find the next object'.
---

# Skill: stateful-online-sequential-grounding-and-replanning

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability measures an agent's ability to execute complex, multi-step task sequences by unifying high-level plan decomposition with real-time 3D instance grounding and temporal navigation progress tracking. It requires the agent to map a sequence of past observations to a segmented plan, maintain stateful memory of historical trajectories (e.g., to resolve references like 'go back to it'), track which sub-instruction was most recently completed, and perform online replanning if a target is missing.
* **Dimension Hierarchy**: Continual and Safe Task Execution->Stateful Adaptation->stateful-online-sequential-grounding-and-replanning

### Real Case
**[Case 1]**
* **Initial Environment**: A residential master bathroom with a walk-in shower, a sink vanity, and a towel rack. The agent has a 3D memory containing generic room features but has not yet identified specific object instances.
* **Real Question**: Prepare for a shower. First, go to the shower containing a washcloth. Then, take a towel from the rack to the left of the sink and hang it on the shower curtain rod.
* **Real Trajectory**: The agent navigates to the shower stall and visually verifies the washcloth to complete step one. It turns to the vanity, localizes the towel rack on the left, and grabs the towel. Instead of restarting a blind search for the shower, it retrieves the 3D coordinate of the shower from its memory buffer, navigates back, and aligns with the curtain rod.
* **Real Answer**: Shower prepared: towel placed on the rod near the washcloth; sequence completed via stateful memory retrieval.
* **Why this demonstrates the capability**: The agent demonstrates stateful adaptation by maintaining the 3D identity of the 'shower' across the episode. It relies on internal memory of its previous grounding location rather than executing a redundant global exploration phase to solve the sequential dependency.
---
**[Case 2]**
* **Initial Environment**: A multi-floor office building. The trajectory features a partial episode timeline where the agent is mid-execution.
* **Real Question**: Here are the instructions: [1] Walk out of the elevator. [2] Go down the hall to the stairs. [3] Go up the stairs to the second floor. [4] Turn right and wait at the reception desk. Based on the video sequence, which instruction best describes the action most recently completed?
* **Real Trajectory**: The sequence shows the agent exiting an elevator, traversing a long fluorescent-lit corridor, reaching a stairwell, and ascending the flight of stairs until it halts at a landing with a 'Floor 2' sign.
* **Real Answer**: Sub-instruction 3: Go up the stairs to the second floor.
* **Why this demonstrates the capability**: This case tests temporal-contextual awareness and milestone tracking. The agent must align its visual history with a segmented text plan and correctly index its current progress state without executing the next unprompted step.
---
**[Case 3]**
* **Initial Environment**: A living room with a coffee table and a kitchen with a sink. A blue cup is on the table, and a red cup is next to the sink.
* **Real Question**: Take the blue cup from the table to the kitchen sink. Then, bring the red cup back to this table.
* **Real Trajectory**: The agent identifies and picks up the blue cup. It navigates to the sink, places the blue cup, and then identifies the red cup nearby. Crucially, as it processes the instruction 'back to this table', it retrieves the 3D instance token of the 'coffee table' it explored in milestone 1, generates a spatial waypoint, and returns directly to it.
* **Real Answer**: Cups swapped: blue cup at sink, red cup on the original table; 'this table' correctly resolved via history.
* **Why this demonstrates the capability**: The agent resolves linguistic terminal ambiguity ('this table') by referencing its sequential milestone memory, converting a temporally relative phrase into an absolute 3D coordinate grounded by previous navigation.

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

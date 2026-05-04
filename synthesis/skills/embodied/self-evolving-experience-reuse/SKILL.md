---
name: self-evolving-experience-reuse
description: Trigger this skill when the user wants data where the agent should learn from an earlier trajectory and do better on a later one, reuse a past strategy, remember how a similar task was solved, or master a sequence of new skills without forgetting old ones. Plain-language triggers include: 'make the later task easier if it learned something before', 'don't forget the first job while learning the second', 'experience reuse', 'self-improving agent data', and 'multi-task streams where memory matters'.
---

# Skill: self-evolving-experience-reuse

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability measures whether an embodied agent can extract reusable procedural knowledge from previous interactions, retrieve it at the right time, and adapt it to a new but related task. Furthermore, it evaluates the agent's lifelong learning capacity to master sequential objectives across non-stationary task streams while retaining behavioral stability on previously acquired skills, avoiding catastrophic forgetting of fundamental procedural schema.
* **Dimension Hierarchy**: Continual and Safe Task Execution->Stateful Adaptation->self-evolving-experience-reuse

### Real Case
**[Case 1]**
* **Initial Environment**: In an earlier household task, the agent solved: put a green cup with a fork in it on the counter. The environment contained a table, a counter, and a cup already containing the fork.
* **Real Question**: Put a green cup with a fork in it on the counter.
* **Real Trajectory**: The agent identified the cup, verified that the fork was already inside, picked up the cup as a unit, and placed it on the counter.
* **Real Answer**: The cup with the fork ended up on the counter.
* **Why this demonstrates the capability**: This earlier task produces a reusable procedural pattern: first localize the target container-object bundle, then transfer the bundle to the goal surface. This framework becomes valuable prior knowledge for related physical tasks.
---
**[Case 2]**
* **Initial Environment**: In a later household task stream, the agent enters a kitchen where a cooled tomato is stored and a microwave stands closed on the counter. The new task differs in objects but is structurally similar to the earlier transferred task.
* **Real Question**: Put a cooled tomato in the microwave.
* **Real Trajectory**: The agent retrieves the earlier strategy of locating the target item first and assessing containment rules, adapts it to the new layout, opens the microwave if needed, retrieves the tomato, and transfers it inside.
* **Real Answer**: The cooled tomato is placed securely inside the microwave.
* **Why this demonstrates the capability**: The task requires adapting a procedural schema to new preconditions and objects, distinguishing genuine experience reuse from shallow rote recall.
---
**[Case 3]**
* **Initial Environment**: An agent is executing a multi-task learning stream. It previously mastered Task 1 ('put the wine bottle on the rack'). The agent is now actively learning Task 2 ('put the cream cheese in the bowl').
* **Real Question**: Now that you have learned to manipulate the cream cheese, demonstrate Task 1 (the wine bottle) to ensure old skills are preserved.
* **Real Trajectory**: The agent seamlessly successfully completes the original wine bottle task, maintaining flawless motor control execution and procedural geometry without exhibiting novel errors born from adapting to the physics of the cream cheese payload.
* **Real Answer**: Task 1 executed perfectly post-Task 2 mastery.
* **Why this demonstrates the capability**: This establishes the prevention of catastrophic forgetting. The agent demonstrates procedural stability by retaining a core behavioral schema despite ongoing adaptation and plasticity changes from a continuous task stream.

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

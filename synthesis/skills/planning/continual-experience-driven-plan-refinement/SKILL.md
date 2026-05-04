---
name: continual-experience-driven-plan-refinement
description: Use this when you want an agent that accumulates experience across a series of tasks to improve its success, or when an agent must use past 'Thought Patterns' to figure out complex or vague intents. Trigger it for requests like 'learn from your previous attempts', 'suggest some gear for an occasion based on past experience', 'I am not sure what I need but I want to start a new hobby', or 'distribute memory units across different agents based on their roles.'
---

# Skill: continual-experience-driven-plan-refinement

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to perform test-time evolution and experience reuse by retrieving, integrating, and updating strategic reasoning patterns or distilled 'Thought Templates' from a continuous stream of task trajectories. It involves an abstract pattern-matching loop to resolve vague human intents, adapt to new variations of past tasks, and refine procedural strategies avoiding known historical failures.
* **Dimension Hierarchy**: Open-World Real-World Planning->Self-Evolving Strategic Planning->continual-experience-driven-plan-refinement

### Real Case
**[Case 1]**
* **Initial Environment**: A household simulation environment where an agent possesses a long-term memory of past navigation and pick-up tasks. The agent has previously completed a task to 'Put a chilled tomato from the fridge into the microwave' which involved locating the fridge, retrieving the item, and navigating to the kitchen appliance.
* **Real Question**: Put a green cup with a fork inside it on the kitchen counter.
* **Real Trajectory**: 1. Think: Apply the 'Locate-Retrieve-Move-Place' strategy from the tomato task. 2. Refine: Retrieve the fridge-to-microwave sequence but swap 'microwave' for 'counter' and 'tomato' for 'cup'. 3. Act: Find the green cup on the table; find the fork; place fork in cup; move to the kitchen; place on counter.
* **Real Answer**: Task successfully completed by reusing the navigation-placement decomposition strategy.
* **Why this demonstrates the capability**: This case demonstrates experience reuse where the agent does not merely solve a task in isolation but retrieves a procedural 'how-to' strategy from a previous, semantically distinct task (tomato) to solve a new one (cup/fork). The agent reuses the macro-level planning structure, significantly reducing the search cost for sub-goals.
---
**[Case 2]**
* **Initial Environment**: A symbolic reasoning environment for mathematical problem solving. The agent has a memory bank containing a failed trajectory for solving '2x^2 - 5x + 1 = 0' where it initially attempted a simple factorization that failed before correctly applying the quadratic formula.
* **Real Question**: Solve the equation 5x^2 - 1x + 7 = 0.
* **Real Trajectory**: 1. Think: Identify this as a quadratic equation task. 2. Refine: Retrieve the previous record; note the 'Factorization Failed' reflection tag to avoid that path. 3. Act: Directly apply the quadratic formula using the coefficients [5, -1, 7].
* **Real Answer**: x = (1 ± i√139) / 10
* **Why this demonstrates the capability**: This illustrates the 'Think-Act-Refine' loop's ability to learn from negative feedback. By recognizing the task structure and the specific failure boundary from its history, the agent avoids a 'stuck loop' and moves directly to the optimal strategy, demonstrating procedural refinement.
---
**[Case 3]**
* **Initial Environment**: A multi-agent recommendation environment where the Manager Agent has access to a 'Thought Pattern' repository (Experience Memory). The user provides a query with a 'Usage Scenario' but an ambiguous product scope.
* **Real Question**: Can you suggest some blouses for a gathering with friends? I'm not sure about the specific wearing scene.
* **Real Trajectory**: 1. [Pattern Matching]: Strategic retrieval identifies the 'Ambiguous Demand' thought pattern. 2. [Phased Planning]: Decomposes the goal into Phase 1 (Knowledge acquisition for gathering styles) and Phase 2 (Targeted recommendations). 3. [Phase 1 Execution]: Identifies 'Casual' and 'Semi-formal' as common gathering subsets. 4. [Phase 2 Execution]: Retrieves items for 'Casual Blouses' and 'Semi-formal Blouses' separately.
* **Real Answer**: Recommended List 1 (Casual Blouses for relaxed hangouts); Recommended List 2 (Semi-formal Blouses for dinner gatherings).
* **Why this demonstrates the capability**: The agent leverages experience-driven schemas to transform ambiguous or multifaceted human intents into structured plans. Instead of a 'flat' planning failure on a vague prompt, the agent uses distilled memory to execute a hierarchical intent-to-attribute conversion.

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

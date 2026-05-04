---
name: open-world-object-goal-navigation
description: Trigger this skill when the agent is given a target object's name or a high-level semantic description and must locate it in a vast, unknown environment using logical deduction and semantic object clustering. Plain-language triggers include: 'find the object from the description,' 'go search for the remote based on what is usually nearby,' 'use common sense to figure out which room to check next,' 'open-world object search,' 'no hand-holding instructions,' and 'make the robot locate the described thing by itself.'
---

# Skill: open-world-object-goal-navigation

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability evaluates an agent's proficiency in performing zero-shot Object-Goal Navigation (ObjNav) within large-scale, unstructured environments. It requires the agent to interpret compact semantic descriptions, maintain a robust topological memory of past visual observations, and perform high-level heuristic search planning. The model must strategically balance the exploration of completely unseen territory with the exploitation of known semantic clusters, leveraging object co-occurrence priors (e.g., navigating near sofas when searching for a TV) to prune irrelevant environment zones and drastically minimize path length.
* **Dimension Hierarchy**: Goal-Directed Exploration->Semantic Goal Navigation->open-world-object-goal-navigation

### Real Case
**[Case 1]**
* **Initial Environment**: A large-scale residential layout currently partially explored. The agent has noted a set of couches, a coffee table, and an entrance door forming a 'Living Space' grouping, and a separate cluster revealing a sink and tiles indicating a 'Bathroom'.
* **Real Question**: Search for a television.
* **Real Trajectory**: The agent assesses its navigation mapping. Relying on spatial semantic priors, it recognizes a 'television' possesses an overwhelmingly higher likelihood of co-occurring with the 'couches' rather than the bathroom amenities. It plots a direct return trajectory to the previously logged couches and executes a localized visual sweep, successfully detecting the television mounted on the opposing wall.
* **Real Answer**: Target TV located confidently nearby the sofa in the living room grouping.
* **Why this demonstrates the capability**: The trajectory perfectly highlights semantic prior exploitation. Instead of continuing blind uniform exploration across all available rooms, the agent leverages the structural relationship between objects to drastically narrow down the physical 3D search space.
---
**[Case 2]**
* **Initial Environment**: Aerial observations originate directly above a dense mixed-use city park. Surrounding zones feature playgrounds, walking trails, distant street grids, and forested patches. The agent integrates multiple optical fields to process the landscape.
* **Real Question**: Help me search for a target: category = human, scale = small, description = wearer of a pale green shirt and resting on a bench.
* **Real Trajectory**: The agent decodes the query attributes. It entirely ignores the distant street grids and purely tracks toward the bench structures associated with the playground semantics. Dropping altitude to secure higher optical resolution, it methodically filters human silhouettes matching the size constraint until it visually isolates the explicit hue parameters of the shirt.
* **Real Answer**: Target individual successfully isolated near the playground seating area.
* **Why this demonstrates the capability**: This case validates compound semantic parsing in open-world topology. The target is defined by deep visual attributes alongside semantic category; the agent demonstrates multi-scale control execution to ground descriptive text into a precise environmental coordinate.
---
**[Case 3]**
* **Initial Environment**: A sprawling warehouse setting populated heavily with dozens of structurally identical aisles, shipping crates, and forklifts. A single metallic blue cylinder is hidden among generalized clutter.
* **Real Question**: Locate the pressurized metallic blue cylinder.
* **Real Trajectory**: To mitigate continuous aimless roaming, the agent switches between macro-scale corridor traversal and micro-scale inspection. Recognizing identical cardboard crates hold no high-relevance to metallic pressurized entities, it deliberately prunes these aisles, centering its active exploration around industrial processing nodes and gas panels until the visual profile accurately matches the target.
* **Real Answer**: Target cylinder found near the primary industrial processing manifold.
* **Why this demonstrates the capability**: Demonstrates structural ambiguity suppression. The agent effectively prevents itself from suffering analysis paralysis in endless uniform aisles by implementing dynamic contextual pruning, prioritizing industrial groupings over general shipping materials.

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

---
name: spatial-relation-reasoning
description: Trigger this skill when the agent needs to identify relative positions (left, right, in front of, behind), disambiguate objects using spatial chains, or build a comprehensive natural language semantic scene graph to formalize environment state. Plain-language triggers include: 'what is next to the microwave?', 'which item is between the sofa and table?', 'describe all object relations in this photo', and 'find the car east of the building'.
---

# Skill: spatial-relation-reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability measures the agent's proficiency in inferring discrete and descriptive spatial relationships among entities across single and multi-view perspectives. It involves mapping natural language predicates (on, in, left of, behind) to 3D scene geometry, enabling complex spatial disambiguation and the exhaustive documentation of semantic scene graphs in natural language. It explicitly trains spatial formalization and predicate observation without relying on rigid programmatic solver syntax.
* **Dimension Hierarchy**: Perceptual World Modeling->Static Spatial Grounding->spatial-relation-reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A city street where a building acts as a central landmark. To its east is a storefront with a distinct yellow sign. Multiple vehicles are parked along the curb.
* **Real Question**: What color is the car parked in front of the shop with the yellow signboard?
* **Real Trajectory**: The agent identifies the building, determines the 'east' vector from its current orientation, localizes the storefront with the yellow sign, and targets the specific car within the 'in front of' spatial boundary.
* **Real Answer**: Red.
* **Why this demonstrates the capability**: This illustrates relation-chain disambiguation. The agent must use a sequence of spatial relations to distinguish the targeted vehicle from other cars in the open-world environment.
---
**[Case 2]**
* **Initial Environment**: A living room scene contains a sofa, a coffee table, a lamp behind the sofa, and a chair to the left of the coffee table from the agent’s current viewpoint.
* **Real Question**: Is the chair on the left or on the right of the table?
* **Real Trajectory**: The agent locks onto the table as the local anchor and computes the egocentric spatial difference relative to its camera bearing to ascertain alignment.
* **Real Answer**: Left.
* **Why this demonstrates the capability**: The answer strictly hinges on applying egocentric relational mapping against an established anchor point to evaluate relative spatial positioning.
---
**[Case 3]**
* **Initial Environment**: A robotics lab table viewed from multiple angles. Pink, red, yellow, and green blocks are scattered.
* **Real Question**: Describe every stacking and spatial state relationship between the colored blocks currently on the table to help me plan.
* **Real Trajectory**: The agent systematically audits all visual angles. It notes the red block has nothing on it, the pink block is on the green block, and the yellow block is alone on the table. It lists these observations comprehensively into a structured natural language summary.
* **Real Answer**: Red is clear; Pink is on Green; Green is on the table; Yellow is clear and on the table.
* **Why this demonstrates the capability**: Demonstrates Exhaustive Predicate Verification via natural language representation. The agent conducts total relationship formalization to guarantee comprehension of implicit physical constraints like 'clear' without restricting answers to hard-coded PDDL strings.

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

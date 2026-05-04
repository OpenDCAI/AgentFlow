---
name: depth-and-dimensional-measurement
description: Trigger this skill when the user asks for questions about how far something is, how big it is, which point is closer, how tall a desk is, or whether an embodied agent can estimate physical size from what it sees. Plain-language triggers include: 'near or far,' 'how deep is that point,' 'how tall is the object,' 'measure the desk,' and 'questions about exact size instead of just naming things.'
---

# Skill: depth-and-dimensional-measurement

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability measures whether an embodied agent can infer metric or near-metric physical properties such as depth, height, width, length, and relative distance from visual observations. It requires transforming image evidence into physically meaningful estimates instead of relying on coarse semantic labels alone.
* **Dimension Hierarchy**: Perceptual World Modeling->Static Spatial Grounding->depth-and-dimensional-measurement

### Real Case
**[Case 1]**
* **Initial Environment**: The embodied agent receives a multi-view observation of an office where a desk appears from two slightly different viewpoints. A monitor, keyboard, notebook, and desk edge are visible, and the full desktop surface can be jointly inferred from the views.
* **Real Question**: What is the height of the desk?
* **Real Answer**: Approximately 950 millimeters.
* **Why this demonstrates the capability**: The answer depends on recovering physical scale from image structure rather than naming the desk. The agent must use scene geometry and object proportions to infer an actual dimension. That makes the task a measurement problem, not a recognition problem.
---
**[Case 2]**
* **Initial Environment**: The agent sees an indoor room with two marked pixels, one on the near edge of a bed frame and one on a suitcase farther back in the room. Both points are visible in the same observation, and their apparent size cues are subtle.
* **Real Question**: Which marked point is nearer to the viewer?
* **Real Answer**: The point on the bed frame is nearer.
* **Why this demonstrates the capability**: The agent must compare scene depth at two precise locations. It cannot answer correctly by reasoning only about object categories, because either object could in principle be near or far. The required behavior is explicit depth comparison.
---
**[Case 3]**
* **Initial Environment**: A manipulation workspace contains a rectangular storage box, a ruler, and a mug. The agent is shown enough viewpoints that the box is fully visible while the ruler is only partly visible.
* **Real Question**: What is the length of the box?
* **Real Trajectory**: The agent selects the object boundaries across views, rejects the partially visible ruler as the target, and estimates the long-axis measurement of the box.
* **Real Answer**: 420 millimeters.
* **Why this demonstrates the capability**: The distractor object invites category-based confusion, but the task demands an object-specific geometric estimate. The difficulty comes from converting appearance into dimension under partial clutter. That is precisely what dimensional measurement is intended to test.

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

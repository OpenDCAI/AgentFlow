---
name: 3d-grounding-and-correspondence
description: Trigger this skill when the user wants questions about matching the same thing across two views, locating the exact object described in a scene, finding which spot or region in one view lines up with another view, or making data that tests whether an embodied agent can really connect what it sees from different angles. Common plain-language triggers include: 'same object from another camera,' 'which spot is the same one,' 'find the thing described near the bed,' 'make the robot connect two views,' and 'questions that need lining up one picture with another.'
---

# Skill: 3d-grounding-and-correspondence

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability measures whether an embodied agent can bind a referent in one observation to the same physical entity, point, or region in another observation while preserving 3D identity under viewpoint change. It requires jointly reasoning over visual evidence, camera change, and scene geometry so that the agent does not merely detect a category, but correctly grounds a particular instance or location across views.
* **Dimension Hierarchy**: Perceptual World Modeling->Static Spatial Grounding->3d-grounding-and-correspondence

### Real Case
**[Case 1]**
* **Initial Environment**: An indoor apartment scene is available to the embodied agent through two RGB observations taken from different viewpoints in the same bedroom. A red suitcase stands near the foot of the bed, a black backpack lies beside a chair, and a small lamp sits on a side table.
* **Real Question**: Locate the 3D bounding box of the red suitcase near the bed.
* **Real Answer**: The grounded target is the suitcase instance beside the bed rather than the backpack or the lamp.
* **Why this demonstrates the capability**: The question does not ask for generic object detection. The agent must resolve a language description into a unique physical instance using both object identity and the surrounding spatial cue 'near the bed.' This directly tests whether the agent can bind language to a specific 3D referent rather than selecting any suitcase-like region.
---
**[Case 2]**
* **Initial Environment**: The agent receives Image-1 and Image-2 from the same tabletop workspace after a small camera movement. In Image-1, a point is marked on the front-left corner of a blue box; in Image-2, four candidate labels appear on visually similar corners across several objects.
* **Real Question**: Which labeled point in Image-2 matches the marked point in Image-1?
* **Real Trajectory**: The agent first identifies the object containing the marked point in Image-1, then estimates how the camera moved, then transfers the point to the corresponding surface in Image-2, and finally selects the candidate lying on the same physical corner.
* **Real Answer**: Point A.
* **Why this demonstrates the capability**: The task is impossible to solve by category recognition alone because several corners look alike. Success requires maintaining object identity and local geometry across viewpoint change. That is the essence of cross-view correspondence.
---
**[Case 3]**
* **Initial Environment**: A service robot stands in a living room and first observes a doorway, a wall clock, a framed picture, and a coat hanger lying near the left edge of the floor. It then turns slightly and receives a second observation from a shifted position.
* **Real Question**: In the second view, which region corresponds to the coat hanger mentioned in the first view?
* **Real Trajectory**: The robot anchors on the doorway and picture, infers how the camera rotated, and then searches the floor region that remains consistent with the earlier left-of-picture relation.
* **Real Answer**: The floor region just left of the framed picture and near the doorway edge.
* **Why this demonstrates the capability**: The target is small, partially peripheral, and easy to lose under viewpoint change. The agent must transfer a grounded referent using scene anchors rather than guess based on salience. This reflects the benchmark intent of robust referent tracking across observations.

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

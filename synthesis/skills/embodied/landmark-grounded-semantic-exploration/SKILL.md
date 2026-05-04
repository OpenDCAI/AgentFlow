---
name: landmark-grounded-semantic-exploration
description: Trigger this skill when the user wants city-style or large-space questions that need landmarks, top-down maps, directional clues, and 'connect-the-dots' exploration to resolve ambiguity. Plain-language triggers include: 'use the building and the shop to find the right car,' 'plan a flight for the drone based on the map,' 'questions for big open spaces,' 'not just indoor room search,' and 'identify targets on the satellite view and go check them.'
---

# Skill: landmark-grounded-semantic-exploration

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability measures whether an embodied agent can use global maps, landmarks, chained spatial cues, and large-scale exploration to find the exact region or object needed for an answer in an open environment. It requires cross-scale navigation: interpreting coarse top-down or long-range cues to restrict the search area, followed by local, fine-grained egocentric movement to collect the final evidence.
* **Dimension Hierarchy**: Goal-Directed Exploration->Question-Conditioned Exploration->landmark-grounded-semantic-exploration

### Real Case
**[Case 1]**
* **Initial Environment**: A UAV-style embodied agent starts above a city block. Directly south is a large building, and east of that building is a shop with a yellow signboard. Two different cars are visible in the wider area.
* **Real Question**: There is a building to the south of you. To the east of the building is a shop with a yellow signboard. Please tell me what color is the car parked in front of the shop.
* **Real Trajectory**: The agent first verifies the southern building, travels to its east side, locates the yellow-sign shop, narrows attention to the car in the frontal parking position, and then inspects color.
* **Real Answer**: Red.
* **Why this demonstrates the capability**: The question is intentionally ambiguous without the landmark chain. The agent must use landmark grounding to filter the candidate area before doing local perception. This matches the intended long-horizon city exploration pattern.
---
**[Case 2]**
* **Initial Environment**: The agent begins at a mid-altitude viewpoint over a commercial parking district where a named store, a regional lot, and several connecting lanes are visible but small. The lot contains multiple vehicles and suffers from partial occlusion from street trees.
* **Real Question**: How many cars are parked in the main parking lot?
* **Real Trajectory**: The agent first identifies the correct lot boundary globally by its landmark cues, descends or moves closer for a finer local view, and then sweeps the area to count only the vehicles inside the intended parking boundary.
* **Real Answer**: Eight.
* **Why this demonstrates the capability**: The challenge is not just counting, but hierarchical spatial reasoning. The agent must first determine which region counts as the target lot and then refine its observation scale to avoid missing small or distant cars that are invisible from the initial high-altitude state.
---
**[Case 3]**
* **Initial Environment**: The agent (operating as an airspace manager) is given a global top-down map of a mixed-use region containing forest edges and industrial warehouses. A drone agent is on standby, awaiting a localized flight path.
* **Real Question**: We have reports of potential fires; please scan the map to plan a route toward the industrial buildings and the northern forest edge, then verify the situation.
* **Real Trajectory**: The agent processes the text to identify semantic target zones, performs pixel-pointing on the global map to extract coordinate waypoints, and dispatches the drone to capture low-altitude verification frames at the industrial zone first, followed by the forest perimeter.
* **Real Answer**: The drone located smoke at the warehouse area, but the forest edge is visually confirmed to be clear.
* **Why this demonstrates the capability**: It highlights the cross-scale leap from a top-down overview or map prior to local embodied verification. The agent successfully decomposes a vague wide-area instruction into structured navigation waypoints, linking coarse regional planning to fine-grained visual confirmation.

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

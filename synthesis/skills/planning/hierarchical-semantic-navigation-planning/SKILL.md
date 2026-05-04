---
name: hierarchical-semantic-navigation-planning
description: Use this when the user provides long-horizon navigation instructions in 3D environments that require following a sequence of landmarks, extracting map coordinates, or navigating based on functional zones and user-lifestyle demands. Trigger it for requests like 'follow the route from the bank to the park', 'I am a graphic designer, find a tidy spot for me to work', 'go to the study and organize my documents', or 'guide the drone over the damaged buildings in the satellite image'.
---

# Skill: hierarchical-semantic-navigation-planning

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to decompose complex, long-horizon navigation instructions into a hierarchical structure of semantic sub-goals (functional zones), landmarks (viewpoint-level cues), and executable waypoints. It leverages a hierarchical scene representation—bridging global layout (zones and connectivity) with local details (object attributes and functionality)—to interpret abstract user demands and lifestyle patterns as explicit navigation trajectories within a 3D environment.
* **Dimension Hierarchy**: Open-World Real-World Planning->Information-Grounded Plan Construction->hierarchical-semantic-navigation-planning

### Real Case
**[Case 1]**
* **Initial Environment**: An aerial drone is positioned in an urban simulated city. The environment contains diverse infrastructure (buildings, GAS signs, billboards, roads). The drone has access to a 3D topological memory graph of previous successful flights in this sector.
* **Real Question**: Start from the blue billboard with 'leartes bank', fly forward, pass the 'GAS' sign, and turn left. Continue flying forward, passing the yellow billboard and the 'Americar' billboard ahead. Continue flying forward and left until you reach the blue billboard with 'leartes bank' and stop.
* **Real Trajectory**: 1. [Landmark Extraction]: Extracts ordered sub-goals: {leartes bank, GAS sign, yellow billboard, Americar billboard, leartes bank}. 2. [Object-Level Reasoning]: Identifies the 'road' and 'sidewalk' as the immediate Object Regions of Interest (OROI). 3. [Exploration & Grounding]: Flies forward, detects the 'GAS' sign. 4. [Memory Retrieval]: Detects a node in its topological graph. 5. [Graph Search]: Uses Dijkstra search on the memory graph to find the shortest action sequence to the final 'leartes bank' landmark.
* **Real Answer**: A sequence of 3D waypoints and low-level actions (Forward, Turn Left, Stop) that traverses all mentioned landmarks.
* **Why this demonstrates the capability**: The agent demonstrates hierarchical planning by decomposing a complex instruction into a symbolic sub-goal sequence (landmarks) and using mid-level reasoning to bridge perception gaps to reach invisible sub-goals.
---
**[Case 2]**
* **Initial Environment**: A household assistant robot operates in a large 3D house with 12 interconnected functional zones. The robot has a profile for a human user who is a Graphic Designer and enjoys a rustic yet modern aesthetic.
* **Real Question**: Walk to the warm hall featuring elegant wooden accents and set the large wooden table with candles and napkins for a lovely dinner ambiance.
* **Real Trajectory**: 1. [Zone Identification]: The agent analyzes the scene overview to identify 'Zone 1' as the multi-functional 'warm hall' with a rustic modern aesthetic. 2. [Viewpoint Retrieval]: Within Zone 1, it retrieves viewpoints with high connectivity to find a gathering space. 3. [View Grounding]: It identifies a specific view containing a 'large wooden dining table' next to a staircase. 4. [Path Planning]: It calculates a path from its current position, through intermediate zone thresholds, to the dining table viewpoint.
* **Real Answer**: Go to the rustic living area (Zone 1) -> Navigate to the central wooden table -> Confirm arrival next to table_1.
* **Why this demonstrates the capability**: This demonstrates hierarchical semantic planning by mapping a high-level user 'demand' (dinner ambiance) to a specific functional zone and then to a fine-grained object (table) based on a hierarchical scene description tree.
---
**[Case 3]**
* **Initial Environment**: An embodied agent is in a multi-floor interior scene. The user is a Lawyer who maintain a habit of early rising and requires a tidy work environment in the study.
* **Real Question**: Please head to the stylish bathroom featuring a round vessel sink; make sure to wipe down the stone countertop and tidy up any items left around the space.
* **Real Trajectory**: 1. [Functional Search]: The agent scans the scene-level description for a 'bathroom' zone. 2. [Attribute Matching]: It filters viewpoints within zone_5 to find the one describing a 'round vessel sink' and 'stone countertop'. 3. [Atomic Execution]: It plans a trajectory that exits the bedroom zone, enters the hallway, and stops at the specific sink coordinates.
* **Real Answer**: Exit Bedroom (Zone 3) -> Enter Hallway -> Enter Bathroom (Zone 5) -> Stop at Vessel Sink.
* **Why this demonstrates the capability**: The agent proves it can navigate using environment semantics and object attributes, extracting the destination from a lifestyle-oriented role simulation and using a hierarchical description to move from global zones to local task objects.

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

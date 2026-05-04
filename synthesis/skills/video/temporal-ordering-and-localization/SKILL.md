---
name: temporal-ordering-and-localization
description: Use this skill when the user asks 'when exactly did the event happen?', 'spot the shot change', 'why did the camera zoom into the face?', 'is this a close-up or a full-body view?', or 'find the boundary where the speaker starts walking'. It is triggered for tasks assessing precise temporal grounding, identifying cinematographic shot scales (like Close-up, Medium, or Full Shot), and parsing the logical relationship between audio/emotional shifts and structural camera transitions across a multi-shot video timeline.
---

# Skill: temporal-ordering-and-localization

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to precisely localize continuous temporal boundaries (onset and offset), classify cinematographic shot scales (Close-up, Medium Close-up, Medium Shot, Full Shot, etc.), and model the structural distribution patterns of sequential milestones across a video timeline. This includes grounding temporal transitions in narrative or emotional flow, identifying discrete cinematography-driven shot boundaries, and formally identifying abstract structural discontinuities where the visual scale reset occurs through intentional editing to emphasize specific speech elements or character gesticulations.
* **Dimension Hierarchy**: Temporal-Spatial Understanding->Temporal Structure Analysis->temporal-ordering-and-localization

### Real Case
**[Case 1]**
* **Initial Environment**: A dashcam video depicting an off-road racing course occupied by multiple vehicles traversing a complex terrain.
* **Real Question**: Based on the video, identify the precise timing interval marking the following event: the trailing vehicle overtakes the leading car.
* **Real Trajectory**: Index the continuous clip to isolate the exact micro-segment where relative velocities result in spatial priority shifting. Mark the precise frame the trailing bumper aligns with the leader (onset at 5.0s) and track the sequence until the overtaker creates a definitive forward gap securely finalizing the merge (offset at 8.2s).
* **Real Answer**: 5.0s - 8.2s
* **Why this demonstrates the capability**: This validates 'High-Granularity Moment Retrieval' by requiring the mapping of ambiguous continuous spatial actions into a highly rigid, numeric start-stop temporal bounding box.
---
**[Case 2]**
* **Initial Environment**: A 10-second narrative sequence beginning with an intense close-up of a character's face in a static, dark internal room, abruptly followed by a rapid-motion exterior street shot.
* **Real Question**: Determine the type of structural temporal gap utilized in this transition and detail its boundary markers.
* **Real Trajectory**: Isolate the sequence boundary anchoring the outgoing static phase at T=4.5s. Detect the immediate, non-blended temporal transposition directly to the chaotic exterior timeline at T=4.6s. Identify this instant kinetic divergence as a 'Smash Cut' transition parsing two disconnected chronological zones.
* **Real Answer**: The transition utilizes a smash-cut mapping the sudden visual boundary change securely at 4.5s, intentionally severing continuous chronological flow to spike narrative velocity.
* **Why this demonstrates the capability**: This exercises 'Structural Edit Boundary Detection'. It confirms the capacity to track timeline consistency and isolate abstract operational discontinuities where temporal flow is intentionally ruptured.
---
**[Case 3]**
* **Initial Environment**: A multi-shot human speech video featuring a talk show host delivering a monologue, transitioning between different camera perspectives based on speech intensity.
* **Real Question**: At what timestamp does the camera transition to a Close-Up (CU) shot to emphasize the speaker's emotional climax, and what was the preceding shot type?
* **Real Trajectory**: Analyze the speaker's vocal pitch and gesticulation frequency. Identify that at T=18.5s, the speaker's tone shifts to 'raised pitch and increased emphasis.' Mark the visual transition from a waist-up 'Medium Shot (MS)' to a head-only 'Close-Up (CU)' at exactly 18.7s. Document the offset of this CU shot at 25.0s as the speaker leans back.
* **Real Answer**: T=18.7s; the preceding shot was a Medium Shot (MS).
* **Why this demonstrates the capability**: This demonstrates 'Cinematographic Shot-Scale Classification' and alignment. The agent must precisely identify the temporal boundary of an edit and classify the visual scale (MS vs CU) while grounding the transition's onset in the multimodal emotional flow of the speech.

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

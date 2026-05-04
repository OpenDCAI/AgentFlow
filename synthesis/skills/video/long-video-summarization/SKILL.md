---
name: long-video-summarization
description: Use this skill when the user wants 'summarize the whole video', 'tell me what happened in the second half', 'explain the development of the situation', 'give the main developments', or when parsing the overarching narrative of fast-paced commercials and trailers. Trigger it when the desired answer must integrate many moments across a long duration into one coherent account, connect the dots between separate events located far apart, or trace the overarching thematic/plot arc of a complex or rapidly edited video.
---

# Skill: long-video-summarization

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to compress long-form or heavily fragmented multi-scene video into a faithful global account and perform high-level narrative reasoning by integrating evidence across distinct temporal segments. This preserves major events, cross-event logical plot progression, and outcomes without collapsing into vague topical language or omitting decisive developments and situational shifts, even amidst rapid pacing.
* **Dimension Hierarchy**: Long-Horizon Reasoning->Global Content Integration->long-video-summarization

### Real Case
**[Case 1]**
* **Initial Environment**: A 100-minute football match video with multiple attacks, substitutions, and momentum swings. The user asks about the second half rather than about one isolated play.
* **Real Question**: What happens in the second half of the game?
* **Real Trajectory**: Segment the second half into major phases, identify turning-point actions, suppress low-impact repetitions, and compose a chronologically ordered summary that preserves the decisive score-changing events.
* **Real Answer**: As the game progressed towards its final stages, Liverpool's offensive pressure gradually intensified. A free kick from Liverpool leading to an own goal in the penalty area later changed the game's momentum, Liverpool once again scored another goal, resulting in a 2-0 victory.
* **Why this demonstrates the capability**: The answer requires broad coverage and selection of high-salience developments across a long interval. This tests whether the agent can preserve temporal progression and outcome while compressing large amounts of video evidence.
---
**[Case 2]**
* **Initial Environment**: A 90-minute cinematic video featuring multiple segments of astronauts preparing for and executing a technical mission. The first 10 minutes establish the mission's scope on Earth, while the final 20 minutes show the execution phase.
* **Real Question**: Why are the men dressed in white space suits walking down a ramp at the beginning of the event from 76.0 to 135.0 seconds?
* **Real Trajectory**: Scan the initial frames to identify the mission context (e.g., preparing for a space mission). Locate the specific temporal window (76s-135s) within the hour-long stream. Correlate the visual of the men on the ramp with the mission goals identified at the very start of the video. Deduce that the action is a procedural prerequisite (pre-launch walk) for the goal established in the long-term context.
* **Real Answer**: They are preparing for a space mission.
* **Why this demonstrates the capability**: This demonstrates 'Within-Event to Global Alignment.' The agent matches a specific, time-localized action at the beginning of a sequence to the overarching narrative goal established in the long-form video profile, proving it can ground reasoning in structural plot intent.
---
**[Case 3]**
* **Initial Environment**: A 120-second cinematic advertisement featuring a woman in a pink dress running through a busy cityscape, transitioning rapidly through multiple high-budget locations like New York's Times Square, an apartment, and a taxi cab.
* **Real Question**: Which classic film shares the same storyline as this fast-paced video? (A) Roman Holiday, (B) The City of Love, (C) The Devil Wears Prada, (D) Before Sunrise.
* **Real Trajectory**: Perform narrative synthesis across rapid scene cuts. First, identify the 'celebrity runaway' archetype in the first 20s. Next, note the cab interaction with a man who doesn't recognize her at 45s. Finally, detect her return to her career at 110s. By correlating this high-density condensed plot to film history, the agent identifies the core escapist romance theme.
* **Real Answer**: Roman Holiday.
* **Why this demonstrates the capability**: This demonstrates 'Cross-Scene Narrative Synthesis' across high-density edits. Bridging rapidly disjointed sequences to extract a unified thematic arc confirms the capability to integrate massive plot gaps into a coherent global scenario.

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

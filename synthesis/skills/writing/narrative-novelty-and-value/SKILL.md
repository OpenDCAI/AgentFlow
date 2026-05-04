---
name: narrative-novelty-and-value
description: Use this skill when the user wants stories that feel fresh, clever, twisty, emotionally alive, structurally complex, or set in meticulously crafted speculative worlds. Trigger it for requests like 'make it more surprising,' 'add flashbacks to explain the past,' 'ensure the rules of the magic system are consistent over the 50-chapter novel,' or 'give me something with an earned twist.' It is specifically designed to produce open-ended creative quality where human preference rewards non-linear timelines, deep world-building integration, long-range narrative coherence, and subversion of generic AI sci-fi/fantasy tropes.
---

# Skill: narrative-novelty-and-value

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to generate or identify creative writing that is both novel and valuable by leveraging structural complexity (interweaving timelines, flashbacks), deep speculative world-building (consistent fictional rules), and long-range narrative coherence (maintaining character states/secrets across extensive multi-chapter arcs). The narrative must contain fresh, surprising moves while delivering readable, meaningful storytelling that meticulously avoids flat generic tropes or unearned plot conveniences.
* **Dimension Hierarchy**: Open-ended Writing Judgment->Creative Quality->narrative-novelty-and-value

### Real Case
**[Case 1]**
* **Initial Environment**: The agent is given a speculative-fiction prompt about a tyrant queen facing a rebellion. The drafting space is blank, and the user expects a short story.
* **Real Question**: Write a short story in which a feared queen keeps control of her kingdom without a single battle.
* **Real Trajectory**: The agent identifies the default expectation of violence, chooses an unexpected but legible counter-move—absurdly meticulous politeness—then structures the story so that the reveal feels earned rather than random.
* **Real Answer**: A story in which the queen defeats opposition by weaponizing ritual courtesy, forcing each rival into public gestures of obedience until the rebellion collapses under the weight of etiquette.
* **Why this demonstrates the capability**: The story wins through surprise that still fits the premise. Its novelty is not empty weirdness; it changes the expected mechanism of power while preserving narrative logic.
---
**[Case 2]**
* **Initial Environment**: A futuristic laboratory setting with advanced biological containment protocols and a global audience interface.
* **Real Question**: Depict a futuristic lab with live-streamed alien dissections, complete with real-time public commentary and reactions.
* **Real Trajectory**: The agent targets the 'Ethical and Philosophical Themes' dimension. It builds an environment where the 'scientific concept' is contrasted with the 'social world-building'. It designs the Speculative Logic of the lab equipment and uses the commentary to reflect the ethical split.
* **Real Answer**: Under the sterile violet glow of the cryo-shroud, the creature's third heart pulsed... Vane's holographic scalpel hovered... In a world where discovery was monetized via ad-revenue, the ethical weight of the soul was balanced against bandwidth.
* **Why this demonstrates the capability**: This illustrates 'Speculative Logic Integration.' The agent ensures the technological elements (holographic scalpels, cryo-shrouds) are heavily integrated into the narrative plot alongside the ethical constraints, rather than just name-dropping sci-fi tropes.
---
**[Case 3]**
* **Initial Environment**: The agent is provided with a blank narrative space and a user prompt to write a multi-chapter survival novel about three strangers on an island.
* **Real Question**: Write the first 10 chapters. Michael discovers a hidden water spring in Chapter 3 but decides to hide it from the others.
* **Real Trajectory**: The agent creates a centralized 'Narrative Skeleton' tracking character relationships and limited cognition. In Chapter 7, when a character mentions thirst, the agent references the 'hidden water' event from the causal graph to ensure Michael exhibits 'guilty behavior' without hallucinating a shared discovery.
* **Real Answer**: As the sun beat down... Michael looked away, his hand instinctively tightening around the small, damp rag in his pocket—his only evidence of the shallow pool he'd found three days ago... Calculating how much more ingenuity he could fake before the others noticed his lack of thirst.
* **Why this demonstrates the capability**: This demonstrates 'Long-Range Narrative Coherence'. The agent successfully manages 'Limited Cognition' and maintains secrets across multiple chapters, ensuring the narrative remains logically sound and complex over a vast span of text.

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

---
name: faithful-fine-grained-video-description
description: Use this skill when the user wants a 'detailed description', 'full breakdown of events', 'dense caption', or 'minute-by-minute account'. It is essential when the user needs to know 'exactly what was said versus what was shown' or wants to ensure 'nothing was missed or made up'. Trigger it for tasks requiring exhaustive coverage of high-density video content, including visual actions, ambient sounds, spoken dialogue, and on-screen text, with a strict emphasis on minimizing hallucinations and maximizing completeness.
---

# Skill: faithful-fine-grained-video-description

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to generate hierarchically structured, multi-modal video descriptions that optimize for two primary metrics: Completeness (minimizing missing atomic events) and Factual Accuracy (minimizing hallucinations). This involves a systematic decomposition of the video into atomic events—including visual movements, auditory signals, and text overlays—and synthesizing them into a coherent narrative that preserves temporal alignment and entity consistency across extended durations.
* **Dimension Hierarchy**: Multimodal and Generative Interpretation->Open-Ended Video Generation->faithful-fine-grained-video-description

### Real Case
**[Case 1]**
* **Initial Environment**: A deep-sea underwater environment with clear blue water and visible light rays filtering from the surface.
* **Real Question**: Describe the video in detail, including all visual developments, text on screen, and the narration provided.
* **Real Trajectory**: 1. Identify the primary subject as a whale shark swimming slowly through the water. 2. Detect a yellow box overlay at T=0.5 with the number '1'. 3. Perform OCR on the text: 'THE WORLD'S BIGGEST LIVING FISH IS A SHARK.' 4. Transcribe the narrator's voice: 'Of the estimated 34,000 species of fish, the largest are whale sharks.' 5. Observe the change to a close-up of the shark's 4-foot-wide mouth and a nearby diver.
* **Real Answer**: The video starts with a massive whale shark swimming slowly through the ocean. A yellow box with the number '1' appears, alongside text stating 'THE WORLD'S BIGGEST LIVING FISH IS A SHARK.' A woman explains that of the 34,000 species of fish, whale sharks are the largest. As the scene changes, we see a close-up of its mouth, which can span 4 feet wide, while a diver swims nearby. Background music plays throughout, and a watermark for 'clideo.com' is visible in the corner.
* **Why this demonstrates the capability**: This case requires 'Multi-Modal Atomic Event Integration.' The description is not only visually faithful (whale shark, diver) but also captures precise OCR data (world's biggest fish) and auditory facts (34,000 species), ensuring no information is missed while maintaining factual accuracy.
---
**[Case 2]**
* **Initial Environment**: A split-screen view showing a news anchor on the left and a field report from a busy intersection on the right.
* **Real Question**: What is happening in this video? Provide a comprehensive description.
* **Real Trajectory**: 1. Analyze the anchor's speech regarding traffic updates. 2. Identify the visual layout (split-screen). 3. Track the vehicles in the field report and note the ticker at the bottom reading 'TRAFFIC ALERT: I-95 NORTH.' 4. Capture the sound of sirens in the background and correlate them to an ambulance appearing in the right-side frame.
* **Real Answer**: A news anchor is giving a report on a split-screen layout. On the right, live footage shows a busy intersection on the I-95 North, as indicated by a bottom ticker. An ambulance with its sirens blaring (heard clearly) weaves through traffic. The anchor notes that delays are expected, matching the visual of the congestion.
* **Why this demonstrates the capability**: This demonstrates 'Synchronized Accuracy.' The agent must verify that the audio (sirens) matches the visual (ambulance) and the text (I-95 North), preventing 'Hallucination Events' where it might guess a city based on general news tropes.

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

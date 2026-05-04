---
name: state-and-attribute-change-tracking
description: Use this skill when you need to know 'if the video looks real', 'if the background is glitching', 'is the motion smooth or choppy?', 'does the person change their appearance mid-video?', or 'how much movement is actually happening?'. It is essential for auditing visual quality, identifying generative AI artifacts like warping backgrounds or flickering subjects, and checking if the dynamic motion matches the expected intensity. Trigger it whenever the user wants a quality check on how natural or consistent a video is, especially for identifying fakes or poorly generated content.
---

# Skill: state-and-attribute-change-tracking

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to audit visual fidelity, perceptual naturalness, and structural consistency across continuous video streams. This involves tracking persistent attribute evolution (e.g., biological decay, material deformation) and conducting rigorous fidelity audits to identify generative or technical artifacts—such as subject flickering, background warping, and temporal motion stuttering. It includes quantifying 'Dynamic Range' to distinguish between static and high-motion content and verifying 'Subject/Background Consistency' to ensure entities and environments maintain structural integrity throughout high-frequency kinetic transitions.
* **Dimension Hierarchy**: Temporal-Spatial Understanding->Dynamic Event Perception->state-and-attribute-change-tracking

### Real Case
**[Case 1]**
* **Initial Environment**: A close-up conditional image of a person holding a spice jar over a cooking pot. The video begins as the interaction starts.
* **Real Question**: Does the video faithfully maintain the identity of the spice jar and the person's hands throughout the pouring motion, or are there visual artifacts?
* **Real Trajectory**: The agent performs an 'Identity Lock' on the spice jar identified in the first frame. It tracks the object as the hand tilts it. The agent then performs a 'Subject Consistency' audit, checking if the jar disappears, morphs into a different object, or if an extra hand is hallucinated to complete the action. It detects that the jar remains stable but notices a slight flickering in the texture of the hand's fingers at T=2.0s.
* **Real Answer**: The video maintains the jar's identity, but a subject consistency violation occurs at 2.0s where the hand's texture briefly flickers and loses structural coherence.
* **Why this demonstrates the capability**: This demonstrates 'Subject Consistency' and 'Artifact Detection'. The agent must ensure that the object from the conditional image persists without corruption during a dynamic interaction, which is a core requirement for high-fidelity video interpretation.
---
**[Case 2]**
* **Initial Environment**: Two separate videos showing horses on a dirt road. One video shows a horse taking a single step, while the other shows a horse galloping forward at high speed.
* **Real Question**: Which video demonstrates a higher Dynamic Range, and what kinetic evidence supports this?
* **Real Trajectory**: The agent analyzes the 'Kinetic Vector Magnitude' in both videos by calculating the pixel-displacement delta of the horse's center-of-mass over the 49-frame sequence. In the first video, the displacement is less than 5% of the frame width. In the second video, the horse traverses 40% of the frame width. The agent also notes the intensity of the dirt being kicked up.
* **Real Answer**: The second video has a significantly higher Dynamic Range because the subject exhibits extensive forward traversal and higher kinetic intensity compared to the relatively static step in the first video.
* **Why this demonstrates the capability**: This illustrates 'Dynamic Range Evaluation'. It tests if the agent can quantify the magnitude of motion and distinguish between low-dynamic (nearly static) and high-dynamic content, avoiding the 'static-video' shortcut common in low-quality streams.
---
**[Case 3]**
* **Initial Environment**: A conditional image of a woman holding a bottle. There are three variations of generated videos: one with a powder explosion, one with flames, and one with water.
* **Real Question**: Does the explosion type in each video consistently follow the semantic attributes established in their respective prompt and initial frame context?
* **Real Trajectory**: The agent first extracts the 'Semantic Seed' from the prompt (e.g., 'flame explosion'). It then monitors the 'Attribute Evolution' of the explosion starting from the bottle. It performs a 'Fidelity Audit' to classify the visual texture of the explosion (liquid vs. gas vs. plasma). It confirms that the 'Flame' video correctly manifests orange-red high-luminance pixels, whereas the 'Water' video incorrectly uses static blue noise.
* **Real Answer**: The flame video correctly aligns with its semantic attributes, but the water video fails the fidelity audit by using untextured blue noise instead of fluid-dynamic water particles.
* **Why this demonstrates the capability**: This demonstrates 'Attribute Alignment and Naturalness'. The agent must verify that the specific type of dynamic change (the explosion) physically matches the intended category and looks natural relative to the source context.

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

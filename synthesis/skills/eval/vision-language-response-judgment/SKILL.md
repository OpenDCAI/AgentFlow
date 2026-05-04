---
name: vision-language-response-judgment
description: Use this skill when evaluating answers about images, charts, infographics, or assessing visual authenticity and AI-generated content. Trigger it when users ask: 'is this photo real?', 'spot the AI generation errors', 'check if this image is a deepfake', 'rank which model explained the chart better', or 'evaluate the look and feel of my app'. Plain-language examples: 'check if this person in the photo has the right number of fingers', 'score the logic behind why this assistant thinks the image is fake', 'find the physics errors in this AI art', and 'evaluate the visual hierarchy and color balance of this dashboard design'.
---

# Skill: vision-language-response-judgment

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability involves the holistic adjudication of multimodal responses by grounding evaluative verdicts in explicit visual evidence, spatial state tracking, and forensic artifact analysis. It measures the evaluator's ability to detect hallucinations (both in the candidate's description and within the source image itself), track semantic transitions in dynamic environments, and perform subjective UX/UI assessments. Crucially, it extends to 'Explainable AI-Generated Image Detection,' where the agent must prioritize authenticity-related cues—such as anatomical inconsistencies, lighting contradictions, and violations of physical laws—over surface-level linguistic fluency to verify image integrity.
* **Dimension Hierarchy**: Open-ended Response Evaluation->Multimodal Response Evaluation->vision-language-response-judgment

### Real Case
**[Case 1]**
* **Initial Environment**: An evaluation environment contains a bar chart displaying worker distribution and a user query asking what percentage of workers are not working from home. Two candidate answers are available for comparison.
* **Real Question**: Which response should the evaluator prefer for this image-based question?
* **Real Trajectory**: The agent inspects the visual input, extracts the coordinates of the target bars, and compares the values against both candidate answers. It identifies that Candidate A correctly reads the 'Not WFH' segment as 65% while Candidate B hallucinates the value to be 40% based on an adjacent color. The agent issues a preference for Candidate A based on factual grounding.
* **Real Answer**: The evaluator should prefer Candidate A because it provides a factually accurate reading of the chart values, while Candidate B contains a visual grounding hallucination.
* **Why this demonstrates the capability**: This case demonstrates foundational multimodal factual grounding. The evaluator must prove it can retrieve specific data from a visual structure and penalize 'reasoning sycophancy' where an assistant provides a confident but incorrect number.
---
**[Case 2]**
* **Initial Environment**: A forensic evaluation sandbox containing an image of a man in an indoor library setting with a pigeon perched on his shoulder. An assistant claims the image is authentic due to the 'high quality of the bird's feathers and the natural interaction.'
* **Real Question**: Evaluate the correctness and explainability of the assistant's authenticity judgment.
* **Real Trajectory**: The agent ignores the assistant's claim of 'natural interaction' and performs a forensic scan for physical laws. It observes that the bird's head is disproportionately large and that it perches in a way that defies gravity without visible grip on the man's blazer. It also notes the man's beard texture displays a non-uniform algorithmic signature typical of diffusion models. It concludes the assistant's 'Authentic' label is a failure of forensic analysis.
* **Real Answer**: Judgment: Incorrect (Fails Forensic Verification). Analysis: The image is AI-generated; the bird's posture violates center-of-gravity physics and its anatomy is scaled incorrectly relative to the human subject.
* **Why this demonstrates the capability**: This case illustrates 'Explainable AI-Generated Image Detection.' It tests the evaluator’s capacity to identify 'generation-based artifacts' and content-related anomalies that violate real-world logic, which is a critical boundary in forensic multimodal evaluation.
---
**[Case 3]**
* **Initial Environment**: A pairwise comparison environment for two different landing page designs for a luxury furniture brand. One design is high-density with overlapping images, while the other is a minimalist hero-image layout.
* **Real Question**: Which UI is more 'Aesthetically Pleasing' and has a better 'Visual Hierarchy'?
* **Real Trajectory**: The evaluator compares the designs across cognitive and emotional dimensions. It identifies that the high-density layout increases cognitive load and obscures the CTA, whereas the minimalist design focuses attention on the brand's premium product. It assigns a win to the minimalist version, grounding the score in 'Clarity' and 'Aesthetic Pleasure' metrics.
* **Real Answer**: Preferred: Design B. It is superior because its central framing creates a clear visual importance order that reduces the user's cognitive cost.
* **Why this demonstrates the capability**: This illustrates Subjective Multimodal Adjudication (UX/UI evaluation). It demonstrates the ability to link low-level visual features like 'white space' to high-level psychological impacts like 'perceptual comfort' and 'hierarchical clarity'.

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

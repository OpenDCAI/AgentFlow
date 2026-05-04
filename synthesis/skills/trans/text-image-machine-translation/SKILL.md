---
name: text-image-machine-translation
description: Use this skill when the user wants to translate text found inside an image (like a photo of a sign, a screenshot, or a damaged manuscript) OR when the user provides noisy text that must be translated by referencing an accompanying image. Trigger it for layman requests like 'translate the text in this picture,' 'decode the ancient script on this stone,' 'read the words in this screenshot,' or 'fix the typos in this description using the picture to ensure the colors match what is actually shown.'
---

# Skill: text-image-machine-translation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform end-to-end multimodal translation by unifying Optical Character Recognition (OCR), visual-spatial contextual reasoning, and cross-linguistic transfer. This capability resolves semantic ambiguities, decodes physical layout constraints, and corrects noisy text-based inputs (like typos) by strictly referencing visual ground-truth items (e.g., surrounding objects, material degradation, and pixel-level attributes).
* **Dimension Hierarchy**: Contextual and Constraint-Aware Translation->Multimodal-Grounded Translation->text-image-machine-translation

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent is provided with an image of a social media post. The user interface features a photo overlay showing a digital TV screen displaying the show 'Friends', a bagel, and some fried potatoes. Chinese colloquial text is overlaid sequentially at the bottom of the interface.
* **Real Question**: Translate all the text in this image into English following the natural reading order.
* **Real Trajectory**: The agent identifies the Chinese characters corresponding to 'Friends', 'Bagel', and 'weird combo'. It cross-references the initial characters '老友记' against the visual evidence of the TV sitcom logo in the background, deducing it is a proper noun (the TV show), not a literal phrase about elderly companions. It then renders a casual English translation.
* **Real Answer**: Friends Bagel Weird combination for lunch Fried shredded potato
* **Why this demonstrates the capability**: This illustrates the integration of text-bounding OCR with explicit visual object grounding. The proper noun's contextual definition depends strictly on referencing the background pixels, isolating the core discrepancy between multimodal translators and basic cascaded text translators.
---
**[Case 2]**
* **Initial Environment**: A translation agent is provided with an image of a young man and an English textual description containing a phonological typo. The image clearly shows the man wearing yellow sneakers on a sidewalk.
* **Real Question**: Translate the following description into Chinese: 'Young man wearing dark glasses, light colored pants, and yellowing snickers.'
* **Real Trajectory**: The agent identifies the source content 'yellowing snickers' and triggers a visual grounding check against the provided image. It observes that while 'snickers' refers to a snack, the visual modality contains 'yellow sneakers' in the corresponding spatial location. The agent resolves the typo as 'sneakers' and translates the attribute as '黄色的运动鞋' (yellow sneakers) to maintain fidelity to the visual evidence.
* **Real Answer**: 年轻人戴着墨镜，穿着浅色的裤子和黄色的运动鞋。
* **Why this demonstrates the capability**: This demonstrates the ability to use visual accompaniment as a ground-truth filter for source-text noise (typos). Without multimodal grounding, a system would literally translate the typo as a 'snack,' resulting in a nonsensical description that violates the real-world visual context.
---
**[Case 3]**
* **Initial Environment**: A high-resolution photograph of a damaged, weathered Roman milestone containing a Latin inscription. The stone bears physical damage and uses heavily abbreviated historical spacing mechanics.
* **Real Question**: Translate the following Latin inscription found on the Roman milestone into English and decode the text.
* **Real Trajectory**: The agent performs an epigraphic scan over the artifact, tracing characters through the weathering. It transcribes valid shapes while denoting physical gaps caused by cracking. It subsequently expands the Latin abbreviations by relying on the circular formatting layout and historical context limits, yielding an accurate archaeological translation.
* **Real Answer**: Translation: [English rendering of the milestone titles]. Date: Circa 220 CE.
* **Why this demonstrates the capability**: This captures the intersection of historical text extraction from physical artifacts and translation workflow. The agent processes material degradation, structural limits, and archaic script formats within an image, encapsulating historical image-based modality resolution.

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

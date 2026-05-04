---
name: interleaved-multimodal-content-composition
description: Use this skill when the user wants a document that combines narrative text with specific visual evidence, such as charts, images, or maps, to support analytical claims. Trigger it for requests like “write a data-driven report with graphs,” “show me the trends with visualizations,” “interleave images with your guide,” or “create a report where the charts and text prove each other.” It is essential for ensuring that visuals are constructed or selected precisely when the narrative needs them, ensuring that subsequent text interprets the data rather than just describing the surface of an image.
---

# Skill: interleaved-multimodal-content-composition

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to compose integrated documents that combine textual narrative with visual evidence (charts, diagrams, or images) in a semantically and logically coherent interleaved sequence. This requires 'Writing-Time Evidence Construction'—the ability to identify the exact moment a narrative requires visual support, construct or select a grounded visualization from underlying data tables or asset pools, and immediately integrate that evidence into the context to constrain and drive 'Decision-Oriented Insight Depth' in subsequent claims.
* **Dimension Hierarchy**: Grounded Expository Writing->Empirical Evidence Grounding->interleaved-multimodal-content-composition

### Real Case
**[Case 1]**
* **Initial Environment**: The agent is provided with an analysis request regarding global longevity and several raw data tables containing life expectancy by country, gender, and infant mortality rates from 1816 to 2023.
* **Real Question**: Why do women live longer than men? Create a global and historical exploration report with interleaved visualizations.
* **Real Trajectory**: The agent drafts an introduction setting the scene for a 5-year global gap. At the first analytical transition, it pauses to request a 'Global map of the life expectancy gap in 2023.' Receiving the map (showing deep blue for Belarus), it resumes writing to explain that Eastern Europe exhibits the largest disparities. It then requests a 'Side-by-side bar chart of infant mortality by sex' to prove the biological foundation of the gap. Finally, it interprets the higher male bars in the specific chart to conclude that the longevity gap is forged in the earliest days of life.
* **Real Answer**: Women consistently outlive men globaly, with a gap of ~5.01 years. This regional variation is vividly illustrated in the world map [IMG#1], where Eastern Europe (e.g., Belarus at 9.33 years) stands out. As seen in the side-by-side bar chart [IMG#4], male infants have higher mortality across all 28 countries. This confirms that while social factors modulate the gap, the foundation is biological vulnerability in infancy.
* **Why this demonstrates the capability**: This case demonstrates 'Writing-Time Construction' and 'Insight-Driven Alignment.' The agent doesn't just list charts at the end; it identifies the specific historical and regional claims that require visual proof, requests them on-demand, and then uses the resulting visual data (like the specific Belarus outlier) to drive the next logical step in the narrative.
---
**[Case 2]**
* **Initial Environment**: The agent is given a source about popular plant meanings and a candidate list of images: a Magnolia flower, an Asparagus Fern, and an Ivy branch.
* **Real Question**: What plants symbolize friendship?
* **Real Trajectory**: The agent identifies the core task as a 'what-is' query requiring visual labels. It maps the meaning 'friendship' to its targets: Magnolia (lasting friendship), Asparagus Fern (eternal friendship), and Ivy (loyalty). It then generates a structured markdown response that interleaves each plant description with its respective candidate image.
* **Real Answer**: Various plants characterize friendship: # **Magnolia**: Symbolizes purity and 'lasting friendship.' ![Magnolia](IMG#1) # **Asparagus Fern**: Represents eternal friendship. ![Asparagus Fern](IMG#19).
* **Why this demonstrates the capability**: This demonstrates 'Sequential and Contextual Accuracy.' The agent must ensure that the sequence of images matches the order of the plant descriptions and that each image index is correctly matched to its specific botanical text rather than mixed up.

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

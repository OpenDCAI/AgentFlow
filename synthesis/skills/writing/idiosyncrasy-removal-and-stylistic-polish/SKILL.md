---
name: idiosyncrasy-removal-and-stylistic-polish
description: Use this skill when the writing needs to move beyond simple 'AI fluency' to achieve expert-level literary quality, human personality, and varied vocabulary. Trigger it for requests like 'make this sound like a real person,' 'add more vivid sensory details,' 'remove the robot-like cliches,' 'make the ending echo the beginning,' or 'don't use the same words over and over.' It is specifically designed to purge 'AI slop' (formulaic metaphors, low-density adjectives, repetitive sentence loops) while injecting high-resolution imagery, diverse vocabulary, and professional structural closure.
---

# Skill: idiosyncrasy-removal-and-stylistic-polish

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to transform standardized, low-variance linguistic outputs into professional, human-aligned prose through multidimensional stylistic optimization. This operates on a physiological axis (injecting high-resolution sensory imagery and varied lexical richness), a subtractive axis (managing Type-Token Ratios to prevent semantic cycling and purging pervasive 'robovoice' cliches), and a structural axis (orchestrating thematic echoes between introductions and conclusions).
* **Dimension Hierarchy**: Open-ended Writing Judgment->Stylistic Polish and Naturalness->idiosyncrasy-removal-and-stylistic-polish

### Real Case
**[Case 1]**
* **Initial Environment**: The agent is in a blank drafting space and receives a prompt about the meaning of life, which often triggers generic AI 'inspirational' templates.
* **Real Question**: Write a high-quality argumentative essay on 'The Journey of Life' for high school students. Use professional, evocative language and ensure the structure is cohesive.
* **Real Trajectory**: The agent first identifies the common 'journey' cliche and resolves to move past generic travel metaphors. It maps a 'Thematic Echo' plan: the introduction describes the 'unfolding map' of youth, and the conclusion returns to the motif of 'navigating by internal stars.' It integrates philosophical anchors to replace abstract 'happiness,' using 'Parallelism' in the body paragraphs to contrast the 'grit of hardship' against the 'fragrance of success.'
* **Real Answer**: Life is less a destination than an evolving cartography of the soul. For the high school student, this map is not yet drawn, but is instead being felt through the friction of every challenge... [Body utilizing Parallelism]... Ultimately, as we fold the maps of our youth and prepare for the broader horizons of adulthood, we find that the significance was never in the arrival, but in the courage to remain the navigator of our own internal stars.
* **Why this demonstrates the capability**: This case demonstrates 'Thematic Echo' and 'Rhetorical Orchestration'. It avoids the low-quality failure mode of simply listing 'life has good and bad parts' by using sophisticated conceptual transitions, avoiding obvious AI metaphors, and providing a circular structural wrap.
---
**[Case 2]**
* **Initial Environment**: The agent is provided with a flat, narrative description of an autumn park that lacks sensory depth.
* **Real Question**: Describe an autumn park at sunset in a way that feels immersive and emotionally resonant.
* **Real Trajectory**: The agent creates a 'Sensory Modality Ledger,' selecting visual (crimson maple leaves), auditory (rhythmic crunch), and tactile (sharp bite of northern air) anchors. It establishes an 'Emotional Atmosphere' of tranquil nostalgia. It curates a diverse lexicon, specifically avoiding repetitive sentence lengths and generic words like 'beautiful' or 'chilly'.
* **Real Answer**: The park was an incinerator of gold and crimson. Beneath my boots, the oak leaves gave a dry, rhythmic crunch—the sound of the season's clock winding down. A sharp northern wind nipped at my collar, carrying the faint, iron scent of impending rain. The shadows grew long, reaching across the pond like dark fingers, until the sun dipped below the oaks and left only the hushed, sapphire quiet of a world preparing for sleep.
* **Why this demonstrates the capability**: This illustrates 'Multi-Sensory Imagery'. By deliberately avoiding the LLM habit of saying 'The park was beautiful and colorful' and instead building an intricate, multi-track sensory experience (sound of crunching, scent of iron, tactile nip), it creates authentic human immersion.
---
**[Case 3]**
* **Initial Environment**: The agent is provided with a task description for a video script, ten formatting instructions (scene headings, call-to-action), and specific stylistic features. The target length is approx 400 words about making sourdough.
* **Real Question**: Generate a funny video script for young adults about the process of making sourdough bread from scratch. Follow all formatting rules, including scene descriptions, and ensure highly varied vocabulary.
* **Real Trajectory**: The agent identifies that formatting instructions often bloat the text with repetitive phrases. It monitors its 'Type-Token Ratio' (TTR) as it drafts. To avoid 'boring' semantic cycling, it clusters synonyms for 'dough' (starter, leaven, sourdough gold) and 'kitchen' (culinary lab, home hearth), ensuring the diversity score remains high across all 12 scenes without reverting to AI defaults.
* **Real Answer**: [scene-1]: A flour-covered kitchen at 3 AM. A young man stares at a jar like it's a child. 'Meet Doug... short for Sourdough.' [scene-2]: Close up of 'Doug'. 'He's alive, he's tangy, and he's currently taking over my fridge.'
* **Why this demonstrates the capability**: This illustrates 'Length-Aware Lexical Optimization.' By anticipating the model's tendency to repeat words when executing long formatted requests, it systematically curates diverse terminology to suppress synthetic 'AI slop' and maintain professional linguistic richness.

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

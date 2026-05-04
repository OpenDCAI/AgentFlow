---
name: proverb-idiomatic-translation
description: Use this skill when the user wants translation data for culturally loaded text that cannot be translated literally, including cases where the source is written in informal phonetic scripts. Trigger it for requests like 'don't translate it word for word,' 'capture the slang and emoji vibe of this social media comment,' 'the text uses Romanized spelling for a local saying,' or 'use a native proverb equivalent.' It manages proverbs, internet slang, and cases where figurative meaning must be recovered from non-standardized orthography.
---

# Skill: proverb-idiomatic-translation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to translate culturally embedded phrases, proverbs, internet slang, and multimodal markers (like emojis) by preserving their pragmatic force and metaphorical wisdom through functional target-language equivalents. This capability specifically encompasses the decoding of figurative intent from both standardized scripts and non-standardized phonetic representations (e.g., Romanized Urdu or Arabizi), resolving the tension between literal word-for-word fidelity and the preservation of the 'cultural aura' or intended sentiment.
* **Dimension Hierarchy**: Specialized and Culturally Grounded Translation->Figurative and Cultural Translation->proverb-idiomatic-translation

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent is provided with an informal digital message written in Romanized Urdu (the Urdu language represented using the Latin alphabet). This format lacks standardized orthography and relies on phonetic approximations of colloquial sayings.
* **Real Question**: Translate the following Urdu text into English while preserving the cultural meaning and avoiding a word-for-word approach: 'Oont ke munh mein zeera.'
* **Real Trajectory**: The agent identifies the Latin-script input as a phonetic representation of an Urdu idiom. It recognizes that the literal meaning ('a cumin seed in a camel’s mouth') describes an insignificant amount for a large need. It maps this figurative proposition to the common English idiomatic equivalent that carries the same pragmatic weight.
* **Real Answer**: A drop in the ocean.
* **Why this demonstrates the capability**: This case demonstrates the capability to resolve figurative meaning from non-standardized phonetic orthography. A literal translator would output the 'cumin seed' string, which is nonsensical in English. By identifying the cultural intent within the Romanized script, the agent proves it can bridge distinct linguistic and script-based conceptualizations.
---
**[Case 2]**
* **Initial Environment**: A translation agent processes a high-engagement comment on a lifestyle social media feed. The comment uses community-specific slang and a pragmatic emoji acting as a mood indicator.
* **Real Question**: Translate the following social media comment into natural English: '看这个教学看到我直接破防了，错失恐惧症犯了 💀'
* **Real Trajectory**: The agent identifies '破防' as internet slang for an emotional breakdown rather than a military breach. It then maps the 'fear of missing out' concept to the English acronym 'FOMO'. Finally, it interprets the skull emoji as a marker of being emotionally overwhelmed, adjusting the tone of the English output accordingly.
* **Real Answer**: I'm literally an emotional wreck after watching this tutorial, giving me major FOMO 💀
* **Why this demonstrates the capability**: This illustrates the mapping of pragmatic nuance across internet cultures. The agent proves it can adapt slang and recognize that emojis function as functional markers that dictate the communicative tone rather than acting as literal word replacements.
---
**[Case 3]**
* **Initial Environment**: The agent receives a literary or poetic lyric sequence focusing on a tragic romance where specific colors symbolize a narrative climax rather than mere optic appearance.
* **Real Question**: Translate these lyrics into English while preserving the cultural metaphors: '君去时褐衣红，小奴家腰上黄'
* **Real Trajectory**: The agent identifies that 'coarse robe turned red' is a metaphor for blood staining clothes due to a fatal injury. It further recognizes that the 'yellow sash' implies wearing mourning garments in the specific historical context. It avoids a literal color-change description and uses language that evokes the grave narrative tragedy.
* **Real Answer**: When you departed, your humble robe was stained crimson with your blood; with my yellow sash, I followed you to the grave.
* **Why this demonstrates the capability**: This case tests the ability to decode the 'aura' of symbolic metaphors. A literal translation would describe brown clothes turning red, entirely missing the narrative tragedy. Prioritizing poetic resonance over dictionary definition demonstrates complex cultural transcreation.

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

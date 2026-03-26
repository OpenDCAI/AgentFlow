---
name: discourse-consistent-document-translation-data-synthesis
description: Use this skill when the user wants translation tasks that break sentence-by-sentence systems and require document context. Trigger it for requests like "make the translation depend on earlier sentences," "test pronoun resolution across the paragraph," "preserve who is speaking," or "keep the wording and style consistent across the whole passage." It is especially useful for literary paragraphs, dialogue scenes, and technical documents where the wrong pronoun, tense anchor, or repeated term can destroy coherence.
---

# Skill: Discourse-consistent document translation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to translate a paragraph or document while preserving discourse phenomena that only become visible with context, including entity consistency, reference resolution, zero pronouns, lexical cohesion, deixis, ellipsis, and narrative voice. The capability goes beyond sentence-level adequacy by requiring the translation to remain coherent when read as a connected document.
* **Dimension Hierarchy**: Document Transformation & Synthesis->Translation->Discourse-consistent document translation

### Real Case
**[Case 1]**
* **Initial Environment**: A Japanese convenience-store narrative paragraph is translated into English, and the system can either see only isolated sentences or the full paragraph context.
* **Real Question**: "Translate the following paragraph into English."
* **Real Answer**: "Ah, and one pack of cigarettes, number five." "Right away." I quickly pulled out a Marlboro Light Menthol and scanned it at the register. "Please confirm your age on the touch screen." His gaze shifted to the showcase with the fast food as he touched the screen, and I stopped my finger’s movement.
* **Why this demonstrates the capability**: The better translation depends on paragraph context, which clarifies that “I” is acting at the register and that “right away” is preferable to the flatter “understood.” Sentence-level translation loses those discourse cues and introduces pronoun and wording errors. This directly tests context-dependent translation consistency.

---
**[Case 2]**
* **Initial Environment**: A document-level machine-translation benchmark evaluates whether prompts and model variants preserve entity consistency, referential expressions, coherence, and phenomena such as deixis, ellipsis, lexical cohesion, and zero pronouns.
* **Real Question**: "Translate the document while preserving discourse phenomena across sentences."
* **Why this demonstrates the capability**: The benchmark is explicitly built to expose failures that look acceptable at sentence level but become wrong at document level. A model must use previous context to resolve omitted subjects, maintain lexical consistency, and avoid discourse-breaking pronoun choices. This is exactly the capability a document agent needs for serious translation work.

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

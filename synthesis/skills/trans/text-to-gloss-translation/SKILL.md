---
name: text-to-gloss-translation
description: Use this skill when the user wants to translate spoken or written natural language into 'Gloss' notation, which acts as a written label system for Sign Language (SL). Trigger it for requests like 'convert this to sign language labels,' 'write the gloss for this sentence,' 'translate this for a deaf person using sign-language word order,' or 'how would you sign this in a word-for-word label format?' It handles specific sign-language constraints such as using infinitives and omitting functional words.
---

# Skill: text-to-gloss-translation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform Text-to-Gloss (T2G) translation by converting natural language into a sequence of glosses—written approximations that bridge spoken language and Sign Language. This involves executing systematic transformations including verbal lemmatization (converting all verbs to infinitives), the omission of functional words (articles, auxiliary verbs, and particles), and reordering syntax to align with the visual-spatial logic of sign languages like BdSL or ASL.
* **Dimension Hierarchy**: Specialized and Culturally Grounded Translation->Sign-Language-Grounded Translation->text-to-gloss-translation

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent is set to process Bangla text for a deaf and hard-of-hearing audience requiring Bangla Sign Language (BdSL) glossing.
* **Real Question**: আমি আজ স্কুলে গাইতে যাব। (I will go to sing in school today.)
* **Real Trajectory**: The agent identifies the source as natural Bangla. It extracts the core concepts—I, Today, School, Sing, Go. It applies the BdSL 'rule of thumb' by converting theinflected verbs 'গাইতে' and 'যাব' into their infinitive forms 'গাওয়া' and 'যাওয়া' and structuring them according to the concept-first logic.
* **Real Answer**: আমি আজ স্কুল গান গাওয়া যাওয়া (I TODAY SCHOOL SING GO)
* **Why this demonstrates the capability**: This case demonstrates the fundamental T2G requirements of lemmatization and omission. The agent successfully maps the complex future tense and infinitive markers into a sequence of base sign labels, ensuring the result is a recognizable gloss sequence for a BdSL user.
---
**[Case 2]**
* **Initial Environment**: A translation agent is provided with an English sentence for conversion into a written sign language approximation.
* **Real Question**: The boy is playing with a ball in the garden.
* **Real Trajectory**: The agent identifies functional words such as 'The', 'is', 'with', 'a', and 'in' for removal. It isolates the primary entities (BOY, BALL, GARDEN) and the action (PLAY). It reorders the tokens to follow a topic-comment or subject-object-verb sign syntax.
* **Real Answer**: BOY GARDEN BALL PLAY
* **Why this demonstrates the capability**: Success is achieved by purging the spoken-language-specific syntactic glue that does not exist in sign language. The agent demonstrates the ability to strip away articles and prepositions while preserving the core semantic propositions in a 'concept-label' format.

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

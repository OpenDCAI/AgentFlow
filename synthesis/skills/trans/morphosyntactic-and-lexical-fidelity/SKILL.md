---
name: morphosyntactic-and-lexical-fidelity
description: Use this skill when translating content into languages where words change their form through prefixes or suffixes to show grammar, or where the same word means different things. Trigger it for requests like 'ensure the prefix matches the pronoun,' 'don't mess up the verb endings in agglutinating languages like Ibibio,' 'keep the grammar straight in complex sentences,' or 'make sure words with many meanings are translated correctly based on the context.'
---

# Skill: morphosyntactic-and-lexical-fidelity

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to ensure sentence-level grammatical and morphological coherence by correctly inflecting verbs, adjectives, and nouns in accordance with the target language's system of gender, case, number, and agglutinating morphology (prefixes/suffixes). This capability mitigates 'syntactic collapse' in high-density sequences, handles phonetic/tonal diacritic stability in African-centric scripts, and resolves lexical disambiguation for polysemous terms and entities using pragmatic and domain-specific evidence.
* **Dimension Hierarchy**: Contextual and Constraint-Aware Translation->Morphosyntactic and Lexical Fidelity->morphosyntactic-and-lexical-fidelity

### Real Case
**[Case 1]**
* **Initial Environment**: A translation scenario involving a factual predicate about a female subject being born in a specific city. The target language is Russian, which requires past-tense verb agreement with the subject's gender and locative case for the city.
* **Real Question**: Translate the following statement into Russian: '[X] was born in Stockholm' where X is 'Sofya Kovalevskaya'.
* **Real Trajectory**: The agent identifies that the subject 'Sofya Kovalevskaya' is female. It chooses the feminine past-tense form of 'was born' ('родилась') instead of the default masculine ('родился'). It also recognizes that the city 'Stockholm' follows a preposition requiring the locative case, rendering it as 'в Стокгольমে' to ensure full sentential fluency.
* **Real Answer**: Софья Ковалевская родилась в Стокгольме.
* **Why this demonstrates the capability**: This case tests morphological agreement across different word classes. A standard template-based model would likely produce a masculine verb ('родился') for all persons, but this agent handles gender-specific inflection and syntactically required case markers, transforming a 'disfluent' prompt into a grammatical sentence.
---
**[Case 2]**
* **Initial Environment**: A translation agent processes English sentences into minority Nigerian languages such as Ibibio and Anaang. These are agglutinating languages belonging to the Lower Cross branch where verbs and nouns take specific prefixes to reflect person, tense, and regional lexical identity.
* **Real Question**: Translate the sentence 'I am going to school' into both Ibibio and Anaang.
* **Real Trajectory**: The agent identifies the root verb 'go' as 'ka'. For Ibibio, it attaches the first-person prefix 'ñ-' to the root, resulting in 'ñ-ka'. For Anaang, it applies the 'n-' prefix variant and identifies the specific regional term for 'school/book' as 'kñgwed' rather than the Ibibio 'kñwed'.
* **Real Answer**: Ibibio: ami ñ-ka ufo. kñwed. Anaang: ami n-ka ufo. kñgwed.
* **Why this demonstrates the capability**: This demonstrates the ability to handle agglutinating morphology and regional lexical differentiation. The agent must correctly apply language-specific prefix rules (ñ- vs n-) and distinguish between closely related Lower Cross vocabularies, proving it can navigate the morphosyntactic nuances of low-resource minority languages.
---
**[Case 3]**
* **Initial Environment**: A translation agent is processing a technical biomedical research paper. The source is a single, extremely dense Arabic sentence describing a laboratory observation regarding neurotransmitter binding, exceeding 50 words.
* **Real Question**: Translate the following complex Arabic sentence into English while preserving the single-sentence structure: قد لا يكون الربط الحويصلي السريع الملاحظ ضرورياً لتراكم الأمين بواسطة النهايات قبل المشبكية خلال فترات التعرض القصيرة...
* **Real Trajectory**: The agent maps 'Long-Distance Morphological Chains' between the sentence head and tail. It identifies the core subject and traces deep nested relative clauses, ensuring that the target English structure avoids 'context collapse' and maintains perfect agreement between the distant subject and the final verbs.
* **Real Answer**: The rapid vesicular binding observed might not be essential for the accumulation of the amine by the presynaptic terminals during periods of short exposure...
* **Why this demonstrates the capability**: This demonstrates high-density fidelity because the sentence contains distinct, nested prepositional modifications within a single clausal frame. It requires the agent to manage long-distance morphosyntactic dependencies without improperly defaulting to new sentence fragments or simplifying the technical logic.

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

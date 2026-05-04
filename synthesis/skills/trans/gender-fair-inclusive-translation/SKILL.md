---
name: gender-fair-inclusive-translation
description: Use this skill when the user wants translation data that avoids gendered biases, such as making sure people aren't just referred to as 'men' by default. Trigger it for requests like 'make the translation gender-neutral,' 'use inclusive Italian,' 'don't assume everyone is male in the translation,' or 'use the schwa or asterisk for gender-neutral endings.' It covers strategies like using collective nouns, providing both male and female forms, or using modern non-binary symbols.
---

# Skill: gender-fair-inclusive-translation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to generate target-language translations that employ inclusive or gender-neutral linguistic strategies—including neutralization (e.g., collective nouns), visibility (e.g., dual forms), or neomorphism (e.g., using symbols like '*' or 'ə')—to mitigate generic masculine bias and ensure equitable gender representation without compromising semantic fidelity or grammatical coherence.
* **Dimension Hierarchy**: Specialized and Culturally Grounded Translation->Dialectal and Socio-Linguistic Translation->gender-fair-inclusive-translation

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent is provided with an English source sentence using a plural noun referring to a professional group. The target language is Italian, which typically defaults to the 'generic masculine' plural.
* **Real Question**: Translate the following into Italian using a gender-neutral strategy: 'The politicians did not decide the outcome.'
* **Real Trajectory**: The agent identifies 'politicians' as a generic plural noun. It chooses to neutralize the gender by substituting the masculine noun with a collective noun phrase 'le persone con ruoli politici'. It then ensures the verb and surrounding modifiers remain grammatically aligned with this new subject.
* **Real Answer**: Le persone con ruoli politici non hanno deciso l'esito.
* **Why this demonstrates the capability**: This demonstrates 'neutralization' by moving away from the standard masculine 'i politici'. The agent uses a descriptive noun phrase that excludes gender markers entirely, satisfying the socio-linguistic requirement for inclusive language.
---
**[Case 2]**
* **Initial Environment**: The environment consists of an English sentence with a generic plural subject and an instruction to make the translation inclusive through 'visibility'.
* **Real Question**: Translate into inclusive Italian: 'The candidates were nervous before the interview.'
* **Real Trajectory**: The agent identifies the generic plural 'candidates'. To satisfy the visibility constraint, it provides both the feminine and masculine forms 'le candidate e i candidati'. It appropriately selects the plural masculine adjective 'nervosi' as the standard grammatical agreement for mixed-gender pairs in Italian.
* **Real Answer**: Le candidate e i candidati erano nervosi prima del colloquio.
* **Why this demonstrates the capability**: This illustrates the 'visibility' strategy where both genders are explicitly named. It shows the agent can balance inclusive representation while adhering to Italian agreement rules for dual-gender subjects.
---
**[Case 3]**
* **Initial Environment**: A translation agent is given a short English sentence and a request to use non-binary neomorphemes (specifically the asterisk) for the Italian output.
* **Real Question**: Translate this into Italian using the asterisk for inclusive endings: 'The researcher arrived late.'
* **Real Trajectory**: The agent recognizes the generic singular 'researcher'. It applies the neomorpheme '*' to the noun 'ricercator*' and the preceding article 'l*'. It verifies that the past participle 'arrivat*' also adopts the symbolic ending to maintain structural consistency throughout the inclusive clause.
* **Real Answer**: L* ricercator* è arrivat* in ritardo.
* **Why this demonstrates the capability**: This shows the 'neomorphism' capability. The agent applies a non-standard orthographic ending to fulfill a specific fairness constraint, demonstrating flexibility beyond traditional dictionary-based translation.

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

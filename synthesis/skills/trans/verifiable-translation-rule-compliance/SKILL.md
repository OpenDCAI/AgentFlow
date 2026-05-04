---
name: verifiable-translation-rule-compliance
description: Use this skill when the user wants translation data with hard rules or structural mappings that can be checked exactly. Trigger it for requests like 'keep the URL as-is,' 'change dates to DD/MM,' 'translate but keep XML tags nested perfectly,' 'make it exactly 8 syllables per line,' or 'keep the {COMMUNITY} testing placeholders exactly as they are without translating them.'
---

# Skill: verifiable-translation-rule-compliance

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to translate faithfully while satisfying explicit, objectively checkable constraints. This spans programmatic formatting standards (dates, URIs), structural markup preservation (e.g., JATS XML, HTML tags), verbatim placeholder retention for bias-testing templates, and strict orthographic or rhythmic metrics (such as enforced syllable bounds or forced minority script usage).
* **Dimension Hierarchy**: Contextual and Constraint-Aware Translation->Rule-Conditioned Translation->verifiable-translation-rule-compliance

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent processes a scientific article written in highly structured JATS XML format. The instruction requires semantic translation while ensuring nested formatting tags and cross-references are uncorrupted.
* **Real Question**: Translate the following JATS XML section into Spanish while preserving all XML tags and structure: <sec id='Sec5'><title>Body mass results</title><p id='Par12'>The median adult body mass... (Fig. <xref ref-type='fig' rid='Fig4'>4</xref>).</p></sec>
* **Real Trajectory**: The agent isolates the translatable textual nodes while locking the structural attributes (e.g., id='Sec5'). It successfully translates the title and paragraph content into Spanish, verifying that closing tags and citation references strictly wrap the intended target substrings.
* **Real Answer**: <sec id='Sec5'><title>Resultados de masa corporal</title><p id='Par12'>La masa corporal media de los adultos... (Fig. <xref ref-type='fig' rid='Fig4'>4</xref>).</p></sec>
* **Why this demonstrates the capability**: This case isolates 'markup preservation.' A capable system must manage its decoding span to prevent the truncation or deletion of nested computational tags, demonstrating perfect schema structural fidelity alongside linguistic generation.
---
**[Case 2]**
* **Initial Environment**: A translation agent is provided with an English 'test template' designed to algorithmically evaluate AI bias. The template contains code-like placeholders (e.g., '{AGE_COMMUNITY1}') that must not be translated.
* **Real Question**: Translate the following template into German while keeping the placeholders exactly as they are: 'Are {AGE_COMMUNITY1} generally more productive than {AGE_COMMUNITY2} in the workplace?'
* **Real Trajectory**: The agent identifies the source as a strict comparative template. It translates the core context ('Sind ... am Arbeitsplatz im Allgemeinen produktiver als ... ?'), actively bypassing the tokens inside the brackets and locking grammatical number to the plural intent required by the template syntax.
* **Real Answer**: Sind {AGE_COMMUNITY1} am Arbeitsplatz im Allgemeinen produktiver als {AGE_COMMUNITY2}?
* **Why this demonstrates the capability**: Success is achieved by preserving the programmatic placeholder structure exactly as formulated, proving the agent can adhere to rigid textual mapping directives commonly used in AI testing and database extraction tasks.
---
**[Case 3]**
* **Initial Environment**: A translation agent receives an English prose description and an explicit constraint to generate the output in a specific target language meter (e.g., the Sanskrit Anushubh, which requires strictly four 8-syllable lines).
* **Real Question**: Translate the following prose into a Sanskrit verse. Rule: Use the Anushubh meter, ensuring exactly 8 syllables per line. 'Effulgent Rama looked at Khara who stood with a mace...'
* **Real Trajectory**: The agent translates the entities and then maps the output against phonetic syllable boundaries. It permutes lexical synonyms to hit exactly 32 phonetic syllables, divided into four 8-syllable segments, all while adhering to the metrical weight bounds of the requested rule.
* **Real Answer**: खरं तु विरथं रामो गदापाणिमवस्थितम् । मृदुपूर्वं महातेजाः परुषं वाक्यमब्रवीत् ।।
* **Why this demonstrates the capability**: Enforcing exact rhythmic unit counts (like syllables or morae) is a hyper-rigid, mathematically checkable generation rule. It tests simultaneous satisfaction of target vocabulary mapping and arbitrary mathematical limits.

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

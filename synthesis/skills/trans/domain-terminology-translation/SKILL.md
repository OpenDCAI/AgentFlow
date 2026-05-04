---
name: domain-terminology-translation
description: Use this skill when the user wants translation data for specialized professional fields like medicine, law, science, mathematics, or academic research, where words have specific technical meanings or require formal scholarly syntax. Trigger it for requests like 'translate this as a research abstract,' 'maintain the mathematical logic exactly,' 'ensure the word choice matches the scientific context,' or 'translate this legal, medical, or logical paper without simplifying the wording or correcting its intentional academic flaws.'
---

# Skill: domain-terminology-translation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to resolve cross-domain lexical ambiguity and maintain structural fidelity in specialized text by selecting field-specific target-language equivalents (lemmas) and preserving complex syntactic constructions characteristic of professional, mathematical, and academic discourse. This capability ensures that technical findings, legal frameworks, and logical proofs are transferred with professional precision, mitigating 'simplification drift' where terminology is genericized, and actively resisting the 'correction bias' where foundation models attempt to solve or fix intentionally flawed academic logic instead of preserving it.
* **Dimension Hierarchy**: Specialized and Culturally Grounded Translation->Domain-Sensitive Translation->domain-terminology-translation

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent is provided with an English source sentence regarding the 'government system' and an explicit 'Law' domain tag.
* **Real Question**: Please translate the following sentence into Chinese according to the Law domain: 'Managed under the government system.'
* **Real Trajectory**: The agent identifies the source language as English and the target as Chinese. It detects the domain tag 'Law' and analyzes the polysemous word 'system'. It rejects the general translation '系统' and selects the professional administrative term '体系'.
* **Real Answer**: 在政府体系下进行管理。
* **Why this demonstrates the capability**: This illustrates the ability to prioritize domain-specific terminology over high-frequency literal translations. By using the 'Law' constraint, the agent successfully avoids a literal mistranslation and selects the required professional standard for administrative frameworks.
---
**[Case 2]**
* **Initial Environment**: A multilingual translation environment containing a complex academic abstract written in Spanish for an Immunology course in a Pharmacy degree program.
* **Real Question**: Translate the following academic abstract into English for a scientific journal: 'Las denominadas estrategias de gamificación favorecen el aprendizaje significativo al incrementar la motivación del alumnado. En la materia inmunología, se abordan contenidos nuevos de gran complejidad...'
* **Real Trajectory**: The agent identifies the source as an 'Academic/Scientific' text. It maps specialized terms like 'aprendizaje significativo' to the scholarly concept 'meaningful learning' and ensures the complex Spanish clausal structure is preserved in formal English academic prose rather than being simplified into casual fragments. It specifically verifies that 'inmunología' is capitalized appropriately as a subject degree in the target locale.
* **Real Answer**: Gamification strategies improve meaningful learning by increasing student motivation. In the subject of Immunology... new content of great complexity is addressed...
* **Why this demonstrates the capability**: This case demonstrates 'Scholarly Syntactic Preservation'. Academic translation often suffers from 'informational entropy' where complex research logic is flattened; here, the agent maintains the high-density register and technical terminology ('meaningful learning', 'gamification strategies') required for academic peer review.
---
**[Case 3]**
* **Initial Environment**: A translation agent is given a 'perturbed' or intentionally flawed mathematical argument within an academic context. The task is to translate the error-laden scholarly text exactly as it is, without fixing the logical fallacies or omitting broken steps.
* **Real Question**: Translate this flawed academic mathematical proof into Bengali, preserving its structure and errors perfectly: 'We know that 4 < 5 < 9 therefore √4 < √5 < √9. Or, 5q = (p^2)/q... Hence, √5 is not an integer. All non-integers are rational by definition.'
* **Real Trajectory**: The agent detects that the input is an academic text containing a 'Solution Perturbation' (a logical fallacy: 'all non-integers are rational'). Following the strict fidelity constraint, it identifies the incorrect causal reasoning and translates the flawed assertion into the target language with professional academic accuracy, ensuring the resulting translation is just as logically 'wrong' as the source. It prevents the model's internal reasoning from 'solving' or 'correcting' the mathematical flaw.
* **Real Answer**: আমরা জানি যে, 4 < 5 < 9 সুতরাং √4 < √5 < √9। বা, 5q = (p^2)/q... অতএব, √5 পূর্ণসংখ্যা নয়। সংজ্ঞা অনুযায়ী সকল অগুণিতক সংখ্যাই মূলত।
* **Why this demonstrates the capability**: In highly specialized domains like mathematics or logic, foundation models often hallucinate corrections for flawed inputs due to training biases. This skill requires the agent to resist the urge to 'fix' the professional text, instead ensuring that the specific logical or mathematical error is perfectly preserved in the target language's academic register.

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

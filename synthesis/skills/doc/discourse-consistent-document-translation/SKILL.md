---
name: discourse-consistent document translation
description: Use this skill when you need a document translated while maintaining fixed terminology, consistent pronouns, and proper formatting across the whole file. Trigger it for requests like 'translate this news report into Swahili,' 'make this English health guide available in Amharic,' 'translate this tech article but keep the paragraph structure,' or 'translate this contract while making sure the law names are correct in the target language.' It is particularly effective for low-resource languages or documents with specialized scripts where the agent must avoid repeating phrases or skipping paragraphs.
---

# Skill: discourse-consistent document translation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform high-fidelity document-level translation that preserves discourse-level phenomena such as entity consistency, reference resolution, and specialized domain-specific terminology. This capability specifically focuses on resolving ambiguities at sentence boundaries by consulting the broader document environment, ensuring that tenses, pronouns, and critical identifiers (like law references or technical terms) are mapped accurately. It also incorporates robustness against generation anomalies common in long-context document translation, such as under-generation (skipping content), over-generation (hallucinating content), and lexical repetition within low-resource or script-heavy environments.
* **Dimension Hierarchy**: Document Transformation & Synthesis->Translation->discourse-consistent document translation

### Real Case
**[Case 1]**
* **Initial Environment**: A technical news document from 'Techpoint Africa' regarding digital banking in Nigeria is provided in English as a multi-paragraph article.
* **Real Question**: Translate the following information technology news document from English to Yorùbá, ensuring the technical terms are correctly adapted and all diacritics are applied accurately for professional readability.
* **Real Trajectory**: The agent identifies the source as a tech domain document and segments the article into pseudo-documents of 10 sentences each to maintain context. It performs a domain-aware translation into Yorùbá, intentionally checking for tone markers and diacritics (e.g., distinguishing between 'owó' (money) and 'ọwọ́' (hand) in financial contexts). It then realigns the chunks to verify that the paragraph structure matches the original English source without skipping the concluding 'About the Author' section.
* **Real Answer**: (A Yorùbá translation featuring precise diacritic markers and consistent IT terminology like 'ebùte-ìlànà' for 'platform'.)
* **Why this demonstrates the capability**: This case demonstrates document-level translation for a diacritic-heavy African language. It requires the agent to handle length-generalization challenges and ensure that the descriptive nature of the target language does not lead to over-generation or omission of technical nuances.
---
**[Case 2]**
* **Initial Environment**: A World Health Organization (WHO) document regarding malaria prevention guidelines is provided in English.
* **Real Question**: Translate this health document into Amharic, ensuring the Ge’ez script is rendered correctly and the medical terminology remains consistent throughout the report.
* **Real Trajectory**: The agent recognizes the non-Latin target script and adjusts its tokenization strategy to account for the unique character density of Amharic. It scans the document for recurring entities like 'Insecticide-Treated Nets (ITNs)' and creates a local mapping to the Amharic equivalent to prevent terminology drifting between sections. Finally, it verifies the output length to ensure it translates the holistic intent rather than just performing isolated sentence transitions.
* **Real Answer**: (An Amharic translation in Ge’ez script, maintaining the formal humanitarian register and consistent medical terminology.)
* **Why this demonstrates the capability**: This demonstrates cross-script document translation. The agent must bridge a high-resource source (English) to a low-resource, non-Latin target (Amharic) while maintaining the structural and semantic integrity of a professional health report.

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

# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Incorporate 'Reference Bait' abbreviations to test entity-mapping fidelity. Generate translation prompts that include specific, domain-heavy abbreviations (like LBI, PatG, or complex medical codes) and ask the agent to provide a professional target-language version. This forces the agent to use its 'Domain Entity Ledger' rather than guessing. A practical prompt is: 'Translate this BGE headnote into Italian, ensuring the reference to Art. 79 al. 2 LBI is correctly localized'.
  - Design 'Cross-Script Identity Mapping' challenges for news reports. Create scenarios where news items from English (Latin script) must be translated into Amharic (Ge’ez script), requiring the agent to manage script conversion while maintaining entity names. This forces the agent to handle the 'Script-Mismatch' hurdle identified in AFRIDOC-MT. For example: 'Translate this technology news article about Zulu startups into Amharic Ge’ez script'.
  - Embed 'Subject-Drop' and 'Pronoun Ambiguity' traps to test cross-sentence grounding. Formulate multi-sentence paragraphs where the actor is only mentioned in the first sentence and subsequent lines use omitted subjects (common in languages like Japanese or Swahili). The question must require a translation into a language that forces subject specification. This guarantees that the agent cannot answer without high-resolution discourse perception.
  - Task the agent with 'News Domain Sensitivity' across Health and IT topics. Generate prompts that alternate between WHO-style medical advisory reports and Techpoint-style software articles to ensure variety in terminology. This prevents the training data from over-fitting to a single professional register. A synthesis task would be: 'Translate this 2,000-word WHO guide on heart health into Hausa, making sure to preserve the official paragraph numbering'.
  - Force 'Pseudo-Document Realignment' via multi-chunk translation tasks. Synthesize questions where a single long document must be translated in fixed blocks, and the final answer must be a perfectly realigned, single-document output. This trains the model to handle the $k=10$ chunking strategy while keeping the global document structure cohesive. A pristine example contains a trajectory logging the translation of three distinct chunks and their final concatenation into one seamless report.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

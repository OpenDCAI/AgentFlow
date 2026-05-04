# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Implement 'Dynamic Paraphrase Injection' to test the retrieval model's semantic limits. Generate questions that explicitly avoid words found in the document chunk (e.g., if the text uses 'pedagogical', the question must use 'teaching style') to force the agent into a non-lexical search. This directly addresses the 'Paraphrase Gap' identified in RAG benchmarks. A practical rule is to prompt for: 'Write a question that uses zero shared nouns with the target paragraph while still asking for the information it contains.'
  - Incorporate 'Cross-Abstraction Level' challenges where the answer is found in an index or summary. Generate questions that target specific sections (e.g., 'What is the purpose of the 2024 Ordinance?') and require the agent to use Section-level MAL chunks to avoid noise. This tests the agent’s ability to recognize structural importance over raw word frequency. A pristine example contains a trajectory moving from Document-level index retrieval to localized paragraph verification.
  - Embed 'Spatial Localization and Coordinate Requests' for recurring document elements like 'Article 1'. Synthesize questions where a label like 'Article 1' appears multiple times (in different resolutions), and the agent must return the [X, Y, W, H] coordinates for the one specific instance. This forces the agent to use perceptual-layout alignment. A success signal is a JSON output containing: '{"value": "Article 1", "location": [150, 200, 50, 10], "section": "Resolution 22"}'.
  - Design 'Lost-in-the-Middle' Trap prompts where the answer is buried in high-density areas of multi-page reports. Formulate questions that require the agent to apply high-threshold semantic filtering to isolate one specific 'needle' in a 'haystack' of similar-sounding regulations. This tests if the agent can stay faithful to a specific clause without being misled by distractors in preceding or following chapters. An example: 'Identify the specific fee for late library returns in 2023, ignoring the 2024 projections listed earlier.'
  - Force 'Institutional Tone Transition' by asking for 'layman summaries' of technical rules. Create synthesis prompts where a highly formal university regulation must be explained to a high-school student while maintaining 100% factual fidelity. This measures the agent’s ability to perform register-shifting during QA. A concrete synth-prompt: 'Explain the enrollment requirements from this statute in plain language, citing the specific paragraph coordinates for where the proof of residency is mentioned.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

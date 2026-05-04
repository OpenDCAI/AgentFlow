# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Synthesize 'Morpho-Stress' prompts using agglutinating language targets like Ibibio and Anaang. Construct commands where a neutral English sentence is paired with a specific minority target language that forces the system to generate complex prefixes. First, define the subject (e.g., 'I') and the verb (e.g., 'go'), then command the agent to produce the exact target variant for that region. For example: 'Translate "I am going to school" into Ibibio using the correct prefix for the first person.'
  - Embed 'Long-Distance Agreement' traps in complex single-sentence prompts. Generate source sentences exceeding 40 words where the primary biological or legal subject is separated from its modifying verb by multiple relative clauses. This forces the agent to demonstrate morphosyntactic retention over long context windows. An effective synthesis item would be: 'Translate this 50-word sentence into Russian, ensuring the adjective in the final clause agrees with the female subject at the start.'
  - Deploy 'Lexical Differentiator' requests for related language clusters. Formulate tasks that require the agent to translate a single source sentence into two different varieties, such as Efik and Anaang, to test fine-grained vocabulary mapping. The gold answer must show 100% adherence to the regional lexical differences (e.g., 'kñwed' vs 'kñgwed'). This evaluates if the agent can distinguish between a lingua franca and a minority variant in low-resource zones.
  - Require Serialized Morphological Reasoning in the JSON trajectory. The synthesis rule mandates that every sample logs the step-by-step identification of the grammatical traits and the subsequent selection of endings. The trace must state: 'Step 1: Identifying Ibibio morph-prefix; Step 2: Mapping first-person subject; Step 3: Executing agglutinating synthesis.' This provides a clear audit trail and ensures the agent is following linguistic logic rather than shallow pattern matching.
  - Incorporate 'Tonal Integrity' checks for African-centric translation datasets. Design prompts that explicitly mention 'preserve all tonal markers and diacritics' to verify if the model can generate high-fidelity scripts without flattening. The gold answer should reflect 100% diacritic accuracy as verified by a native-level character map. For example: 'Translate to Yorùbá and do not omit any tonal marks, particularly on the recurring entity names.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

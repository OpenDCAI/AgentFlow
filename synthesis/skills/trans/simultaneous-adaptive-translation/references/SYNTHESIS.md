# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Synthesize ‘Latency-Aware’ multi-turn prompts using indicator tokens ('low', 'medium', 'high'). The instructions should phrase the translation task as a streaming requirement, for example: 'Translate the following stream from English to German with low latency.' This forces the agent to activate the adaptive segmentation skill learned during its two-stage fine-tuning process. Avoid using a single block of text; instead, simulate the arrival of text as discrete chunks followed by a request to respond.
  - Insert 'Explicit Read/Write Signals' in the gold synthetic answer keys. The synthesis must mandate that every translation segment is preceded by <|end-of-read|> and followed by <|end-of-write|>. This ensures the training data enforces the signaling mechanism necessary for real-time environment interaction. For example: 'Source Segment 1 <|eor|> Target Segment 1 <|eow|> Source Segment 2 <|eor|>...' must be the final format of the answer string.
  - Incorporate 'Non-Monotonic Stressors' to evaluate adaptive reading. Synthesize source sentences where the grammatical structure (like German verb-final clauses) requires the agent to read more than usual before translating. This tests if the agent can 'look ahead' by reading more source chunks before emitting the write signal. An example is a German sentence with a separable prefix at the very end, requiring the agent to defer translation until the full semantic meaning is clear.
  - Utilize 'Interpolated Latency' commands for advanced testing. Create questions that use combined labels like 'low-medium latency' to test the agent's ability to generalize between the fixed categories learned during SFT. This evaluates the 'interpolation effect' and determines if the agent's internal policy can smoothly adjust between granularities. The gold answer should reflect a segmentation frequency that is realistically balanced between the low and medium benchmarks.
  - Implement a 'Streaming Document-Level' continuity rule. Formulate questions that translate long documents without sentence boundaries, requiring the agent to maintain high-quality context over many chunks. This evaluates the 'zero-shot generalization' to document-level SiMT. The gold answer must ensure that terminology and referents (like pronouns) remain consistent across the entire stream, even when segments are generated minutes apart.
  - Strictly enforce the JSON 'Trajectory' and 'Answer' format to include the auto-regressive steps. The synthetic data MUST record the observations (reading chunks) and the actions (writing chunks) in a Step-by-Step sequence inside the trajectory attribute. This proves the agent is performing a genuine real-time interpretation task rather than just an offline translation formatted to look like SiMT. For instance, Step 1: Observation = Chunk1; Action = Translate Chunk1.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

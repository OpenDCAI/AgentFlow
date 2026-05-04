# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Phrase the prompt to explicitly demand cohesive multi-source aggregation. The instructions must command the agent to read oversized files or conflicting sets and synthesize a wholly interconnected, continuous narrative rather than disconnected bullet lists. This tests whether the agent can manage long-range dependencies and theme weaving. An edge case is asking for a trial facts overview from four disjointed witness testimonies.
  - Engineer refutation drafting against conflicting evidence bases. Supply generalized lists of critical allegations alongside chaotic, raw factual evidence, requiring the agent to trace and draft targeted counter-arguments or confirmations. This formally tests the capability to organize a professional output based on rigid structural alignment. A good prompt might say: 'Draft a formal defense letter that maps each numbered accusation to the provided timecards.'
  - Seed chronological contradictions necessitating explicit conflict resolution. Inject dates or claims in one source that explicitly conflict with a hard verifiable log in another source. This forces the agent to play the role of an objective arbiter when composing the final descriptive timeline. A practical example is having a plaintiff claim a car was red, while the police document explicitly states it was blue.
  - Enforce interleaved dynamic formatting constraints. Require the output to generate narrative text that incorporates specific visual asset markers (e.g., [IMAGE: diagram.png]) exactly where the content is discussed. This guarantees the model learns to synthesize layout and prose at the same time. The prompt must explicitly state: 'Images must not be placed at the end; embed them exactly next to the sentence describing them.'
  - Mandate distinct professional or stylistic register shifts. Instruct the agent to discard the tone of the baseline files and adopt a wholly separate one, such as rewriting technical raw notes into a polished presentation script or formal legal filing. A strong example requires minimizing verbose corporate reports into terse bullet points, paired with a conversational speaker script. This proves the agent transforms rather than merely extracts.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

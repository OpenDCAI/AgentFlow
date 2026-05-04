# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Target 'Contextual Granularity' by asking for descriptions that require external anchors. Formulate questions that ask for the 'how' or 'why' behind a local entity, forcing the agent to find the 'Class Skeleton' or 'Parent Section' to answer. For instance, ask 'How does this class-level constant affect the behavior of the `process_data` method?' This forces the agent to navigate from the method to the class-level state. This instruction ensures the agent is not just summarizing a snippet but explaining its role in the system.
  - Formulate 'Relational De-fusion' queries for repository structures. Design questions that ask which specific external utility or constant among a repository group is responsible for an action described vaguely in the target snippet. For example, if a function calls `log_event()`, ask 'Which logging level and destination are used by the `log_event` call in this file?'. This rewards agents that can 'bridge' the call site to the definition site found in a distant utility file.
  - Embed 'Few-Shot Style Alignment' markers in the synthetic ground truth. When generating the final answer for repository-level synthesis, emphasize a concise, 1-3 sentence 'Developer-Style' tone, mirroring the few-shot behavior found in the literature. Avoid conversational 'filler' or 'over-explanation' (e.g., 'In this code, we can see...') and instead provide direct, technically dense summaries. This forces the model to integrate large context volumes without losing the crispness required for high-utility RAG outputs.
  - Synthesize 'Requirement-to-Constraint' questions that hinge on cross-file logic. Create questions that ask 'Is the current implementation of X compliant with the global project standard defined in the README?'. This forces the agent to integrate a 'Requirement' (from Document A) with an 'Implementation' (from Document B). By providing the JSON provenance (e.g., 'Fact A from File 1, Fact B from File 2'), the ground truth provides a clear training signal for multi-step reasoning across domains.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

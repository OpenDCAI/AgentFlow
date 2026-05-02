# Phase 3: Data Synthesis Instructions
* **Question Generation Rules:**
  * **Use passages where context is necessary.** Select paragraphs or multi-sentence segments in which at least one correct translation decision depends on earlier or later content. This is the heart of the skill. Good sources include dialogue, literary narration, pro-drop languages, and technical passages with repeated terminology.
  * **Preserve the full discourse unit in the prompt.** Do not shorten the source down to a single sentence if that would eliminate the dependency. The prompt should explicitly ask for paragraph- or document-level translation when appropriate. An edge case is allowing sentence annotations, but only when the surrounding context remains visible.
  * **Design evaluation around consistency-sensitive outputs.** Prefer answer targets where a reviewer can see whether reference, terminology, style, or deixis has remained stable across the whole output. This makes scoring sharper than general fluency judgments alone. A practical example is checking whether the same item is translated consistently across repeated mentions.
  * **Avoid over-explaining the hidden cue in the prompt.** The question should not tell the agent exactly which pronoun or lexical chain is difficult, because that would collapse the task into guided editing. Instead, let the source naturally contain the dependency. This better reflects real translation work.
  * **Write the trajectory around ambiguity resolution.** The real trajectory should log which earlier sentence or discourse cue was consulted to settle each critical choice. This is more valuable than a generic “translated the paragraph” trace. A concrete example is recording that the agent looked back to determine whether the clerk or the customer was performing the action.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Preserve translation as the principal directive while embedding interlocking verifiable rules. Phrase instructions demanding basic translation but entwined with 1 to 3 explicit mathematical or syntactic structural constraints (e.g., metric conversions, placeholder retention).
  - Embed strict structural elements into deep lexical context. Force the agent to translate heavily nested text formats like JATS XML, JSON values, or LaTeX, commanding that absolutely no formatting tags are altered or translated.
  - Impose exact mathematical and rhythmic limiters. Craft translation requests that ask for rigid rhythmic or token bounds (e.g., 'Convert this prose strictly into 4 lines of exactly 11 syllables each'). This tests rule synthesis intertwined with vocabulary flexibility.
  - Demand forced verbatim adherence for specific string variables. Formulate template translation prompts dictating the strict non-translation of specific code-like blocks (e.g., 'Keep all variables formatted as {VAR_NAME} completely unchanged').
  - Serialize a faithful procedural execution trace in the JSON output. The synthetic trajectory must rigorously document the rule extraction, isolation, variable locking, and exact syntactic rendering steps necessary to pass a programmatic Boolean grader.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

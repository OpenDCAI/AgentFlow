# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Provide a 'Contextual Anchor Sentence' from the preceding paragraph to set the temporal baseline. Synthesize the input so the target sentence is preceded by a sentence already in a clear tense (e.g., 'Yesterday, the hero began his journey'). This forces the agent to demonstrate it can maintain the established frame. For example: 'Using the previous sentence as a tense guide, translate the next line.'
  - Formulate tasks involving 'Temporal Transitions' like flashbacks or changing perspectives. Synthesize prompts where the source text includes a shift from a character's action to their memory of a past event. Command: 'Ensure the translation clearly distinguishes between what is happening now and what happened before.' This evaluates the agent's ability to handle complex aspectual mapping.
  - Embed 'Aspectual Particles' in the Chinese source to test morphological mapping. Design inputs containing 了, 着, and 过 to see if the agent correctly reflects these as Simple Past, Progressive, or Perfective in English. A high-quality synthesis item would use 'guo' (indicating experience) to see if the agent selects the English Present Perfect or Simple Past correctly.
  - Incorporate 'Dialogue-Action Interleaving' to test shift-resistance. Create a source text where a character speaks (Present Tense) while performing an action (Narrative Past Tense). The gold answer must show 100% adherence to this dual-tense structure. For instance: '“What are you doing?” he asked as he drew his sword.'
  - Serialize the 'Temporal Reasoning' steps in the trajectory JSON. Each synthetic sample must document: 1) Identification of the global narrative tense, 2) Detection of any local tense shifts, and 3) Alignment of the English verb forms. This provides the audit trail for document-level temporal cohesion. Step 1: 'Context is past tense'; Step 2: 'Applying simple past to all verbs'.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

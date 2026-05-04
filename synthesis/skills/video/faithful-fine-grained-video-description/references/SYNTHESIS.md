# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Construct Complete Factual Accuracy Prompts that explicitly instruct the agent to avoid common hallucinatory triggers like 'assuming intent' or 'interpolating between cuts'. Use instructional tags such as: 'Describe this video in extreme detail; only include information you can explicitly see or hear, and do not guess what happened between scenes.' This forces the model into a high-fidelity audit mode.
  - Implement Atomic Event Validation Queries that ask the model to list the 'Top 10 most important milestones' in the video before providing the full description. This forces the agent to organize its internal memory based on the atomic blocks identified during exploration. For example, 'First list the key spoken points and text overlays, then provide a flowing description of the scene.'
  - Generate Multi-tier Hierarchical Descriptions where the prompt demands separate paragraphs for 'Global Narrative', 'Micro-Facial Movements', and 'Auditory/Environmental Context'. This structure ensures the output is exhaustive and covers all facets of the multimodal stream. A specific template would be: 'Describe the main events first, then the specific expressions of the subjects, and finally the exact text seen on screen.'
  - Design Hallucinated-Detail Distractors in multiple-choice formats that include plausible but 'missing' events or 'incorrect' attribute shifts. Create wrong options that are 90% accurate but change a single small detail verified in the trajectory (e.g., 'the shirt was blue' when it was green). This creates a high-stakes verification task where the agent must possess perfect recall of the atomic event log to succeed.
  - Apply a Fact-based Chain-of-Thought (CoT) format for the ground truth answers where every sentence in the description is preceded by its source modality and timestamp. For example: '[Visual 02s] A woman enters. [Audio 03s] She says hello. [OCR 05s] The text "Welcome Home" appears.' This establishes a 'Reproducible Fidelity' standard where every part of the description index is linked to target pixels or waveforms.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

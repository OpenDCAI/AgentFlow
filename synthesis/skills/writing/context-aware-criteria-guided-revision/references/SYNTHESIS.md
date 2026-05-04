# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Draft the revision using a 'Rationale-First' approach: identify the specific professional gap (e.g., missing situational ideal) and write that bridge before smoothing the surrounding prose. This ensures the 'persuasive weight' of the paragraph is restored early in the synthesis pass. For example, if clarifying 'Motivation,' first define the 'Gap' and then align the 'Proposed Solution' to that gap using evidence from the full context.
  - Implement 'Terminological Locking' by ensuring all technical entities (e.g., 'VGAE structure', 'CVG framework') are copied exactly as they appear in the Paper Context T. Do not allow the model to synonymize technical terms (e.g., changing 'auto-scheduler' to 'automated scheduling tool') as this destroys scholarly rigor. A concrete rule: if the context uses 'Ansor' as a baseline, the revision MUST use 'Ansor' and not replace it with 'existing auto-schedulers.'
  - Generate a 'Criteria-Aware Explanation' for every revision made, following the Role 2 instructions from Figure 5. You must explicitly reference specific sections of the paper context that informed your changes (e.g., 'The 22% improvement was integrated from the Results table in Section 4.1'). This proves to the user that the AI acted as a competent collaborator who 'read' the whole draft.
  - Perform a 'Length-Controlled Polish' after the initial synthesis: identify any GPT-style filler words (comprehensive, robust, innovative, pivotal) and replace them with specific, evidence-backed adjectives or delete them entirely. If a sentence says 'Our robust framework provides a pivotal solution,' replace it with 'Our CVG framework achieves 22% higher accuracy.' This enforces the 'LC-Win Rate' standard of expert human preferences.
  - Apply 'Section-Level Mirroring' to the revised span: ensure the 'Aspect' (from Table 2) is satisfied through specific linguistic markers (e.g., using 'In contrast to...' for Existing Solutions or 'Specifically we...' for Key Innovations). This linguistically signals to the conference reviewer that the document follows the expected argumentative structure. A success case is a revision that makes the contribution 'visible' by using an itemized list or a bolded summary sentence as per typical ICLR norms.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

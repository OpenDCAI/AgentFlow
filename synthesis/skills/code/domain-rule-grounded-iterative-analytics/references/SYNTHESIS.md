# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Engineer prompts that explicitly pair a 'Real-World Analytical Goal' with 'Heterogeneous Evidence' and 'Format Guardrails'. The question should ask for a specific factoid or a newly modified dataset, but the evidence to reach it must be split between a structured data file (CSV/JSON/SQL) and an unstructured text manual/PDF. For example, 'Calculate the total fee for Merchant A on [Date] following the regulations in our [Manual].' This forces the agent into an iterative, multi-source reasoning loop. Success must require at least 3-6 distinct extraction and execution steps.
  - Incorporate 'Implicit Dependency Traps' and 'Professional Protocol Asymmetry' where the manual defines a rule that depends on a column or file the agent hasn't looked at yet. For instance, the prompt might ask about 'fraud', but the manual explains that 'fraud' is only counted if the 'Authorization Indicator' column in a secondary registry equals 'Y'. If the agent only filters by a main 'fraud' column without checking the required secondary policy status, it should produce an incorrect answer. This ensures the synthetic task rewards deep, meticulous context integration.
  - Include 'Parameterization Stressors' by creating variations of the task with different time ranges, threshold values, or target entities. The synthetic question shouldn't just be a unique logic puzzle; it should prove that the agent can apply the SAME standard operating procedures (SOPs) from the manual to different physical data subsets. This reflects the design of high-accuracy analytics benchmarks where generalization across varying inputs is the primary differentiator.
  - Command the final output JSON to include a 'Provable Result Chain' that links the final data artifact or aggregate number to intermediate data steps. The synthesis instructions should mandate that the trajectory records 'Sub-Results'—such as the total count of transactions before the conversion rate is applied—to document the logical flow. This allows the evaluator to pinpoint exactly where an agent's reasoning diverged from the ground truth. A specific requirement is: 'Every major business logic choice or mathematical transformation must be justified by identifying the responsible code output in the trajectory step.'
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

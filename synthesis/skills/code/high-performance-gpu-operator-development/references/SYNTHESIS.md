# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Engineer prompts that combine a rigorous mathematical specification with an explicit empirical performance target or speedup goal. Instead of asking to 'make it fast', state requirements like 'the kernel must outperform the standard PyTorch implementation by at least 1.5x on the target hardware'. This forces the agent to move past generic code generation and engage in deep architectural optimization logic.
  - Include 'Hardware Distractor Constraints' such as requiring a specific memory alignment or a limited register budget to force the agent into advanced resource management. For instance, the prompt might specify that the kernel will be run on a device with limited shared memory, requiring the agent to carefully manage its tile sizes. This creates a realistic engineering bottleneck that necessitates the use of more sophisticated tiling strategies.
  - Implement a 'LLM-as-Optimizer' pattern in the synthesis loop where the agent is provided with an archive of previous generations and their associated performance metrics. The question should require the agent to analyze this historical data to identify trends and propose a new configuration that beats all previous records. This reflects the state-of-the-art methodology where agents learn from their own experimental history to achieve expert-level performance.
  - Require the final output to contain a 'Provenance Table' that maps specific mathematical terms in the prompt to the corresponding code snippets in the kernel. The synthesis JSON should include comments such as '# Mapping Eq 1: Indirect address calculation' or '# Optimization: Register reuse for tiling'. This documentation ensures the synthesized data is pedagogically useful for teaching how to translate scientific papers into high-performance source code.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

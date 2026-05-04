# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Engineer 'Compiler-Beating' bottlenecks where a functionally correct C snippet is provided alongside its maximum-optimization compiler assembly output. The prompt should explicitly ask the agent to 'superoptimize' the assembly to beat the current runtime, forcing the agent to find optimizations like manual loop unrolling, instruction fusion, or specialized hardware instruction selection that the compiler heuristics missed.
  - Incorporate 'Integral Score Lures' where a purely time-optimized implementation would violate a memory constraint or a security invariant. The question should ask for 'resource-efficient' code, requiring the agent to find a balanced approach that reduces the product of memory and time. For example, a task where an O(N) time solution with high memory allocation is compared against an O(N log N) solution with zero heap usage, forcing a deductive trade-offs calculation.
  - Design 'Scale-Aware Resource Stressors' where the validation set is small enough for a naive solution, but the 'secret' benchmarking set is large enough to trigger an execution timeout or resource exhaustion. The agent must use its 'Exploration' phase to identify these hidden scale constraints and implement a hardware-efficient approach (like vectorized operations) to survive the stress test. This creates realistic difficulty for testing the agent's architectural foresight and resource stewardship.
  - Implement 'Implicit hardware traps' where the most efficient algorithm requires discovering a niche mathematical invariant or a specific CPU feature not named in the prompt. The question rewards the agent for using a reasoning block to explore multiple pathways—such as bitwise periodicity or population count instructions—before implementing the code. Success is awarded only when the agent uncovers the hidden 'Aha!' moment that collapses the computational complexity.
  - Require the final output to include a 'Metric Delta and Transformation Ledger' that explicitly links each code change to a measured improvement in efficiency percentiles. The synthesis JSON must mandate that the trajectory records: 'Step 1: Removed stack canaries -> Speedup +5%; Step 2: Replaced loop with instruction X -> Speedup +40%'. This provides high-density signal for reward models to distinguish between meaningful engineering gains and superficial code refactoring.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

---
name: autonomous-software-performance-optimization
description: Use this skill when you need to improve the runtime efficiency (latency) or resource footprint (memory) of an existing script or codebase through iterative self-improvement. It is triggered by natural language requests like 'make this run faster', 'optimize the memory usage of this function', 'improve the efficiency score relative to human solutions', or 'generate code that outperforms the standard compiler output'. It guides the agent in using empirical feedback from a sandbox—ranging from high-level algorithmic refinement to low-level assembly superoptimization—to progressively reach peak computational performance.
---

# Skill: autonomous-software-performance-optimization

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to autonomously optimize software artifacts for peak efficiency by establishing a closed-loop Iterative Optimization Framework (IOF) that combines forward code generation with backward empirical evaluation. This involves identifying performance bottlenecks across multiple layers of the software stack—including suboptimal time/space complexity, memory leaks, and redundant low-level instruction sequences—and applying refinements such as algorithmic replacement, hardware-aware instruction selection, or architectural restructuring. Success is measured by the agent's capacity to improve global efficiency metrics (execution time, peak memory, and relative speedup over industry-standard compiler output) while guaranteeing that functional behavior and ABI conventions remain intact.
* **Dimension Hierarchy**: Repository Maintenance and Repair->Software Performance Engineering->autonomous-software-performance-optimization

### Real Case
**[Case 1]**
* **Initial Environment**: A software workspace equipped with a C source function for bitwise manipulation and its corresponding baseline x86-64 assembly compiled with standard industry-level optimizations (e.g., maximum optimization level). The environment includes a benchmarking tool to measure execution latency.
* **Real Question**: Produce a highly optimized version of the provided assembly that remains functionally equivalent to the source but executes significantly faster by utilizing specialized hardware capabilities.
* **Real Trajectory**: Analyze the source C code to identify the logical task as a 'population count' (counting set bits) which currently uses a loop and shift-and-add logic in the baseline assembly. Identify that modern CPUs possess a specialized hardware instruction for this exact pattern. Implement a superoptimized assembly block that replaces the entire loop structure with a single specialized instruction and its associated return sequence. Verify the result through exhaustive unit testing to ensure no divergence from the original input-output behavior.
* **Real Answer**: An optimized assembly implementation where an O(N) loop is reduced to an O(1) single-cycle hardware instruction, achieving a massive speedup over the standard compiler output.
* **Why this demonstrates the capability**: This demonstrates low-level performance engineering by recognizing that even 'fully optimized' compiler output can be surpassed through specialized instruction selection. The agent must bridge the gap between high-level logic and CPU-specific hardware features.
---
**[Case 2]**
* **Initial Environment**: A cloud-based engineering sandbox containing a data processing module where the current implementation is passing tests but performing poorly relative to human-level optimized benchmarks.
* **Real Question**: Optimize the sequence processing module to outperform existing human submissions in terms of execution time and memory integral metrics.
* **Real Trajectory**: Profile the initial solution using a sandbox and find it is in the bottom 30th percentile of efficiency due to redundant object creations. Identify that the current recursive approach causes a high memory footprint during large data spikes. Refactor the implementation into an iterative solution with in-place updates to minimize heap allocations and avoid stack overflows. Execute the refined version multiple times to confirm that both time and memory metrics have moved to the top efficiency tier.
* **Real Answer**: A production-ready iterative script using in-place data transformations that minimizes resource consumption while maintaining functional correctness.
* **Why this demonstrates the capability**: Success requires the agent to iterate beyond simple correctness, using empirical performance comparisons to reach expert-level performance through algorithmic refinement.

## Pipeline Execution Instructions
To synthesize data for this capability, you must strictly follow a 3-phase pipeline. **Do not hallucinate steps.** Read the corresponding reference file for each phase sequentially:

1. **Phase 1: Environment Exploration**
   Read the exploration guidelines to discover raw knowledge seeds:
   `references/EXPLORATION.md`

2. **Phase 2: Trajectory Selection**
   Once Phase 1 is complete, read the selection criteria to evaluate the trajectory:
   `references/SELECTION.md`

3. **Phase 3: Data Synthesis**
   Once a trajectory passes Phase 2, read the synthesis instructions to generate the final data:
   `references/SYNTHESIS.md`

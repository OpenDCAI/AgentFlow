---
name: simulation-driven-stepwise-refinement
description: Use this when the user wants to verify the logic of a plan or code before it is executed, or when they want to 'dry run' a set of instructions using a specific example. Trigger it for requests like 'check if this plan makes sense with an example', 'simulate the steps in your head first', 'trace the logic with input X to see the output', or 'find the mistake in this procedure by walking through it step-by-step with a test case'.
---

# Skill: simulation-driven-stepwise-refinement

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform internal logic verification by simulating the execution of an action program (plan, code, or procedure) step-by-step using a sample input/output pair. This capability enables the agent to identify semantic contradictions, initialization errors, and logical edge cases by comparing the results of a mental dry-run against expected symbolic outcomes before committing to a final artifact.
* **Dimension Hierarchy**: Open-World Real-World Planning->Self-Evolving Strategic Planning->simulation-driven-stepwise-refinement

### Real Case
**[Case 1]**
* **Initial Environment**: A programming workspace with the definition of a custom Tribonacci sequence: tri(1)=3; tri(n)=1+n/2 if even; tri(n)=tri(n-1)+tri(n-2)+tri(n+1) if odd.
* **Real Question**: Generate the first n+1 numbers of the Tribonacci sequence for n=3. Based on the examples, tri(3) should return [1, 3, 2, 8].
* **Real Trajectory**: The agent drafts a plan: 1. Initialize list with [3]. 2. Loop from 2 to n. 3. Calculate even/odd using formulas. Before coding, the agent simulates: For n=2 (even), 1+2/2=2, list becomes [3, 2]. For n=3 (odd), tri(2)+tri(1)+tri(4) = 2+3+3 = 8, list becomes [3, 2, 8]. The simulation shows the list has 3 items, but it needs n+1 (4 items). The agent realizes tri(0)=1 was missing from the plan.
* **Real Answer**: Modified Plan: Initialize the list with [1, 3] to include tri(0), then loop from 2 to n to ensure n+1 elements are returned.
* **Why this demonstrates the capability**: This demonstrates simulation-driven refinement because the agent used a sample input (n=3) to 'walk through' its own generated plan. The simulation revealed a mismatch between the plan's initialization logic and the required output length, allowing the agent to refine the plan's base state before any code was written.
---
**[Case 2]**
* **Initial Environment**: An environment for string and integer manipulation tasks requiring calculations on digit subsets within specified ranges.
* **Real Question**: Given two positive integers a=10 and b=14, return the even digits (not numbers) between a and b in ascending order. For example, 10 and 14 should return [].
* **Real Trajectory**: The agent produces code that loops from 10 to 14 and appends even numbers. During debugging, it simulates input (10, 14): Loop covers 10, 11, 12, 13, 14. 10 is even, 12 is even, 14 is even. Output: [10, 12, 14]. Expected: []. The agent traces the steps and realizes it is collecting the whole numbers (10, 12) rather than the individual digits (1, 0, 1, 2) and checking if those digits satisfy the range/parity constraints.
* **Real Answer**: Corrected Code: Loop through the range, convert each number to a string, iterate over each digit, check if the digit's integer value is even and within the range, and return unique results.
* **Why this demonstrates the capability**: This demonstrates internal debugging through simulation. By performing an execution trace on a failed test case, the agent pinpointed the exact logical divergence where the code processed the 'number' entity instead of the 'digit' entity, enabling a precise structural fix.

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

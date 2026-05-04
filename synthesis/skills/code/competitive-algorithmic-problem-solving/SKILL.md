---
name: competitive-algorithmic-problem-solving
description: Use this skill when the user wants data for solving elite-level algorithmic puzzles (like NOI or ICPC) that require 'aha' moments, advanced mathematical insights, and performance-critical implementations. Trigger it for requests like 'generate NOI-level coding challenges', 'make tasks that need efficient C++ implementations for math puzzles', 'create problems where the agent must refine code based on TLE or MLE feedback', or 'give me high-difficulty competitive programming trajectories'. This skill is specifically for scenarios where naive solutions fail and the agent must utilize an execution feedback loop to reach an AC (Accepted) state under tight time and memory limits.
---

# Skill: competitive-algorithmic-problem-solving

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to solve elite-tier competitive programming problems (e.g., NOI, ICPC, Codeforces) by discovering non-obvious mathematical insights and implementing them with optimal time and space complexity. This involves navigating a rigorous development loop where implementations must be verified against exhaustive test suites rather than just sample inputs, utilizing execution feedback (e.g., Time Limit Exceeded, Memory Limit Exceeded, Runtime Error) to iteratively refine algorithms, and making strategic choices regarding programming languages (e.g., C++ vs. Python) based on the strictness of the computational environment.
* **Dimension Hierarchy**: Competitive Algorithm Engineering->Competitive Problem Solving->competitive-algorithmic-problem-solving

### Real Case
**[Case 1]**
* **Initial Environment**: A competitive programming environment containing a problem description for a 'Path Count' challenge on a tree with 10^5 nodes. The environment provides a C++ compiler (g++), a Python 3.12 interpreter, and a local judge with 50 secret test cases. The time limit is extremely tight (0.5s).
* **Real Question**: Given a tree where each node has a value, count the number of paths between any two nodes such that the sum of values is a prime number. Constraints: N <= 100,000.
* **Real Trajectory**: The agent first drafts a naive O(N^2) depth-first search in Python to solve small cases. It observes a 'Time Limit Exceeded' (TLE) on the local judge for N > 5,000. It then recognizes the problem requires Centroid Decomposition to achieve O(N log N) complexity. To meet the 0.5s limit, the agent switches from Python to C++, implements the decomposition using a recursive structure, and refines the memory allocation to avoid 'Memory Limit Exceeded' (MLE) errors detected during the initial C++ run. Finally, it executes the optimized binary and passes all 50 test cases.
* **Real Answer**: A performance-optimized C++ implementation utilizing Centroid Decomposition and a fast prime-counting sieve to solve the tree-path query within the time and memory bounds.
* **Why this demonstrates the capability**: This demonstrates the capability because the agent moved beyond a simple algorithm to a high-level competitive engineering loop. It diagnosed a failure through TLE feedback, performed a language-level pivot (Python to C++) for performance, and correctly implemented a complex data structure (Centroid Decomposition) required for elite informatics competitions.
---
**[Case 2]**
* **Initial Environment**: A contest-style repository containing a problem about an 'Ideal Game' where two players move on a row of colored cells. The environment includes a skeleton solution file and a judge that returns specific error codes like 'Wrong Answer' (WA) or 'Runtime Error' (RTE).
* **Real Question**: Determine the winner of a game where players alternate painting adjacent colored cells white until no moves are possible. Both play optimally. N up to 10^18.
* **Real Trajectory**: The agent identifies this as a Sprague-Grundy game theory problem but realizes N=10^18 makes standard DP or recursion impossible. It writes a small Python script to print Grundy values for N up to 100 and observes a cyclic pattern with a period of 34 steps. It then performs a 'Refinement under Feedback' by implementing the cyclic parity check in Python. After receiving a 'Wrong Answer' on a boundary case, it identifies that the cycle only stabilizes after an initial offset, corrects the modulo logic, and attains an 'Accepted' status across all scales.
* **Real Answer**: A constant-time O(1) mathematical solution based on the discovered periodicity of Grundy values, correctly handling large coordinate ranges.
* **Why this demonstrates the capability**: This illustrates the 'Observation-heavy' nature of competition-level reasoning. The agent successfully used small-scale brute-force exploration to discover a hidden mathematical invariant (periodicity) and refined its logic based on specific judge feedback to handle massive inputs that would otherwise be computationally intractable.

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

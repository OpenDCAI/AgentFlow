---
name: automated-test-suite-synthesis
description: Use this skill when the user wants to generate high-quality, comprehensive test suites for a software problem or code snippet to ensure it is robust against edge cases and logical errors. It is triggered by natural language requests such as 'generate hard test cases', 'create an adversarial test suite for this algorithmic problem', 'find edge cases for my code', 'make sure my code handles extreme values', or 'build a verifier for this programming task'. It is specifically designed to proactively identify subtle logical flaws by analyzing problem constraints and comparing correct solutions against known error patterns.
---

# Skill: automated-test-suite-synthesis

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to autonomously synthesize comprehensive, high-coverage, and discriminative test suites for software solutions by performing multidimensional analysis of problem constraints and differential analysis of known failure modes. This involves generating executable input-generation scripts (e.g., Python scripts), defining formal mathematical/logic constraints for inputs (e.g., equivalence classes, boundary values, and extremal cases), and utilizing ground-truth interpreters to produce verified outputs that expose subtle logical faults and cognitive biases in code generation.
* **Dimension Hierarchy**: Repository Maintenance and Repair->Software Testing and Verification->automated-test-suite-synthesis

### Real Case
**[Case 1]**
* **Initial Environment**: A software workspace contains a problem description for a 'Grid Path' complexity challenge where an agent must find a path between two nodes on an $N imes M$ grid with obstacles. The environment provides access to several correct ground-truth solutions and a history of human submissions that failed on hidden test cases.
* **Real Question**: Generate a set of adversarial test cases that can detect subtle logical errors in solutions that pass standard sample tests but might fail on large-scale grids or specific obstacle patterns.
* **Real Trajectory**: The agent first performs a multidimensional analysis on the correct solutions to identify the 'Defense Pattern', such as how they handle $N=1$ or grids where the start and end are the same point. It then compares a successful submission with an incorrect human submission to find the 'divergence input' where their behaviors differ. The agent identifies specific boundary values like $(N=200,000, M=1)$ and obstacle-dense patterns. It then writes a Python Case Script to programmatically generate these specific adversarial inputs. Finally, the agent validates the inputs with a self-validation script and runs a ground-truth interpreter to produce the final test outputs.
* **Real Answer**: A comprehensive test suite containing large-scale adversarial grids and edge-case obstacle patterns that successfully identifies logical flaws in 'plausible' but incorrect solutions.
* **Why this demonstrates the capability**: This demonstrates the capability because the agent moved beyond random input generation. It used both correct and incorrect solution traces to identify the precise sub-space where common logical errors occur, then programmatically synthesized adversarial inputs that target those specific weaknesses.
---
**[Case 2]**
* **Initial Environment**: A development environment for a 'Modular Inverse' mathematical problem where $N$ up to $10^{18}$ is provided. The task is to calculate the modular inverse under a prime modulus $P$.
* **Real Question**: Create a test suite to detect if an implementation correctly handles the case where $N$ and $P$ are not coprime, or where the result overflows a 64-bit integer during intermediate calculations.
* **Real Trajectory**: The agent analyzes the problem constraints and identifies that naive implementations often fail when the prime is extremely large ($> 2^{31}-1$). It performs a differential analysis by comparing a 'naive' extended Euclidean algorithm and a 'robust' version using arbitrary-precision arithmetic. It identifies that the common error is an integer overflow that occurs during the intermediate multiplication step. The agent writes a generator script targeting boundary values near $10^{18}$ and uses math explanations to specifically verify the 'no inverse exists' logic. The resulting test suite includes several prime and non-prime $P$ values at the maximum scale.
* **Real Answer**: A test suite targeting overflow boundaries and non-coprime edge cases for modular arithmetic.
* **Why this demonstrates the capability**: The agent identifies a specific 'cognitive bias' (the assumption that inputs fit in a standard integer) and uses differential analysis to generate cases that specifically challenge that assumption. This requires mapping abstract mathematical constraints to concrete, executable input scripts.
---
**[Case 3]**
* **Initial Environment**: A contest-style repository containing a complex string-matching problem involving regular expressions and multi-language character sets. The environment includes 10 correct solutions and 50 'Wrong Answer' submissions from humans.
* **Real Question**: Identify the distinct error patterns in the provided failed submissions and synthesize a minimal set of test cases that covers all unique failure modes.
* **Real Trajectory**: The agent executes all incorrect submissions against a large pool of random inputs to identify 'failing seeds'. It then uses a diversity-ratio analysis to cluster these failures into unique 'Error Patterns', such as failure to handle nested brackets or multi-byte UTF-8 sequences. For each unique pattern, it implements a specialized Python script that generates the simplest possible input that reveals that specific error. It verifies the suite's efficiency by confirming that the number of tests is minimized while the 'Detection Rate' remains maximized. Finally, it uses a self-validation pass to ensure every generated string is a valid challenge according to the problem rules.
* **Real Answer**: A minimized, highly discriminative test suite where each test case is designed to capture a unique, non-redundant logical error pattern identified from human bugs.
* **Why this demonstrates the capability**: This shows the agent's ability to manage 'inter-test correlation'. By focusing on 'distinct error pattern coverage', the agent avoids redundant testing and builds a more efficient verifier that is optimized for both speed and diagnostic power.

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

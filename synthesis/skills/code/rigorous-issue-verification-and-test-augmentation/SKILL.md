---
name: rigorous-issue-verification-and-test-augmentation
description: Use this skill when a user wants to proactively identify gaps in a software project's test suite, generate new reproduction tests for a bug (TDD), or rigorously verify an issue resolution. It is specifically triggered by everyday requests like 'check if these tests are enough for the bug', 'make a test that shows the bug happening', 'write a reproduction script for this issue', 'make sure the fix handles all edge cases', or 'try to find where the original developer missed a scenario'. This skill ensures that a bug fix is not just superficially correct but grounded in an executable fail-to-pass signal and robust against unhandled boundary conditions.
---

# Skill: rigorous-issue-verification-and-test-augmentation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform automated reproduction test synthesis and patch verification by analyzing software repositories and issue descriptions to establish an executable fail-to-pass signal. This involves hierarchical localization of test and focal files (file-to-function), requirements extraction from natural language reports, and the execution of a self-reflective action planner to synthesize high-fidelity, issue-grounded unit tests. Success is determined by the test's ability to reproduce the issue on the baseline code (Fail), validate the correction on the new code (Pass), and maximize line coverage on the logical changes introduced by the patch.
* **Dimension Hierarchy**: Repository Maintenance and Repair->Issue-Driven Repair->rigorous-issue-verification-and-test-augmentation

### Real Case
**[Case 1]**
* **Initial Environment**: A Python software repository for data visualization containing a library module for statistical calculations. A specific issue report indicates that the `PolyFit` function fails to handle missing values (NaN) in the input data, but the existing test suite only checks for cases where both coordinate axes have missing values.
* **Real Question**: Generate an augmented reproduction test to verify that `PolyFit` correctly handles scenarios where only one axis, specifically 'x', has missing data, ensuring the fix is robust and the current version fails.
* **Real Trajectory**: The agent first performs a hierarchical localization to identify 'regression.py' as the most relevant test file and 'TestPolyFit' as the target class. It plans a set of actions: reading the existing 'TestPolyFit' code, then writing a new test 'test_missing_data' that constructs a DataFrame with np.nan exclusively in the 'x' column. It uses a static analyzer to fix missing imports for numpy and pandas, adds the test function to the class, and executes it. The agent confirms the test fails on current code with a ValueError, effectively reproducing the reported bug.
* **Real Answer**: A new test function 'test_missing_data' within 'test_regression.py' that creates a DataFrame with np.nan in 'x', asserting that the return value matches a drop-na baseline, which fails on the unpatched implementation.
* **Why this demonstrates the capability**: This case demonstrates the ability to translate a natural language bug report ('fails on NaN in x') into a specific 'fail-to-pass' test. It highlights the use of localization to find the right class and the synthesis of an issue-grounded test that exposes an unhandled logical state in the existing codebase.
---
**[Case 2]**
* **Initial Environment**: A large-scale project workspace for a documentation framework. An issue report details an error where a specific metaclass fails to handle Python @property decorators during docstring inheritance from parent classes.
* **Real Question**: Identify the relevant code sections for the metaclass bug and generate an augmented test that triggers the inheritance failure for decorated properties.
* **Real Trajectory**: The agent performs a search for the metaclass name and retrieves 10 candidate files, narrowing down to the utility module responsible for class manipulation. It develops a self-reflective plan to read the 'PropertyDocstrings' test class and then modifies it to include a multi-level inheritance check. The agent writes a test case defining a Parent with a docstring-heavy property and a Child that inherits it, then verifies that the child's property docstring is empty in the current version. Finally, it uses an import fixer to resolve missing dependencies from the internal utility package.
* **Real Answer**: A modification to the internal test suite that includes a complex hierarchy of classes with @property methods, confirming that docstrings are not propagated in the buggy version of the library.
* **Why this demonstrates the capability**: Success requires the agent to understand the architectural implications of the issue (metaclass inheritance) and extend a simple flat test case into a structured reproduction script. This proves the agent can use self-reflective planning to bridge the gap between abstract issue descriptions and executable verification code.

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

---
name: interactive-underspecified-issue-resolution
description: Use this skill when the user provides a software bug report or feature request that is vague, missing error logs, or lacks specific file locations. Trigger this for requests like 'fix the crash in the login module' (without giving the log), 'the update button doesn't work', 'make the questions a bit clearer', or 'there is an error in the data processing part'. This skill is essential when you feel you are guessing about where the bug is or what the expected behavior should be; it guides you to detect the ambiguity and ask the user for the missing details before you start writing code.
---

# Skill: interactive-underspecified-issue-resolution

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to resolve software engineering tasks starting from underspecified or ambiguous instructions by proactively detecting missing technical context, formulating targeted clarifying questions for the user, and integrating retrieved information into the repair trajectory to minimize resource wastage and misalignment.
* **Dimension Hierarchy**: Repository Maintenance and Repair->Issue-Driven Repair->interactive-underspecified-issue-resolution

### Real Case
**[Case 1]**
* **Initial Environment**: A Python repository and a brief issue report stating: 'The InheritDocstrings metaclass fails to handle properties.' No traceback, file path, or code example is provided. The agent has tools to search the codebase and communicate with a user who has the full context.
* **Real Question**: Fix the InheritDocstrings metaclass because it fails to handle properties.
* **Real Trajectory**: The agent first performs a repository-wide grep for 'InheritDocstrings' to locate the definition in 'astropy/utils/misc.py'. It observes that the implementation uses 'inspect.isfunction', which skips Python properties. Recognizing that the user hasn't specified the exact failure mode (e.g., missing docstrings vs. runtime crash), the agent asks: 'Does this refer specifically to @property decorators and should they inherit docstrings from the parent?' The user confirms. The agent then implements the fix using 'isinstance(obj, property)' and verifies it with a new test case.
* **Real Answer**: Modified 'astropy/utils/misc.py' to include property types in the docstring inheritance logic, ensuring children classes inherit documentation for decorated properties.
* **Why this demonstrates the capability**: This case demonstrates the capability because the initial instruction was underspecified regarding the implementation of 'properties'. The agent successfully detected the ambiguity, asked a targeted question to confirm the 'behavioral' expectation, and used that information to avoid making incorrect assumptions about the fix.
---
**[Case 2]**
* **Initial Environment**: A large Django-based repository. The user provides a summary: 'Migrate signals verbose stdout emissions are not capturable.' Detailed context about verbosity flags and specific function hooks is hidden.
* **Real Question**: Resolve the issue where migrate signals cannot capture stdout emissions.
* **Real Trajectory**: The agent identifies multiple functions related to migration signals (emit_pre_migrate_signal and emit_post_migrate_signal). It realizes it is unclear whether the user intends for the output to be redirected to a custom stream or simply suppressed under certain verbosity levels. The agent asks: 'Should the output be redirected to the provided stdout stream inside the signal handlers, and does this affect the -verbosity flag?' The user provides the specific requirement for the stream redirection. The agent then modifies the signal emission logic to accept and use the 'stdout' argument.
* **Real Answer**: The migration signal functions now correctly accept an 'stdout' parameter, allowing 'call_command' to capture output instead of polluting the system's global stdout.
* **Why this demonstrates the capability**: The agent avoided 'blind exploration' by identifying that 'capturability' is a vague technical requirement. By eliciting the specific architectural design choice (stream redirection) from the user, it ensured the patch was aligned with the intended infrastructure change.

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

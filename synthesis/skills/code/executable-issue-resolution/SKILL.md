---
name: executable-issue-resolution
description: Use this skill when the user wants bug-fix data for normal repository issues where the answer should come from reading an issue, navigating unfamiliar codebases, editing code, and running tests. Trigger it for requests like 'fix the NaN loss in my ML training script', 'solve issues in a massive codebase', 'fix this data race', 'debug my SQL query', or 'resolve this executable failure'. It covers standard software environments, database architectures, and systems infrastructures, emphasizing the fix-test-verify loop.
---

# Skill: executable-issue-resolution

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to resolve a concrete repository issue by translating a human-authored issue description or automated machine diagnostic log into a structured repair plan. This involves executing systematic structural audits in diverse architectures (including Web, Systems, Databases, and Machine Learning models), locating the relevant program state, modifying code iteratively over long-horizon trajectories, and validating the fix empirically through test suites without introducing regressions.
* **Dimension Hierarchy**: Repository Maintenance and Repair->Issue-Driven Repair->executable-issue-resolution

### Real Case
**[Case 1]**
* **Initial Environment**: A Python repository contains a data export module, an issue report describing that CSV exports silently drop timezone offsets, and a robust execution test suite preventing secondary functional breakages.
* **Real Question**: Fix the export logic so timestamps retain timezone information in generated CSV files.
* **Real Trajectory**: Inspect the serializer used by the export path, trace how datetime objects are conventionally transformed, modify the formatting branch to preserve aware datetimes, and run the targeted export test plus the broader export suite files.
* **Real Answer**: The export path emits ISO-8601 timestamps containing explicit timezone values, and the failing test transitions cleanly from Error to Success.
* **Why this demonstrates the capability**: The task establishes foundational issue-resolution bounds: finding the unmentioned file, inferring the execution logic, isolating precisely where state modifications occur, and requiring explicit verification of the resolution signal.
---
**[Case 2]**
* **Initial Environment**: A large C++ repository utilizing a distributed build system is equipped with a concurrent thread sanitizer. The diagnostic build log details a 'data_race' runtime error during concurrency tests.
* **Real Question**: Fix the data race reported by the thread sanitizer in the networking module as identified in the provided log.
* **Real Trajectory**: Examine the sanitizer log to isolate specific memory addresses mapping to shared data. Create a mutex-based synchronization lock over the critical section across files, preventing concurrent read/write execution, while avoiding newly formed dependency deadlocks.
* **Real Answer**: The shared memory accesses are correctly synchronized, preventing the race condition and achieving a clean build from the C++ compiler checking suite.
* **Why this demonstrates the capability**: Extracting information directly from machine-level compiler/sanitizer reports instead of natural language proves the ability to map physical error logs seamlessly into structural repository adjustments.
---
**[Case 3]**
* **Initial Environment**: A PostgreSQL database contains an 'account' table and a 'loan' table. The user provides a faulty query using a UNION operator that is producing duplicate entries despite the intent to list unique account IDs. The environment allows for arbitrary SQL execution to probe the tables.
* **Real Question**: Debug an existing SQL query combining data from the account and loan tables, which is incorrectly generating duplicates, ensuring the output respects the strict uniqueness constraint.
* **Real Trajectory**: The agent uses COUNT queries to profile the data distribution, confirming standard UNION fails due to differing sorting columns. It researches dialect-specific capabilities, implements a PostgreSQL `DISTINCT ON` wrapper, and reruns the subqueries against the test harness to confirm the duplicates are definitively eliminated.
* **Real Answer**: The query is updated to wrap the UNION within a `SELECT DISTINCT ON` block, aligning the logic to the schema and successfully handling the edge cases.
* **Why this demonstrates the capability**: It demonstrates mapping the classic debugging loop—reproduce, probe state, apply patch, verify—to a specialized database framework. The agent successfully treats the SQL execution engine feedback just as it would a Python stack trace to achieve issue resolution.

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

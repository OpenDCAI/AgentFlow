---
name: multi-turn-instruction-following-and-refinement
description: Use this skill when a user wants to iteratively update or refine code through multiple rounds of instructions, especially when new constraints (like error handling, edge cases, or style rules) are added one by one. It is triggered by requests like 'keep the old behavior but add this new rule', 'refine the function I just wrote to handle empty inputs', 'don't forget the case sensitivity I mentioned earlier', or 'update the code to match my new feedback'. Use this to ensure the agent doesn't 'forget' previous requirements while implementing new ones.
---

# Skill: multi-turn-instruction-following-and-refinement

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to maintain logical and functional consistency across multi-turn code generation sessions by strictly adhering to a cumulative set of verifiable instructions. This involves managing conversational context to prevent 'instruction forgetting,' where previously satisfied constraints—such as input validation, edge-case handling, or specific code standards—are inadvertently discarded or regressed during subsequent refinement rounds.
* **Dimension Hierarchy**: Repository Maintenance and Repair->Issue-Driven Repair->multi-turn-instruction-following-and-refinement

### Real Case
**[Case 1]**
* **Initial Environment**: A standalone Python development environment is provided with a blank workspace. The user intends to build a string utility function.
* **Real Question**: Round 1: Write a function called 'remove_dirty_chars' to remove characters from the first string which are present in the second string. \nRound 2: Refine the function to handle case-insensitive character removal. Ensure that the original case status of the first string is retained when filtering characters.
* **Real Trajectory**: The agent first implements a basic list comprehension to filter characters. After the second instruction, it modifies the logic to convert the 'dirty' string to a set for performance and uses lowercase comparisons for the filter while preserving the character from the original string in the final join. It verifies that 'A' is removed if 'a' is in the dirty set, but the resulting string retains its original capitalization for non-dirty characters.
* **Real Answer**: def remove_dirty_chars(s, t):\n dirty_set = {char.lower() for char in t}\n return ''.join([char for char in s if char.lower() not in dirty_set])
* **Why this demonstrates the capability**: This case demonstrates multi-turn refinement where the agent must integrate a new constraint (case-insensitivity) while strictly adhering to a functional constraint from the previous turn (preserving original case status). It tests the model's ability to evolve a solution without losing track of nuanced behavioral requirements.
---
**[Case 2]**
* **Initial Environment**: A repository-level context for a network utility project is provided, containing the 'NetstringSocket' class definition which lacks input validation logic.
* **Real Question**: The 'setmaxsize' function in the NetstringSocket class should be updated. It must raise a ValueError if the 'maxsize' parameter is not a positive integer or zero.
* **Real Trajectory**: The agent locates the target class in the 'socketutils.py' file. It identifies the existing 'setmaxsize' method and inserts a guard clause using 'isinstance(maxsize, int)' and a comparison 'maxsize < 0'. It then confirms that the modification does not interfere with the existing socket initialization logic.
* **Real Answer**: def setmaxsize(self, maxsize):\n if not isinstance(maxsize, int) or maxsize < 0:\n raise ValueError("maxsize must be a non-negative integer")\n self.maxsize = maxsize
* **Why this demonstrates the capability**: This illustrates 'Exception Handling' as a verifiable instruction. The agent must ground its implementation in the existing class structure and apply a specific, objectively testable validation rule that was missing from the initial version.
---
**[Case 3]**
* **Initial Environment**: A large-scale project workspace for an infrastructure toolkit. The agent is working within the 'MRJob' class, which handles Hadoop streaming tasks. The state of the function 'set_status' is currently basic and lacks type documentation.
* **Real Question**: Round 1: Implement 'set_status' to print the job status via stderr. \nRound 2: Ensure that the 'set_status' function is fully documented with parameter and return type annotations. \nRound 3: The status message should be encoded to utf-8 before being written to stderr.
* **Real Trajectory**: The agent first writes the stderr writing logic. In the next turn, it adds ': str' and '-> None' type hints. In the third turn, it adds the '.encode("utf-8")' call while ensuring the type hints and the stderr write logic remain intact. It avoids the common error of removing the encoding logic while trying to satisfy the 'documentation' requirement in a later round.
* **Real Answer**: def set_status(self, msg: str) -> None:\n # verification logic... \n status_message = f"reporter:status:{msg}\n".encode("utf-8")\n self.stderr.write(status_message)
* **Why this demonstrates the capability**: This represents a long-horizon refinement across functional (encoding) and non-functional (type hints) requirements. Success is measured by the ability to accumulate these requirements without 'forgetting' the encoding logic or the documentation standards from previous turns.

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

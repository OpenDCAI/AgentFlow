---
name: interactive-tool-augmented-logic-synthesis-and-orchestration
description: Use this skill when the user wants data for solving software logic or algorithmic problems where the agent must interactively call specialized tools (representing atomic code functions) rather than writing a single code block. Trigger it for requests like 'solve this logic puzzle as an agent', 'use these coding tools to find the hidden answer', 'create interactive algorithmic tasks', or 'give me multi-turn tool-use data for code agents'. This is crucial when the agent must solve a task by actively exploring state feedback (e.g., querying indices, checking intermediate calculations) to arrive at a final answer.
---

# Skill: interactive-tool-augmented-logic-synthesis-and-orchestration

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to resolve complex software logic and state-based algorithmic tasks by orchestrating a suite of atomic, domain-specific tools that abstract internal program logic (e.g., search, stack manipulation, DP table updates). This involves performing multi-turn exploration to retrieve partial environmental states, interpreting tool-execution feedback (success/error) to refine subsequent actions, and composing these modular steps into a coherent workflow that achieves a verifiable terminal objective.
* **Dimension Hierarchy**: Repository Maintenance and Repair->Complex Software Feature Engineering->interactive-tool-augmented-logic-synthesis-and-orchestration

### Real Case
**[Case 1]**
* **Initial Environment**: A sorted array of integers is hidden within the environment. The agent only knows the length of the array (N) and a target value (K).
* **Real Question**: Find the number in the sorted array that is closest to K. If two numbers have the same absolute difference, return the smaller one.
* **Real Trajectory**: The agent calls Observe() to get n=5, K=8. It then performs a binary search by calling LookUpPos(2) which returns Arr[2]=9. Sensing the target might be to the left, it calls LookUpPos(1) returning Arr[1]=5. Comparing |9-8|=1 to |5-8|=3, it identifies 9 as the closest. It calls Done(answer=9).
* **Real Answer**: 9
* **Why this demonstrates the capability**: This case demonstrates the agent's ability to use atomic lookup tools to perform an interactive binary search. It requires the agent to manage the state of its search range (left/right) across multiple turns and make an optimal decision based on the values retrieved from the environment rather than having the full array visible in the prompt.
---
**[Case 2]**
* **Initial Environment**: A histogram is represented as a series of bars with varying heights. The agent can only see the number of bars but must query each bar's specific height.
* **Real Question**: Calculate the maximum rectangular area that can be formed by these consecutively arranged bars.
* **Real Trajectory**: The agent calls Observe() to see there are 6 bars. It calls GetBarHeight(2) and GetBarHeight(3), receiving 5 and 6. It uses PushToStack(2) and PushToStack(3) to track increasing heights. Upon calling GetBarHeight(4) and seeing the height drop to 2, it calls PopAndCalculateArea() to find the area formed by the previous peaks (5 and 6). After iterating through all bars using these stack tools, it identifies the max area is 10.
* **Real Answer**: 10
* **Why this demonstrates the capability**: This demonstrates 'tool-based reasoning' for a stack-based algorithm. The agent must orchestrate the stack operations (Push/Pop) in synchronization with environment observation to solve a dynamic programming/stack problem, ensuring it correctly tracks the 'active' rectangles across turns.
---
**[Case 3]**
* **Initial Environment**: Two strings are hidden in the environment. The agent can query the length and specific characters at any index of either string.
* **Real Question**: Compute the minimum number of operations (insert, delete, replace) required to convert String A to String B.
* **Real Trajectory**: The agent identifies the task as finding the Edit Distance. It calls ObserveStrings() to get the lengths. It uses a SetDPValue(i, j, value) tool to build the distance table based on character comparisons retrieved via GetCharAt(index). It iteratively calculates the optimal sub-problems until the final table entry is populated. It calls Done(final_value).
* **Real Answer**: 3
* **Why this demonstrates the capability**: The agent must bridge the gap between abstract DP logic and tool-mediated execution. It proves it can maintain a complex intermediate state (the DP table) across many turns, verifying that its tool calls accurately reflect the mathematical requirements of the algorithm.

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

---
name: closed-loop-instruction-validation-and-recovery
description: Trigger this skill when the task requires evaluating real-time feedback, parsing execution traces to verify functional correctness, breaking retry deadlocks, or waiting for conditional environmental/social states to synchronize. Plain-language triggers include: 'watch for errors and try again', 'check the execution logs to verify pacing', 'wait for the person to take the delivery', 'stop if you are stuck in a loop', and 'ensure the task is functionally successful before moving on'.
---

# Skill: closed-loop-instruction-validation-and-recovery

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability evaluates interleaved execution, real-time deadlock breaking, temporal sequence auditing, and environmental synchronization. The agent must perform conditional state verification, manage diverse system feedback (like spatial boundary errors or inventory blocks), diagnose repetitive retry-loops to trigger metacognitive replanning, audit empirical execution traces/logs to verify that programmatic outputs achieved the desired physical outcomes, and manage conditional waiting loops for asynchronous events (including human interaction hand-offs).
* **Dimension Hierarchy**: Continual and Safe Task Execution->Stateful Adaptation->closed-loop-instruction-validation-and-recovery

### Real Case
**[Case 1]**
* **Initial Environment**: A kitchen containing a refrigerator and a counter. The agent is at the starting position with empty hands.
* **Real Question**: Check if there are any bananas in the fridge. If not, take one banana from the kitchen counter and put it in the fridge.
* **Real Trajectory**: The agent sequentially plans to test the fridge state. It acts to 'Open' the fridge and processes the visual feedback token representing 'banana == False'. With this confirmation, it branches smoothly to fetch the replacement counter item instead of terminating.
* **Real Answer**: Task completely resolved because a conditional pre-task feasibility check successfully directed the dynamic fetching routine.
* **Why this demonstrates the capability**: Validates interleaved state discovery. The multi-stage objective depends strictly on in-situ visual feedback gathered at step 1 seamlessly routing into the subsequent branch without a planning crash.
---
**[Case 2]**
* **Initial Environment**: A scientific research simulator where an agent operates a specimen scope. A bee hive contains multiple bees flying tightly together.
* **Real Question**: Focus on the adult bee to determine its life span.
* **Real Trajectory**: The agent attempts the 'focus' command three times. Each time it returns an error 'Ambiguous target'. Recognizing the repeated identical failure pattern, the agent breaks the loop, triggering an alternate exploration strategy to find a separated bee.
* **Real Answer**: Repetitive attempt sequence terminated; agent branched to an alternate sub-task after diagnosing a command-level deadlock.
* **Why this demonstrates the capability**: This case tests deadlock breaking and metacognition. The agent avoids the fatal infinite-retry failure mode by using its own execution history to veto a stuck loop.
---
**[Case 3]**
* **Initial Environment**: Kitchen counter. Agent carrying a fragile item on a tray. Target recipient is standing adjacent.
* **Real Question**: Bring the item to the user, wait for them to take it, then return to base.
* **Real Trajectory**: The agent navigates to the user. It enters a deliberate active wait-state. By monitoring its perceptual trace, it detects when 'Tray Load = 0', signaling the conditional social-handshake is complete, and solely then triggers the base-return plan.
* **Real Answer**: Hand-off verified; agent synchronized departure exclusively with the empirical state change signifying a completed transfer.
* **Why this demonstrates the capability**: Proves the agent handles asynchronous conditional state-waiting. The action loop halts until the required environmental change (a human removing an item) is empirically logged, proving dynamic synchronization.
---
**[Case 4]**
* **Initial Environment**: Industrial workstation workspace where the agent controls a scanning head tracing a rectangle.
* **Real Question**: Review your motor logs for the scan mission. Does the set of visited coordinates in your trace cover the required area with the correct pacing?
* **Real Trajectory**: The agent ingests its chronological historical execution record, auditing coordinates visited and time delays, algorithmically confirming that the traversed empirical vectors align identically with the tasked coverage region.
* **Real Answer**: Execution trace verified for completely accurate 3D spatial coverage and chronological pacing.
* **Why this demonstrates the capability**: Tests retrospective trace validation. The agent confirms closed-loop functional capability not by assuming its commands worked, but by auditing the empirical time-stamped history of the environment's physics engine.

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

---
name: temporal-gui-precision-control
description: Use this skill when the task requires actions to be timed perfectly, such as waiting for a hidden element to appear, holding a button for a specific duration, or clicking a target that is moving or changing. Trigger it for requests like "wait a few seconds before acting," "hold the button down," "be quick and tap it multiple times," "click it three times as it moves," or "patience is required to find the password."
---

# Skill: temporal-gui-precision-control

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to execute GUI actions within specific temporal constraints, encompassing duration-based interactions (holding elements), time-delay synchronization (waiting for state transitions), and high-frequency or reactive execution (clicking moving targets or rapid-fire tapping). This requires the agent to coordinate its internal execution clock with dynamic on-screen indicators like timers, progress bars, or movement patterns.
* **Dimension Hierarchy**: Reliable and Aligned Operation->Safe and Efficient Control->temporal-gui-precision-control

### Real Case
**[Case 1]**
* **Initial Environment**: A web browser is open on a blank page with a single text box and a hidden label that only populates after a server-side delay. There are no immediate buttons to click.
* **Real Question**: Patience is a virtue. Wait for the perfect amount of time to reveal the password and enter it below.
* **Real Trajectory**: Navigate to the designated URL, capture the static screen and observe the 'Waiting' message, initiate a polling or 'Wait' action to monitor the DOM for updates, identify the password string once it renders after 10 seconds, and type the revealed code into the input field.
* **Real Answer**: The password revealed by the delay is successfully entered.
* **Why this demonstrates the capability**: This case tests the agent's ability to handle temporal gaps where no immediate action leads to success. The agent must understand that the environment is in a transient state and must maintain focus over a duration-based 'no-op' period before the goal becomes attainable, demonstrating stable time-delay synchronization.
---
**[Case 2]**
* **Initial Environment**: A GUI desktop environment shows a single large button labeled 'Hold to Unlock'. The system metadata indicates that the button only registers a 'Success' state if the mouse-down event persists for more than 3000 milliseconds.
* **Real Question**: Press and hold the button for exactly 3 seconds to get the secret code.
* **Real Trajectory**: Locate the 'Hold to Unlock' button, perform a 'MouseDown' action at the center coordinates, maintain the button-down state while monitoring the system clock or an on-screen progress bar, and execute the 'MouseUp' action only after exactly 3.0 seconds have elapsed.
* **Real Answer**: The secret code is displayed after the 3-second hold.
* **Why this demonstrates the capability**: Duration-based interaction is a core precision capability. The agent must move beyond discrete clicks to manage the 'state of the button' over time, precisely calculating when to terminate an action based on a temporal threshold, which is a key requirement for advanced GUI controls like sliders or secure toggles.
---
**[Case 3]**
* **Initial Environment**: An interactive canvas application features a 'Bullseye' target that moves in a randomized linear path across the viewport, increasing in velocity every time it is successfully hit.
* **Real Question**: Click the moving target three times - but watch out, it gets faster!
* **Real Trajectory**: Identify the target's starting position and motion vector, calculate the intersection of the cursor and the target's future coordinates, execute a precise click on the moving object, and repeat the prediction-action cycle two more times as the environment's speed increases.
* **Real Answer**: The target is hit 3 times and the task signals completion.
* **Why this demonstrates the capability**: This requires reactive temporal-spatial coordination. The agent must process visual updates in real-time and synchronize its action dispatch with the moving window of opportunity, testing high-frequency precision control under dynamic conditions.

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

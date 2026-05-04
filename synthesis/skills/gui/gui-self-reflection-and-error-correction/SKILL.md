---
name: gui-self-reflection-and-error-correction
description: Use this skill when the agent needs to handle environmental obstacles like pop-up advertisements blocking the target, or when it must correct common interactive widget errors such as pre-filled text in form fields and incorrect date-picker formats. Trigger it for requests like 'something is in the way of the button,' 'there is already text in the box I need to type in,' 'the date picker keeps resetting,' or 'close whatever is blocking the screen before you continue.' This skill focuses on detecting UX disruptions and state-entry conflicts to ensure the visual outcome matches the specific user goal despite environmental noise.
---

# Skill: gui-self-reflection-and-error-correction

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to continuously monitor graphical outcomes against a target goal to recognize and mitigate deviations caused by self-induced errors or real-world environmental anomalies, specifically addressing UX disruptions like pop-up overlays, state-entry conflicts such as pre-filled input buffers, and widget-dependent constraints like specific date/time formats. This requires overcoming 'Perception Drift'—where internal history conflicts with a reset or obscured UI—and performing 'Outcome Evaluation' to distinguish between a task that is truly complete and one that remains blocked by artifacts like interstitial advertisements or incorrect auto-formatting in complex interactive widgets.
* **Dimension Hierarchy**: Reliable and Aligned Operation->Error-Resilient Self-Correction->gui-self-reflection-and-error-correction

### Real Case
**[Case 1]**
* **Initial Environment**: A web application for color selection is open. The 'Hex Code' input field is pre-populated with a default '#' character from a previous session, but the user's intended code also starts with '#'.
* **Real Question**: Change the primary color to #EDC55E.
* **Real Trajectory**: 1. Locate the color input field on the canvas. 2. Observe that the field already contains a '#'. 3. Analyze the conflict where simply typing the full code would result in '##EDC55E', causing a format error. 4. Execute a click on the field, backspace to clear the pre-existing '#', and then type the fresh code '#EDC55E'. 5. Verify the color box updates to the specific shade of gold.
* **Real Answer**: The primary color is changed to #EDC55E after clearing the pre-filled buffer.
* **Why this demonstrates the capability**: This case demonstrates reflection on state-entry conflicts. The agent must recognize that a pre-existing character in the input buffer acts as a 'state pollutant' and proactively perform a corrective 'clean-up' interaction before continuing with the primary intent to avoid a logic failure.
---
**[Case 2]**
* **Initial Environment**: An airline booking website is rendered in the browser. A large 'Sign Up for Savings' pop-up modal has appeared in the center of the screen, completely obscuring the language selection menu located in the header.
* **Real Question**: Set the language to Portuguese.
* **Real Trajectory**: 1. Perform a visual sweep and identify the target language menu area. 2. Recognize that the 'Sign Up' modal is a prioritized overlay blocking the interactive nodes of the header. 3. Locate the 'X' or 'Close' button on the top-right of the modal. 4. Dismiss the pop-up and verify that the header elements are now fully visible and active. 5. Click the language menu and select 'Portuguese'.
* **Real Answer**: The language is set to Portuguese after dismissing the blocking pop-up modal.
* **Why this demonstrates the capability**: This demonstrates recovery from UX disruptions. Instead of failing due to a 'missing' button, the agent identifies the causal reason—the pop-up—and adaptively modifies its trajectory to remove the obstacle, restoring the environmental state needed for the core task.
---
**[Case 3]**
* **Initial Environment**: A complex date-picker widget is open on a travel portal. The widget enforced a strict 'MM/DD/YYYY' entry format, but the agent's internal prior assumes 'YYYY-MM-DD'.
* **Real Question**: Select March 21 2025 as the departing date.
* **Real Trajectory**: 1. Click the 'Departing' date input. 2. Type '2025-03-21' based on a general habit. 3. Observe the UI response where the field turns red or resets to blank. 4. Reflect on the error by inspecting the grey placeholder text which reads 'MM/DD/YYYY'. 5. Correct the action by entering '03/21/2025' and verify that the date-picker calendar highlights the correct day in March.
* **Real Answer**: The date March 21 2025 is successfully selected using the MM/DD/YYYY format.
* **Why this demonstrates the capability**: This illustrates self-correction of widget-dependent constraints. The agent must process the negative outcome of its first attempt, identify the specific format requirement through visual cues (placeholder text or error signals), and pivot to a format-aligned interaction sequence.

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

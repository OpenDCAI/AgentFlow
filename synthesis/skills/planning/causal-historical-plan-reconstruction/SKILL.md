---
name: causal-historical-plan-reconstruction
description: Use this when the agent needs to figure out what happened in the past to reach its current situation, especially if it is confused or the environment changed unexpectedly. Trigger it for requests like 'how did I get to this screen?', 'reconstruct the steps leading to this error', 'check if my last few clicks actually worked', 'what were the previous actions that caused this state?', or 'verify the history of this task before moving forward.'
---

# Skill: causal-historical-plan-reconstruction

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform causal back-tracking and retrocausal inference to reconstruct the sequence of historical actions and environmental state transitions that resulted in the current observation. This capability enables the agent to resolve state-transition ambiguities, verify the success of preceding operations, and rectify its internal world model through reflective analysis of the causal chain linking the starting state to the present configuration.
* **Dimension Hierarchy**: Open-World Real-World Planning->Self-Evolving Strategic Planning->causal-historical-plan-reconstruction

### Real Case
**[Case 1]**
* **Initial Environment**: A mobile device is open to the home screen. The goal is to set the recording quality of a sound recorder app to 96kbps. The agent has already performed some actions but is now on a settings page that looks different than expected.
* **Real Question**: I want to increase the recording quality in the Sound Recorder Plus app to 96kbps. I am currently looking at a settings list. What did I just do and what is the next step?
* **Real Trajectory**: 1. [Observation] Analyzes the current screen showing 'Settings > Audio Constraints'. 2. [Back-tracking] Infers that the previous sequence was: Click 'Menu' -> Click 'Settings'. 3. [Next Action] Identifies 'Recording quality' at [193, 661] as the target to satisfy the goal.
* **Real Answer**: According to the current screen state, you previously opened the Menu and navigated to Settings. To reach your goal, click the 'Recording quality' option now visible at the bottom.
* **Why this demonstrates the capability**: The agent must analyze the current GUI state to reconstruct the hidden historical moves (Back-tracking). This ensures the plan remains consistent even when the agent's internal progress-tracker requires re-synchronization with the real environment state.
---
**[Case 2]**
* **Initial Environment**: A multi-application workflow where a user is attempting to transfer data between a banking app and a spreadsheet. Several windows are open, and the last action seems to have failed or timed out, leaving the agent on a blank login screen.
* **Real Question**: I was trying to move my transaction history. Why am I on a login screen now? Reconstruct what happened and tell me how to continue.
* **Real Trajectory**: 1. [Analysis] Observes the 'Login' prompt on the bank app. 2. [Causal Reconstruction] Determines that the 'Export' click likely triggered a session timeout or a security re-authentication challenge. 3. [Self-Repair] Plans a re-login followed by navigating back to the 'Transactions' tab identified in the pre-failure state.
* **Real Answer**: The banking app session timed out after the export attempt. You must log in again; then I will re-initiate the export to complete the transfer to your spreadsheet.
* **Why this demonstrates the capability**: The agent performs cross-application back-tracking, identifying the cause-effect relationship between an action (Export) and an unexpected environment transition (Login Screen) to repair the broken plan structure.

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

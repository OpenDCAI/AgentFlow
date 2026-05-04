---
name: grounded-task-infeasibility-detection
description: Use this skill when the user asks for a task that might be impossible, broken, or based on features that do not exist. Trigger it for requests like “tell me if you can't do this,” “explain why the button is missing,” “don't just fail, show me why it’s not working,” or “check if this command is actually possible in the current app version.” This skill ensures the agent identifies deprecated features, hallucinated commands, or environmental blockers and provides a logical reason for stopped execution rather than a generic failure.
---

# Skill: grounded-task-infeasibility-detection

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to distinguish between a functional failure and a terminal environmental infeasibility, where the environment lacks the necessary components, software versions, or state to fulfill the user intent. It involves a systematic audit of the GUI for the requested affordances, identifying the absence or deprecation of specific widgets, and generating a grounded refusal backed by visual evidence to prevent 'hallucinated success' or generic 'fail-state' hacking.
* **Dimension Hierarchy**: Reliable and Aligned Operation->User-Aligned Intent Resolution->grounded-task-infeasibility-detection

### Real Case
**[Case 1]**
* **Initial Environment**: A web browser is open on a blank tab. The user provides a command that references a non-existent browser feature named 'Teleport Mode' which is not part of the standard Chromium build.
* **Real Question**: Activate the 'Teleport' browser mode to speed up navigation.
* **Real Trajectory**: The agent opens the main browser menu (the 'three dots' icon), scans all available settings, navigates to the 'Extensions' and 'Experimental Features' tabs, and verifies that no 'Teleport' option exists in the UI tree. It then synthesizes a thought process explaining that the feature is not found in the current browser version.
* **Real Answer**: Task terminated: The requested 'Teleport' browser mode is a non-existent feature in Google Chrome and cannot be activated.
* **Why this demonstrates the capability**: This case demonstrates grounded infeasibility detection by showing that the agent did not simply output a random click or a generic error. Instead, it systematically proved the absence of the requested widget across various menus and provided a specific rationale for why the user's intent was impossible to fulfill.
---
**[Case 2]**
* **Initial Environment**: A Windows 11 desktop is open. The user requests a legacy UI feature (like 'Aero Glass' themes) that was officially deprecated in previous versions of the operating system and is no longer available in the Settings app.
* **Real Question**: Turn on the 'Aero Glass' transparency effects for all windows.
* **Real Trajectory**: The agent navigates to Settings -> Personalization -> Colors, looks for 'Transparency effects,' and notes that while transparency exists, the specific legacy 'Aero Glass' setting with its associated glass-texture widgets is absent. It confirms the system version and explains that the specific feature cannot be enabled via the standard GUI.
* **Real Answer**: Infeasibility detected: The 'Aero Glass' theme is a deprecated Windows feature and is not available in Windows 11 Settings.
* **Why this demonstrates the capability**: This case tests the ability to recognize deprecated features. The agent avoids the 'infeasible hacking' trap of outputting a generic FAIL by explaining the version-specific context and the absence of the target widget in the modern OS layout.

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

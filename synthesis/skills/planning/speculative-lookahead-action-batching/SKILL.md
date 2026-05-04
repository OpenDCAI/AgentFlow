---
name: speculative-lookahead-action-batching
description: Use this when the user wants to speed up computer tasks or decrease wait times by doing several steps in a single execution phase. It is ideal for requests like 'batch these actions to save time', 'do these clicks and typing in one go', 'optimize the plan to finish in fewer steps', or 'perform this routine quickly without waiting for every screen refresh.' It is especially useful for GUI automation where planning/reflection cycles take many minutes but actions take seconds.
---

# Skill: speculative-lookahead-action-batching

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to consolidate multiple sequential operations into a single execution batch by identifying predictable environment transitions and co-visible UI elements. This capability minimizes the cognitive overhead of repetitive Planning and Reflection cycles—which can account for over 90% of total agent latency—by performative grouping of actions (e.g., Click-Type-Enter) that share a single observation state. It utilizes speculative path-finding alongside lightweight control-state validation to maintain high execution throughput while ensuring plan safety.
* **Dimension Hierarchy**: Open-World Real-World Planning->Information-Grounded Plan Construction->speculative-lookahead-action-batching

### Real Case
**[Case 1]**
* **Initial Environment**: A Microsoft Word document is open with the focus on the main editing area. There is a multi-line document where the first line, 'Annual Strategic Growth Plan 2025', is currently left-aligned and needs to be formatted as a centered heading.
* **Real Question**: Help me center align the main heading in my Word document quickly.
* **Real Trajectory**: The agent identifies the heading text through the accessibility tree. Instead of performing two separate planning cycles, it predicts a batch: 1. Select the text 'Annual Strategic Growth Plan 2025'; 2. Click the 'Center' button in the Paragraph ribbon. The agent executes the selection, then immediately uses the internal control-state API to verify that the 'Center' button is visible and enabled on the ribbon before performing the second click.
* **Real Answer**: The heading 'Annual Strategic Growth Plan 2025' is successfully center-aligned within a single execution round.
* **Why this demonstrates the capability**: This case demonstrates speculative look-ahead because the agent does not wait for the visual confirmation of the text selection before planning the click on the alignment button. It treats the sequence as a predictable batch and uses local UIA validation to ensure the alignment tool is reachable, drastically reducing the latency compared to step-by-step reasoning.
---
**[Case 2]**
* **Initial Environment**: Microsoft Excel is active with a workbook named 'Financial_Audit_Results.xlsx' containing detailed tables. The user is on the primary 'Data_Summary' sheet and needs to export it to a standardized CSV format for a legacy database import.
* **Real Question**: Can you export the current Excel summary to a CSV file named 'Audit_Export_Final' in the current directory?
* **Real Trajectory**: The agent identifies that exporting a file is a multi-step routine with a predictable GUI logic. It plans a multi-action batch: 1. Click the 'File' tab; 2. Click the 'Save As' option; 3. Open the file type dropdown; 4. Select the 'CSV (Comma delimited)' format; 5. Enter the filename 'Audit_Export_Final'; 6. Click 'Save'. The executor proceeds through these steps, checking at each stage (e.g., after Step 2) if the next UI element (the dropdown) has materialized in the window before executing the corresponding action.
* **Real Answer**: A file named 'Audit_Export_Final.csv' is generated in the correct folder using a single planning step.
* **Why this demonstrates the capability**: This demonstrates look-ahead batching because the agent constructs the entire 6-step interaction program in advance. The capability relies on the agent's knowledge that the transition from 'File' to 'Save As' is stable, allowing it to bypass redundant thinking cycles while maintaining safety through sequential control-state validation.
---
**[Case 3]**
* **Initial Environment**: A LibreOffice Writer document contains two paragraphs of draft text. The user wants to adjust parallel formatting such as line spacing which is currently set to single (1.0).
* **Real Question**: Change the line spacing of the first two paragraphs to double-spaced.
* **Real Trajectory**: Instead of performing five separate 'Observation-Planning-Action' steps (Select -> Click 'Format' -> Click 'Paragraph' -> Select Tab -> Change Value), the agent identifies that the 'Line Spacing' icon is visible in the active sidebar. It groups the actions into a single operational phase: 1. Drag mouse across paragraphs 1 and 2; 2. Click the 'Line Spacing' icon; 3. Select '2.0' from the resulting dropdown. The agent performs this sequence in a single execution burst using the coordinates from the initial screenshot.
* **Real Answer**: Both paragraphs are updated to double-spaced (2.0) in a single planning cycle.
* **Why this demonstrates the capability**: This demonstrates 'Grouped-Action' efficiency as defined in human-baseline benchmarks. By identifying that the sub-menu triggers are predictable and co-visible, the agent consolidates what typically takes 5-10 minutes of LLM inference into a 30-second human-like trajectory, directly addressing the latency bottleneck of computer-use agents.

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

---
name: fine-grained-widget-grounding
description: Use this skill when the user wants to target tiny, crowded, or easy-to-misclick GUI elements, particularly in high-resolution (4K) professional software. Trigger it for requests like “click the small wrench icon,” “find the share button in this crowded toolbar,” “use the tiny checkboxes,” or “the target is like a needle in a haystack.” This skill is for GUI tasks where the agent must overcome extreme spatial dilution through multi-stage visual refinement and recover from initial localization errors using bidirectional search logic.
---

# Skill: fine-grained-widget-grounding

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to localize and interact with GUI widgets in environments characterized by extreme spatial dilution and visual density, such as professional 4K interfaces where a target may occupy less than 0.1% of the screen. This requires a multi-stage adaptive refinement process utilizing bidirectional ROI (Region-of-Interest) zooming—including asymmetric zoom-in for efficient pruning and context-recovery zoom-out—to maintain target containment while reducing distractor saturation for precise grounding.
* **Dimension Hierarchy**: GUI Perception and Environment Modeling->Element Grounding->fine-grained-widget-grounding

### Real Case
**[Case 1]**
* **Initial Environment**: A professional vector graphics editor (e.g., Figma) is open on a 4K resolution screen. The interface is densely packed with layers, toolbars, and icons, with the target 'Share' button typically located in a crowded top-right toolbar.
* **Real Question**: Click the blue share button in the top-right toolbar.
* **Real Trajectory**: 1. Perform a full-screen scan and identify the top-right region of interest. 2. Execute an asymmetric zoom-in, pruning the bottom and left areas of the screen to focus on the toolbar coordinates. 3. Detect that the initial crop missed the center of the button; execute a controlled zoom-out to regain context. 4. Re-calculate the target center, upscaling the local 1000px ROI by 3x to resolve the 'Share' text label and icon border. 5. Click the precise center of the blue widget.
* **Real Answer**: The 'Share' settings dialog is opened.
* **Why this demonstrates the capability**: This case demonstrates fine-grained grounding under extreme spatial dilution. The agent must successfully navigate multiple stages of ROI refinement, using bidirectional logic to recover from a mis-centered initial crop, and ultimately grounds its action on a widget that was previously a 'needle in a haystack' on the 4K canvas.
---
**[Case 2]**
* **Initial Environment**: A web browser is open to a professional developer blog featuring a historical document Comparison Tool. The document contains tiny, hand-written marginalia below a horizontal line in the right margin.
* **Real Question**: What is the text written below the horizontal line in the right margin of the historical document?
* **Real Trajectory**: 1. Search the page for the 'Interactive Tool Comparison' section. 2. Perform an ROI deduction to isolate the historical document interactive view. 3. Apply a 3x bicubic upscaling to the right margin area to render the tiny hand-written characters clearly. 4. Identify the horizontal line and the specific text span located immediately beneath it. 5. Extract the literal text from the high-resolution pixels.
* **Real Answer**: The text written below the line in the margin is 'Anno 1612'.
* **Why this demonstrates the capability**: Success depends on high-resolution spatial precision and multimodal inspection. The agent must combine multi-stage navigation with scaling agents to extract information from an element that is otherwise unreadable at standard resolutions, proving the ability to seek information from extremely small visual assets.
---
**[Case 3]**
* **Initial Environment**: An email client displays a list of messages. Each message row contains a cluster of visually similar, tiny action icons (Archive, Delete, Flag, Pin) that appear only on hover or in compact mode.
* **Real Question**: Pin the third email from the top.
* **Real Trajectory**: 1. Identify the third row in the email list. 2. Focus on the action icon strip for that specific row. 3. Distinguish the 'Pin' icon from the 'Flag' and 'Archive' icons, which share similar geometric shapes. 4. Calculate the precise center coordinates for the Pin icon within the dense cluster and execute a click.
* **Real Answer**: The third email is pinned successfully.
* **Why this demonstrates the capability**: This case stresses fine-grained localization in repetitive layouts. The agent must perform precise element grounding to separate the correct target from identical visual distractors located in a high-density action strip where a misclick of a few pixels would result in a different action (like deletion).

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

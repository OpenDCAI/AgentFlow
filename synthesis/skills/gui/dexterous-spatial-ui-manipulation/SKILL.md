---
name: dexterous-spatial-ui-manipulation
description: Use this skill when the user wants tasks requiring precise physical interaction across coordinates, such as drag-and-drop, selecting specific text spans, adjusting sliders, or drawing/arranging elements based on spatial constraints. Trigger it for requests like “highlight the second sentence,” “select the paragraph starting with 'For',” “move the file to the folder,” “set the slider to 75%,” “draw a circle inside the square,” or “draw a 3x3 grid.” This skill is for GUI tasks where the agent must resolve spatial start/end points, compute geometric bounding boxes, or maintain continuous motion control to manipulate UI elements precisely.
---

# Skill: dexterous-spatial-ui-manipulation

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to perform spatially-aware, continuous physical interactions within a GUI, calculating and executing actions involving multi-point trajectories (drag-and-drop), precise 2D coordinate resolutions (drawing geometric shapes within relational bounds), and area-based selections (character-level text highlighting). This skill requires the agent to move beyond discrete clicking to compute relative positioning, coordinate-based intersections, and visual text-snapping mechanisms across dense or blank-canvas environments.
* **Dimension Hierarchy**: GUI Perception and Environment Modeling->Element Grounding->dexterous-spatial-ui-manipulation

### Real Case
**[Case 1]**
* **Initial Environment**: A document editor is open showing a text-dense page with multiple paragraphs and sentences. The interface context is a scoped application window focus.
* **Real Question**: Drag to select the second sentence of the first paragraph.
* **Real Trajectory**: Locate the first paragraph block, identify the punctuation marking the end of the first sentence, calculate the precise starting coordinate (x,y) at the beginning of the second sentence's first word, initiate a drag action, move the cursor to the coordinate (x',y') following the last word of the second sentence, and release.
* **Real Answer**: The second sentence of the first paragraph is highlighted/selected.
* **Why this demonstrates the capability**: This case requires character-level precision rather than simple widget grounding. The agent must resolve the spatial range between two arbitrary points in a dense text field and maintain the 'drag' state to encapsulate a specific span, reflecting the dexterity required to manipulate non-atomic UI content.
---
**[Case 2]**
* **Initial Environment**: A desktop environment is open with a file manager showing several documents in one pane and a 'Work' folder in the other pane. A text editor is also visible in the background.
* **Real Question**: Move the 'invoice.pdf' file from the Downloads folder into the Work folder.
* **Real Trajectory**: Locate the 'invoice.pdf' icon, initiate a drag action by clicking and holding, calculate the trajectory to the center of the 'Work' folder icon, move the cursor to that target, and release the mouse button.
* **Real Answer**: The file 'invoice.pdf' is successfully relocated to the 'Work' folder.
* **Why this demonstrates the capability**: This demonstrates dexterous manipulation by requiring the agent to maintain a persistent 'mouse-down' state while traversing the spatial gap between two GUI nodes. It moves beyond 'click to select' into continuous motion control across application boundaries.
---
**[Case 3]**
* **Initial Environment**: A drawing application is open with a color palette (Red at (429, 25), Blue at (477, 25)) and shape tools (Circle at (35, 445), Rectangle at (35, 365)).
* **Real Question**: Draw a red circle inside a blue square.
* **Real Trajectory**: Click the blue color. Click the rectangle tool. Draw a square by mouseDown at (400, 300) and mouseUp at (700, 600). Click the red color. Click the circle tool. Calculate the center of the newly drawn blue square and mouseDown at (500, 400), dragging a circular stroke that stays entirely within the square's 400x300 bounds, releasing the mouse.
* **Real Answer**: A red circle is rendered completely contained within the bounds of a blue square.
* **Why this demonstrates the capability**: This requires relational coordinate calculation and prolonged spatial planning. The agent must continuously transition tool color states and define exact dragging vectors (mouse down to mouse up) that execute geometric structures based solely on visual bounds without discrete GUI buttons.

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

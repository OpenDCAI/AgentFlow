---
name: multimodal page grounding
description: Use this skill when the user wants tasks where the page layout, screenshot, specific visual position, layout adjacency in tables, or physical drag-and-drop motions actually matter. Trigger it for requests like “make it rely on what’s visible on the page,” “extract the data from this complex table layout,” “buttons and layout should dictate the choice,” or “force the agent to navigate based on spatial coordinates.” It is the right skill for browser tasks where perception must combine HTML-like structure with visual grounding to execute continuous mouse events or parse complex semi-structured layouts (like grids or key-value structures).
---

# Skill: multimodal page grounding

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to ground actions and interpretations in both the textual structure of a webpage and its visual-spatial coordinate state, enabling the agent to interpret layouts, resolve visual ambiguity, parse complex semi-structured tables via adjacency, and execute precise physical mechanisms like drag-and-drop or spatial selections using continuous spatial logic.
* **Dimension Hierarchy**: Web Interaction Execution->Web Perception->multimodal page grounding

### Real Case
**[Case 1]**
* **Initial Environment**: A search page containing a dynamic textbox and multiple elements labeled 'Search', accompanied by both DOM references and a captured screenshot of the visible UI structure.
* **Real Question**: Use the textbox to enter "Olin" and press the specific 'Search' button connected to the input, then find and click the 7th visible search result.
* **Real Trajectory**: {"action": "type", "ref": "5", "text": "Olin"} -> visually grounds which 'Search' button is spatially aligned with the textbox -> initiates click -> identifies the seventh visible search result via spatial order -> clicks the corresponding element.
* **Real Answer**: Click successfully registers on the 7th visually rendered search item.
* **Why this demonstrates the capability**: The page must be understood as an actionable geometric interface rather than a plain textual document. The agent is forced to align the textbox and search button using spatial proximity rather than raw DOM matching, and then reason about visible search-result ordering to accurately execute the final selection.
---
**[Case 2]**
* **Initial Environment**: A web interface featuring a sequence of interactive vertical slider tracks and a geometric alignment line rendered across the upper third of the UI, lacking discrete text-based endpoints.
* **Real Question**: Align all the blue interactive boxes on the screen with the central target line by mastering the vertical sliders.
* **Real Trajectory**: The agent inspects the relative visual starting state of the slider blocks. It triggers a 'Mouse Down' coordinate sequence on the first slider, computes the expected visual pixel offset to reach the geometric line, moves the mouse across the calculated Y-axis distance, and executes a 'Mouse Up' release, verifying successful alignment visually before moving to slider two.
* **Real Answer**: Successfully aligned all blocks via continuous drag actions.
* **Why this demonstrates the capability**: This explicitly demonstrates the mechanical coordination of drag-and-drop actions reliant entirely on visual boundaries. The agent cannot simply fire a baseline click command onto a fixed DOM ID; it must actively interpret the spatial gap between two visually rendered objects and execute a continuous coordinate-bound stroke to achieve the geometric configuration.
---
**[Case 3]**
* **Initial Environment**: A web browser viewing a product detail page where technical specifications are listed in a complex layout of horizontal tables and vertical key-value formats.
* **Real Question**: What are the specific CPU and GPU clock speeds listed for the X3216 model extracted directly from the spec table?
* **Real Trajectory**: 1. Locate the multi-column div block containing the specifications. 2. Identify the implicit subject 'X3216' via header visual alignment. 3. Scan for the 'CPU Clock' attribute in the left-hand column and map the spatially adjacent value '1.6 GHz' as the object. 4. Detect a repeating 'Base' label row under 'GPU' column and utilize horizontal alignment to extract '0.8 GHz'.
* **Real Answer**: [(X3216, CPU Clock Base, 1.6 GHz), (X3216, GPU Clock Base, 0.8 GHz)]
* **Why this demonstrates the capability**: This case requires perceiving spatial and layout motifs within the HTML structure rather than reading linear text. The agent must successfully recognize grid structures, implicit header nesting, and spatial adjacency (left-to-right alignment) to parse repeating semi-structured data points correctly.

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

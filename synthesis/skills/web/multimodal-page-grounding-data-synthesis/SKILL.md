---
name: multimodal-page-grounding-data-synthesis
description: Use this skill when the user wants tasks where the page layout, screenshot, button position, visual state, or on-screen cues actually matter. Trigger it for requests like “make it rely on what’s visible on the page,” “the agent should need the screenshot,” “buttons and layout should matter,” or “don’t let text alone be enough.” It is the right skill for browser tasks where perception must combine HTML-like structure with visual grounding.
---

# Skill: Multimodal Page Grounding

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to ground actions and interpretations in both the textual structure of a webpage and its visual-spatial state, so that the agent can use screenshots, layout, visible widgets, and dynamic UI changes together with HTML or DOM information.
* **Dimension Hierarchy**: Web Interaction Execution->Web Perception->Multimodal Page Grounding

### Real Case
**[Case 1]**
* **Initial Environment**: An email interface showing multiple messages, visible sender names, and forward controls, with both screenshot and HTML references available to the agent.
* **Real Question**: Find Gisele’s email and forward it to Siana, please.
* **Real Trajectory**: Click the email from the proper sender, open the forward action, type `Siana` into the receiver field, and click the final confirmation control.
* **Why this demonstrates the capability**: The task depends on grounding sender identity, the visible email list, and the actionable controls in the current UI state. The agent cannot solve it by raw text extraction alone because it must map visible elements to executable actions across multiple screen transitions. This demonstrates multimodal grounding because the correct next move depends on where the relevant content and controls are on the page now, not only on abstract page text.

---
**[Case 2]**
* **Initial Environment**: A search page containing a textbox and a search button, represented both as HTML references and as a screenshot with visible UI structure.
* **Real Question**: Use the textbox to enter "Olin" and press "Search", then find and click the 7th search result.
* **Real Trajectory**: {"action": "type", "ref": "5", "text": "Olin"} -> {"action": "click", "ref": "6"} -> identify the seventh visible search result -> click the corresponding element.
* **Why this demonstrates the capability**: The page must be understood as an actionable interface rather than as a plain document. The agent has to align the textbox and search button with their references, then later reason about visible search-result ordering to pick the seventh item. The capability is tested by whether the agent can move from structured page text to visually grounded action selection as the interface changes.

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

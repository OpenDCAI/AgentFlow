---
name: semantic-gui-hierarchical-exploration
description: Use this skill when the user wants to find a button or setting that isn't on the front page and requires digging through menus. Trigger it for requests like “I can't find where to change my avatar,” “where is the customer service hidden,” “find the setting to turn off auto-play,” or “explore the app to find the draft folder.” This skill focuses on searching through deep app hierarchies and figuring out which icons or text labels to click when the path to the goal is not obvious or mentioned in the prompt.
---

# Skill: semantic-gui-hierarchical-exploration

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to autonomously navigate through complex, multi-layered GUI hierarchies to discover specific functionalities by inferring semantic relationships between user goals and interface affordances. This involves hierarchical search (deciding which nested sub-menus to enter), icon-content mapping (interpreting visual symbols without text), and exploratory recovery (recognizing dead-end branches and backtracking to the last logical decision point).
* **Dimension Hierarchy**: GUI Perception and Environment Modeling->Environment Understanding->semantic-gui-hierarchical-exploration

### Real Case
**[Case 1]**
* **Initial Environment**: The Bilibili mobile app is open on the 'Home' screen with the bottom navigation bar visible.
* **Real Question**: I want to contact Bilibili customer service.
* **Real Trajectory**: 1. Identify and click the 'Me' icon in the bottom navigation to enter the personal center. 2. Scan the page for 'Support' or 'Help', but notice these are not immediately visible in the top widgets. 3. Scroll up the page to reveal lower sections including 'More Services'. 4. Identify the 'Help Center' button or the 'Customer Service' headset icon located within the scrolled area. 5. Click the element to reach the interactive support page.
* **Real Answer**: The Bilibili customer service / help center page is successfully reached.
* **Why this demonstrates the capability**: This case requires hierarchical exploration because the customer service function is hidden at a depth of two levels and resides in an off-screen 'More Services' area. The agent must successfully infer that the 'Me/Profile' section is the correct starting branch and perform a vertical scroll to unearth the hidden functional entry point rather than clicking obvious homepage elements.
---
**[Case 2]**
* **Initial Environment**: A cloud-based email application (NetEase Mail) is open at the inbox view.
* **Real Question**: Open my draft in NetEase Mail.
* **Real Trajectory**: 1. Analyze the inbox view and observe that the 'Draft' folder is not in the primary navigation tabs. 2. Click the 'Sidebar' or 'Folder List' icon in the top header. 3. Scan the expanded hierarchical menu for the 'Drafts' item. 4. Identify the item through its folder-shaped icon or label and execute the click.
* **Real Answer**: The drafts folder is opened, displaying all unsent messages.
* **Why this demonstrates the capability**: Success depends on 'Hidden Function Discovery' where a core utility (Drafts) is tucked away inside a non-default drawer. The agent must recognize that the current page state is insufficient and proactively trigger a menu-expansion action to explore the app's structural hierarchy.
---
**[Case 3]**
* **Initial Environment**: The Bilibili app is open on a video playback page with global settings previously set to default.
* **Real Question**: Set a 15-minute turn-off timer in Bilibili.
* **Real Trajectory**: 1. Navigate to the 'Me' center. 2. Click on the 'Settings' gear icon at the top right. 3. Search the settings list for 'Timer' or 'Global' options. 4. Realize the timer is not in the top-level list and enter the 'General Settings' or 'Timed Shutdown' sub-menu. 5. Locate the 15-minute radio button and activate it.
* **Real Answer**: A 15-minute automatic shutdown timer is activated for the application.
* **Why this demonstrates the capability**: This demonstrates 'Hierarchical Navigation' through three distinct logic layers (Me -> Settings -> General -> Timer). The agent must maintain the specific numeric parameter (15 mins) while navigating through deep menus that offer similar-looking but unrelated toggle switches.

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

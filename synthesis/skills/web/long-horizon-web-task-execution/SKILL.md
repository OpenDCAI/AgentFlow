---
name: long-horizon web task execution
description: Use this skill when the user wants tasks that require a long sequence of actions across multiple screens, tracking state changes, executing recursive loops to generate exhaustive list data, tree-walking hidden menus, or filling out multi-page forms. Trigger it for requests like 'prowl this site to find hidden settings,' 'create a complete table by checking every item,' 'fill out the entire application using this document,' or 'apply all these filters while staying under budget.' It perfectly handles complex traversal loops, multi-item data aggregation across sub-pages, and mapping a site's hidden topology through persistent exploration.
---

# Skill: long-horizon web task execution

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to execute extended, non-linear web task sequences requiring complex control flows such as maintaining task state, executing structured paginated loops for exhaustive dataset aggregation, tree-walking nested UI hierarchies via difference-spotting, and honoring complex negative policies across prolonged layout transitions without omission.
* **Dimension Hierarchy**: Web Interaction Execution->Web Control->long-horizon web task execution

### Real Case
**[Case 1]**
* **Initial Environment**: An e-commerce platform initialized for an office procurement task with a list of items including catering, drinks, and snacks.
* **Real Question**: Order catering for a birthday party for 10 people in our office. Policy: 1. No alcohol. 2. At most one cake. 3. Total budget must not exceed $200. 4. Must include vegan food.
* **Real Trajectory**: 1. Search and add 'Chicken Wings'. 2. Add 'Tiramisu Cake'. 3. Locate 'Moët Champagne' but reject it due to the no-alcohol policy. 4. Add 'Veggie Platter'. 5. Ensure total cost strictly remains under the $200 cumulative state limit. 6. Execute Checkout.
* **Real Answer**: Checkout successfully executed while maintaining all procedural and state-bound negative constraints.
* **Why this demonstrates the capability**: This requires 'Sequential Policy-Compliance' during long-horizon actions. The agent must reconcile a multi-step task completion goal against continuous state invariants (budget) and specific prohibitions, demonstrating working memory tracking across multiple complex interactions.
---
**[Case 2]**
* **Initial Environment**: A web browser with access to global political archives, news aggregators, and encyclopedic historical records of South Korea.
* **Real Question**: Provide a table listing all presidents in South Korean history, featuring specific 'Start/End Dates', and a 'Martial Law' column indicating whether martial law was declared during their tenure. Sort chronologically.
* **Real Trajectory**: 1. Issue a broad query to establish the horizontal entity set (master list of presidents). 2. Iterate recursively through the list, drilling down into deep vertical search queries or secondary bios for each individual to verify specific 'Martial Law' usage. 3. Consolidate distributed findings, apply date normalizations, and structure into a complete 15+ row table.
* **Real Answer**: A table with rows for all presidents, their specific standardized dates, and individually verified martial law indicators.
* **Why this demonstrates the capability**: The case forces the execution of 'Recursive Loops' within a single session. The agent transitions from broad structural discovery to exhaustive sequential data extraction, proving it can manage a multi-item queue and maintain a complex organizational schema over extended site traversals.
---
**[Case 3]**
* **Initial Environment**: A web-based SaaS dashboard displaying a high-level overview with numerous collapsed layout sidebars and unclicked overflow options.
* **Real Question**: Systematically map the 'Settings' architecture of this platform to find where 'API Token Generation' is buried.
* **Real Trajectory**: 1. Execute 'Left_Click' on the Profile icon and identify newly appeared 'Account Settings'. 2. Navigate to 'Account Settings' and observe the menu expansion. 3. Click 'Security' and detect the appearance of a nested 'Advanced' sub-menu. 4. Click 'Advanced' and successfully isolate the final generative modal.
* **Real Answer**: Final functional state isolated: API Token Generation interface located under Profile -> Account Settings -> Security -> Advanced.
* **Why this demonstrates the capability**: This explicitly tests 'Structural Tree-Walking' and autonomous topology discovery. The agent utilizes continuous 'Difference Spotting' between DOM/visual states to identify newly exposed UI elements, mapping deepest-layer nodes without explicit navigational clues.

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

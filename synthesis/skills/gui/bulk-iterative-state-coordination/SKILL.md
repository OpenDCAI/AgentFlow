---
name: bulk-iterative-state-coordination
description: Use this skill when the user wants to process a long list, a large table, or multiple items one by one. Trigger it for requests like “collect all the names from the table,” “copy every row from the list,” “loop through the folders without missing any,” “make sure you get all 50 items across the pages,” or “process these invoices skipping the ones I've already done.” This skill focuses on tracking progress during repetitive loops to ensure no items are omitted and no actions are redundant.
---

# Skill: bulk-iterative-state-coordination

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to manage operational reliability in high-volume, multi-step repetitive processes by maintaining set-integrity and iteration state. This includes the ability to navigate through paginated tables, infinite-scrolling lists, or hierarchical trees while tracking progress to avoid the 'capability cliff' of omitting items or repeating actions. It requires the agent to utilize state-coordination to handle dynamic interface resets and maintain memory of processed versus unprocessed elements within a large-scale execution horizon.
* **Dimension Hierarchy**: Goal-Directed GUI Workflow Execution->Verified Task Completion->bulk-iterative-state-coordination

### Real Case
**[Case 1]**
* **Initial Environment**: A web-based enterprise application is open to a paginated 'Customer Records' table. The table contains 50 entries distributed across 5 pages, with a 'Next' button at the bottom and a search bar at the top.
* **Real Question**: Extract the contact names of all 50 customers from the list.
* **Real Trajectory**: 1. Identify the starting row of the first page. 2. Iteratively extract names from rows 1 to 10. 3. Locate and click the 'Next' page button. 4. Verify that the table has refreshed to page 2 (to avoid repeating page 1). 5. Continue this loop, tracking the 'processed count' in memory, until the 'Next' button becomes disabled on page 5. 6. Perform a final verification scan to ensure exactly 50 names are collected.
* **Real Answer**: A list containing exactly 50 unique customer names extracted from the paginated table.
* **Why this demonstrates the capability**: This case requires set-based memory management and state coordination. The agent must distinguish between different pages and maintain an internal record of progress to ensure that no page is skipped and no row is processed twice, which is a key failure mode in enterprise workflows.
---
**[Case 2]**
* **Initial Environment**: A cloud-based file management system is open, showing a nested folder structure for 'Project Q3'. The system uses a hierarchical tree view where folders must be expanded to reveal sub-files.
* **Real Question**: Locate and collect every PDF document within the 'Project Q3' folder tree, including all sub-folders.
* **Real Trajectory**: 1. Locate the 'Project Q3' root folder and expand it. 2. Scan the level-1 elements and identify sub-folders a, b, and c. 3. Systematically enter sub-folder 'a', collect PDF files, and then return (Back) to the root level. 4. Track 'Folder a' as 'completed' in memory to avoid redundant re-entry. 5. Repeat for folders 'b' and 'c' until all nodes in the tree have been visited and verified.
* **Real Answer**: A collection of all PDF files found throughout the hierarchical tree structure.
* **Why this demonstrates the capability**: This demonstrates hierarchical planning and state tracking. The agent must maintain a 'frontier' of unvisited nodes and avoid the 'looping trap' where it repeatedly re-opens the same directory, proving reliable coordination in complex custom layouts.
---
**[Case 3]**
* **Initial Environment**: A Salesforce CRM application is open to the 'Leads' dashboard. There are 25 leads with the status 'New' that need to be updated to 'Contacted'.
* **Real Question**: Update the status of every 'New' lead in this list to 'Contacted'.
* **Real Trajectory**: 1. Scan the list to identify the coordinates and IDs of all entries with the 'New' status tag. 2. Select the first lead, navigate to its detail page, update the status to 'Contacted', and save. 3. Return to the list view and observe the updated state. 4. Identify the next 'New' lead, ensuring it skips the previously updated entries that might still be visible in the feed due to lazy-loading. 5. Iterate until the filter for 'New' leads returns zero results.
* **Real Answer**: All 25 leads in the system have their status updated to 'Contacted'.
* **Why this demonstrates the capability**: This case requires the agent to handle dynamic UI changes during bulk processing. It must rely on visual state-aware logic to identify the remaining work set and avoid 'perception drift' where it attempts to update a lead that has already been successfully processed but is still visible in the interface.

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

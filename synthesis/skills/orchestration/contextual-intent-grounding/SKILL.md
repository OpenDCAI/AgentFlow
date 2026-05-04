---
name: contextual-intent-grounding
description: Use this skill when the user gives a short or messy request that doesn't explain the full details, but the 'right way' to do it is already visible in the environment. It should be triggered by casual phrasing like “finish the rest of the list,” “do it just like the others,” “update the records using the existing style,” or “add a new entry to the site following the current layout.” This applies when an agent must look at previous examples, templates, or sibling folder structures to figure out what fields to fill, what formats to use, or where exactly to put a file without being told explicitly. Example triggers include: “keep the formatting consistent with previous weeks,” “fill in the missing rows,” and “put the file where it belongs based on the other folders.”
---

# Skill: contextual-intent-grounding

## 1. Capability Definition & Real Case
* **Professional Definition**: Contextual intent grounding is the orchestrator's capability to resolve underspecified or 'fuzzy' user instructions by autonomously deriving operational parameters and formatting constraints from the existing environment state. Unlike basic schema compliance which focuses on technical API types, this capability involves analyzing 'reference artifacts'—such as existing database entries, document templates, or historical state snapshots—to infer the correct logical structure and domain-specific values required for a successful tool invocation. It represents the bridge between highly concise human intent and the specific, grounded logic required to maintain consistency within a complex, pre-populated multi-tool workspace.
* **Dimension Hierarchy**: Tool Invocation Fidelity->Invocation Specification Handling->contextual-intent-grounding

### Real Case
**[Case 1]**
* **Initial Environment**: A Google Sheets workspace contains a master 'Security Audit' spreadsheet. The spreadsheet includes two pre-populated sheets, 'Week1' and 'Week2', which contain specific columns for 'Microservice ID', 'Vulnerability Level', and 'Remediation Date' formatted as MM/DD/YYYY, and a blank sheet named 'Week3'.
* **Real Question**: Please perform a security audit on the cluster for this week and sync the results to the Week3 sheet in the audit file.
* **Real Trajectory**: The agent first calls a tool to read the contents of 'Week1' and 'Week2' to observe the established column headers and data formats. It recognizes that while the API for adding a sheet only requires raw values, the domain-correct metadata requires following the existing chronological format (MM/DD/YYYY) and specific header strings found in the siblings. It then executes the cluster audit tools, maps the findings into the discovered row-column structure, and populates 'Week3' with identical formatting to ensure the master file remains consistent.
* **Why this demonstrates the capability**: This case demonstrates contextual grounding because the user never specified the format or the necessary columns for the audit. The orchestrator had to proactively investigate the environment's internal 'state history' to infer the implicit requirements of the task. Success is not just calling the spreadsheet tool correctly, but calling it with the specific content structure derived from the environment.
---
**[Case 2]**
* **Initial Environment**: A Notion workspace contains an 'HR Record' database with a history of sample entries showing fields such as 'Highest Degree' (restricted to an uppercase enum), 'Application Status', and 'University'. A local directory contains 10 newly arrived PDF resumes that need to be parsed and integrated.
* **Real Question**: Update the HR Record subpage on Notion according to all the resumes in my workspace. Make sure to fill in all information strictly according to the content, and remember to delete the samples first.
* **Real Trajectory**: The agent identifies the target database and first retrieves the 'sample entries' to distinguish between the database's technical schema and the domain-level recording style (e.g., verifying if 'Master of Finance' is stored as the full string or mapped to a 'Master' tag). It then deletes the sample records as requested. Finally, it parses the resumes and populates the database, ensuring that information like the degree name or school name matches the specific field-mapping logic inferred from the now-deleted samples rather than inventing new categories.
* **Why this demonstrates the capability**: This case highlights the ability to extract constraints from 'ephemeral state.' The agent must learn the formatting rules from the samples *before* deleting them, as the samples represent the only source of truth for how the user expects the data to be structured. It tests the orchestrator's foresight to survey the environment for latent constraints before executing state-destructive operations.
---
**[Case 3]**
* **Initial Environment**: A Github repository contains a personal homepage project. The repository structure includes a 'papers/' directory with subdirectories for each year (e.g., '2023/', '2024/') and a 'README.md' that lists recent publications using a specific Markdown bibtex-style format. The user's inbox contains a new paper acceptance email.
* **Real Question**: I just got a paper accepted; please update my personal homepage with the new info.
* **Real Trajectory**: The agent reads the inbox to find the paper title and year. It then explores the repository's file tree to identify the established organization pattern, discovering that new papers are stored in year-specific folders. It reads the current 'README.md' to extract the exact HTML or Markdown pattern used for citations. It then creates the new file in the '2025/' directory (which it creates autonomously based on the pattern) and appends the new citation to the README using the identical linguistic style of the existing entries.
* **Why this demonstrates the capability**: This demonstrates capability in a macro-environment where the user provides 0% of the layout or location details. The orchestrator must ground its plan in the 'observed convention' of the existing workspace. Failure to identify the year-based directory structure or the specific README format would result in a broken or inconsistent homepage, even if the paper data itself was correct.

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

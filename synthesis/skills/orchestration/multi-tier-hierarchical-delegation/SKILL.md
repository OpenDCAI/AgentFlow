---
name: multi-tier-hierarchical-delegation
description: Use this skill when you want to divide a big, complicated job among different 'expert teams' or 'specialized sub-agents' rather than having one agent try to do everything at once. This is perfect for requests like “let the local files team handle the database while the internet team searches the web,” “manage multiple specialized groups to find an answer,” or “use a manager to coordinate different expert sub-agents.” Trigger it when a task involves so many different tools or knowledge sources (like internal corporate data plus public web data) that a single agent would get confused by too many options. Use it to keep the manager focused on the 'big picture' while the experts handle the technical details. Examples: “ask the local expert for the specs and the web expert for the price,” “coordinate between the medical team and the legal team,” and “don't give all the tools to one agent; split them up.”
---

# Skill: multi-tier-hierarchical-delegation

## 1. Capability Definition & Real Case
* **Professional Definition**: Multi-tier hierarchical delegation is the orchestration capability to manage complex, multi-domain tasks by partitioning a large tool/action space into specialized sub-agents (leaf nodes) coordinated by a high-level manager (planner/root agent). This hierarchical structure addresses the 'Action Space Explosion' problem, where equipping a single agent with dozens of heterogeneous tools leads to training instability and low execution fidelity. The coordinator manages macroscopic source selection and high-level strategy, while specialized leaf agents maintain localized synergies within specific domains (e.g., Local Database Search vs. Web Search). It incorporates 'Reasoning-Aware Knowledge Refining,' a mechanism that filters and extracts only the relevant evidence from sub-agent trajectories to prevent hallucination, error propagation, and context-window saturation at the root level.
* **Dimension Hierarchy**: Workflow Orchestration->Iterative Planning and Refinement->multi-tier-hierarchical-delegation

### Real Case
**[Case 1]**
* **Initial Environment**: A multi-source enterprise environment contains a 'Local Search Agent' (equipped with internal text chunks and an RDF knowledge graph) and a 'Web Search Agent' (equipped with a web search engine and a webpage browser). A 'Planner Agent' sits atop the hierarchy to coordinate them.
* **Real Question**: Who is the father of the person who performed the album 'Labo M'?
* **Real Trajectory**: The Planner Agent first identifies that 'Labo M' is a specific entity and dispatches a high-level request to the Local Search Agent. The Local Agent utilizes the internal text corpus to identify that the 'Labo M' performer is the French singer-songwriter Matthieu Chedid. The Planner Agent receives this refined fact and, realizing current local data is insufficient for familial relations of this person, dispatches a second request to the Web Search Agent for 'father of Matthieu Chedid'. The Web Agent browses the relevant wiki pages and retrieves the fact that his father is Louis Chedid. The Planner then synthesizes the final answer based on these filtered inputs.
* **Real Answer**: Louis Chedid
* **Why this demonstrates the capability**: This demonstrates multi-tier delegation by showing the Planner coordinate two specialized sub-agents rather than calling local/web tools directly. The hierarchical partitioning allows the system to master local data (corpus/graph) and web data (engine/browser) in isolation, while the Planner manages the cross-supplementation logic without being overwhelmed by the raw HTML or dense triplets seen by the specialists.
---
**[Case 2]**
* **Initial Environment**: An enterprise deep search workspace where a project requires comparing internal sensitive revenue data with public market benchmarks. The environment partitions tools into an 'Internal Auditor' squad and an 'External Market' squad.
* **Real Question**: What is the sibling of the author of Kapalkundala, and how do their literary sales compare to our current local projections?
* **Real Trajectory**: The Planner Agent triggers the 'Internal Auditor' for local author records. The auditor identifies Bankim Chandra Chattopadhyay as the author but fails to find sibling records in the local corpus. The Planner then delegates the 'sibling' search to the 'External Market' squad (Web Search). The Web Agent identifies Sanjib Chandra Chattopadhyay as the brother. Finally, the Planner instructs the Internal Auditor to retrieve the 'current local projections' from the private database and performs the comparative analysis in its own context window.
* **Real Answer**: The sibling of the author (Bankim Chandra Chattopadhyay) is Sanjib Chandra Chattopadhyay. Their sales compare to our current local projections by [Comparison Stat].
* **Why this demonstrates the capability**: This showcases the filtering of hallucinations where the low-level agents navigate messy search results (distinguishing between multiple authors) and only pass high-confidence evidence back to the Planner. The Planner maintains the task state (Goal 1: Sibling, Goal 2: Comparison) and ensures that knowledge conflicts between local and web sources are handled through hierarchical priority.

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

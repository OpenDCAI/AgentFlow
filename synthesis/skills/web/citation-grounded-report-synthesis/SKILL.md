---
name: citation-grounded report synthesis
description: Use this skill to generate high-quality, professional investigative reports that mirror expert human standards and satisfy the Deep Reasoning (Depth) and Wide Aggregation (Width) dimensions of research. Trigger this skill when the user asks for 'analyst-level research,' 'deep-dive investigative reports,' or when they need to 'verify findings against expert standards' on the live web. It is especially useful for requests like 'do some deep research into this,' 'make sure the analysis goes beyond just summarizing facts,' 'trace the specific history across the web,' or 'reconcile complex data into a structured case study.' This skill ensures the output provides both logical deduction to identify hidden entities and comprehensive attribute gathering to ensure data completeness.
---

# Skill: citation-grounded report synthesis

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to execute autonomous investigations over extended horizons by navigating real-time Information Trees and synthesizing findings into expert-level reports. This capability involves two orthogonal pillars: Deep Reasoning (Depth), which utilizes multi-hop deduction across relationship chains to identify core subjects; and Wide Coverage (Width), which aggregates multifaceted attributes across sibling entities to ensure informational density. It requires an evidence-based execution framework that evaluates findings against atomic logical predicates (checklists) and manages temporal alignment by grounding analysis in the live state of the internet.
* **Dimension Hierarchy**: Grounded Research Output->Report Construction->citation-grounded report synthesis

### Real Case
**[Case 1]**
* **Initial Environment**: A web browser with access to regional sports associations, gymnastics facility directories, and specialized training program registries in the New York and New Jersey metropolitan area.
* **Real Question**: Locate a gymnastics organization in the New York/New Jersey area that structures its competitive teams into three specific tiers: an in-house 'Club Team' that competes exclusively against the organization’s other branches, a 'USA-IGC' program capped at 3 training days per week, and a third 'Junior Olympic' program that explicitly prohibits athletes from participating in other activities. Provide the name of this organization, the specific name of the high-performance program, and a list of all cities where they currently operate gyms.
* **Real Trajectory**: 1. Search for 'gymnastics Club Team vs USA-IGC tiers NY NJ'. 2. Identify 'Gold Medal Gymnastics' (GMGC) via its multi-branch structure mentions in forum archives. 3. Navigate to the official 'Gold Medal Gymnastics' competitive team page. 4. Verify the three-tier logic: 'Club Team' (intra-branch only), 'USA-IGC' (limitations on training hours), and 'Junior Olympic' (the high-performance program with exclusivity clauses). 5. Browse the 'Locations' footer to extract the full set of 7 cities: Centereach, Garden City, Huntington, Levittown, Rocky Point, Short Hills, and Smithtown. 6. Reconcile the program name and city set into a structured summary.
* **Real Answer**: Organization: Gold Medal Gymnastics (GMGC); High-Performance Program: Junior Olympic Team; Locations: Centereach, Garden City, Huntington, Levittown, Rocky Point, Short Hills, Smithtown.
* **Why this demonstrates the capability**: This case demonstrates 'Deep reasoning' because the organization is not named in the prompt; the agent must deduce it using a complex three-tier logic chain. It also tests 'Wide aggregation' by requiring the retrieval of a comprehensive list of seven distinct city names that are distributed across a multi-branch location directory rather than a single summary point.
---
**[Case 2]**
* **Initial Environment**: A web browser with access to global medical joint-venture registries, specialized telehealth service registries (e.g., Cleveland Clinic, Amwell), and international healthcare regulatory listings.
* **Real Question**: Investigate the remote medical second opinion service operated by the joint venture between Cleveland Clinic and Amwell. Provide a detailed breakdown of its geographic scope by listing the U.S. states eligible for the full 'Concierge Plus' virtual visit, those restricted to the written report only, and those where the service is unavailable. Additionally, report the service costs for U.S. vs international patients, and the countries where the service is prohibited.
* **Real Trajectory**: 1. Search for 'Cleveland Clinic Amwell second opinion joint venture' to identify the entity 'The Clinic'. 2. Navigate to the official 'The Clinic by Cleveland Clinic' platform. 3. Access the 'Terms of Service' or 'State Availability' map to identify 'Concierge Plus' states. 4. Systematically extract 21 states for virtual visits and 28 'Written Report Only' states, identifying Maine and South Dakota as 'Unavailable'. 5. Navigate to the pricing/billing FAQ to find the $1,690/$1,990 U.S. rates and the $4,500 international rate. 6. Locate the 'International Exclusions' list to identify countries like China, Australia, and Russia where specific laws prohibit the service.
* **Real Answer**: Service: The Clinic (VSO); Concierge Plus States: (Ariz., Calif., Colo., etc.); Written Report Only: (Alaska, Ala., Ark., etc.); Unavailable: Maine, Rhode Island, South Dakota; U.S. Pricing: $1,690-$1,990; International Pricing: $4,500; Prohibited Countries: Australia, China, Germany, Denmark, Greece, Iran, North Korea, South Korea, Kazakhstan, Malaysia, Russian Federation, Sweden, Turkey.
* **Why this demonstrates the capability**: This case demonstrates 'Wide coverage' through the aggregation of a massive list of attributes (all 50 U.S. states and 13+ countries) across different regulatory categories. It forces the agent to manage a heavy context load while maintaining high precision on pricing and geographic alignment, which is critical for expert-level reporting.

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

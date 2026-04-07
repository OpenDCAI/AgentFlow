---
name: geospatial-rule-grounding-data-synthesis
description: Use this skill when the user wants SQL tasks involving maps, zones, ports, waterways, or rule compliance tied to location. Trigger it for requests like “use area-based conditions”, “make the model check whether something is inside a region”, “tie the SQL to navigation or geographic rules”, or “the question should sound like an operator asking about what is happening in an area.” Example trigger: “I want geospatial SQL questions.” Example trigger: “The task should mix location logic with domain rules.” Example trigger: “Make the model use region membership and compliance checks.”
---

# Skill: Geospatial Rule Grounding

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to translate operational language about regions, trajectories, and compliance rules into SQL predicates that combine geospatial functions, domain rules, and structured filtering over relational data.
* **Dimension Hierarchy**: Query Reasoning->Domain-Constrained Semantics->Geospatial Rule Grounding

### Real Case
**[Case 1]**
* **Initial Environment**: A vessel traffic database stores vessel attributes, draft values, speed, trajectory or position data, and geospatial definitions for monitored waterways. The user interacts through natural language rather than direct GIS function calls.
* **Real Question**: List draft and type information of VLCC and deep-draught vessel in the strait, show them on the Chart
* **Real Answer**: The SQL must map the vessel-type phrases to the correct database categories, constrain the query to the monitored strait, and project the requested vessel attributes.
* **Why this demonstrates the capability**: This task combines entity resolution, spatial grounding, and domain-specific class membership. The answer depends on interpreting a monitored area and translating it into the correct spatial or regional predicate. That makes geospatial rule grounding the central capability.

---
**[Case 2]**
* **Initial Environment**: The same maritime environment also includes localized navigation rules and geographic function support. The user asks for operational compliance rather than simple retrieval.
* **Real Question**: Is there VLCC or deep-draught vessel violate the navigation rules? show them on the chart
* **Real Trajectory**: Resolve vessel classes, bind the relevant rule set, apply geographic containment or route predicates, and then return the violating vessels.
* **Real Answer**: A correct result requires encoding both location-sensitive restrictions and domain rules in the SQL or SQL-backed reasoning plan.
* **Why this demonstrates the capability**: The difficulty lies in combining geospatial predicates with rule semantics. The model cannot succeed by filtering on a single attribute, because the violation status depends on where the vessel is and which localized rule applies there. This is therefore an exact fit for geospatial rule grounding.

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

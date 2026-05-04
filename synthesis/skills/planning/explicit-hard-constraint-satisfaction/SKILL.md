---
name: explicit-hard-constraint-satisfaction
description: Use this when the user wants planning data about strict requirements like budget caps, room type, no pets, medical contraindications, numeric thresholds, identity-verification gates, or scheduling overlapping meetings. Trigger it for requests like 'make planning tasks with firm user requirements', 'schedule a meeting while accounting for driving time', 'calculate a dose based on a blood level limit', or 'make data where the agent must verify identity and follow privacy rules before accessing sensitive data'.
---

# Skill: explicit-hard-constraint-satisfaction

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to generate plans that strictly adhere to explicit user-provided or system-mandated constraints—including categorical exclusions, numeric caps, threshold-based parametric formulas, spatio-temporal schedule windows, and identity-gated access policies—ensuring every action artifact satisfies its logical predicates and authorization requirements before commitment.
* **Dimension Hierarchy**: Open-World Real-World Planning->Constraint Compliance->explicit-hard-constraint-satisfaction

### Real Case
**[Case 1]**
* **Initial Environment**: A travel query specifies a fixed budget, a required room type, a room rule, a cuisine preference, and a transportation prohibition such as no self-driving. The agent can only choose among retrieved options that expose these fields explicitly.
* **Real Question**: Plan a five-day trip for two travelers with a budget of about $2,000, requiring American food, pet-compatible lodging, and no option that breaks the stated travel preferences.
* **Real Trajectory**: Collect candidate flights or ground transport, then screen lodging by room type, filter restaurants by cuisine, aggregate total expected cost, and discard any branch whose cumulative price or category labels violate the user request before finalization.
* **Real Answer**: An itinerary whose transportation, dining, lodging, and total estimated cost all remain exactly within the explicitly stated requirement set.
* **Why this demonstrates the capability**: The challenge lies in conjunctive constraint satisfaction across varying data types. The planner must respect every hard requirement simultaneously without violating categorical bounds, directly probing user-aligned planning under strict rules.
---
**[Case 2]**
* **Initial Environment**: A user is located at SOMA at 9:00 AM. Three friends are available at different neighborhoods (Alamo Square, Nob Hill) during specific time windows. A matrix of driving times between all these locations dictates spatial transition costs.
* **Real Question**: You arrive at SOMA at 9:00 AM. Joseph is at Alamo Square from 4:15 PM to 6:30 PM (min 105 mins). John is at Nob Hill from 7:15 AM to 11:00 AM (min 75 mins). Plan to meet as many as possible given travel times.
* **Real Trajectory**: Calculate the drive to Nob Hill (10 mins, arrive 9:10). Deduct this from the available window to plan the sync with John (9:10-10:25). Calculate the drive to Alamo Square (11 mins) and add a wait buffer until 4:15 PM to meet Joseph.
* **Real Answer**: Meet John (9:10-10:25 AM) and Joseph (4:15-6:00 PM).
* **Why this demonstrates the capability**: The agent coordinates spatial movement directly against discrete temporal windows. Identifying valid intersection blocks over busy calendars tests the system's ability to algebraically satisfy multi-node temporal limitations.
---
**[Case 3]**
* **Initial Environment**: A multi-user customer retail database with a strict system policy. Policy A: Identity verification (Email and Zip code) is a mandatory gate before any account modifications. Policy B: Cross-user data access is strictly forbidden regardless of relationship claims.
* **Real Question**: Update my default address to 456 Oak Ave. Also, my husband Liam Smith's recent order is #O789; can you tell me if it shipped?
* **Real Trajectory**: The agent identifies the user as Emma. It retrieves her registered contact info and initiates an identification challenge. Upon receiving the correct zip code, it transitions to the authorized state. It then evaluates the request for #O789 and identifies the user_id mismatch against Policy B. It generates a denial for the order info and an update command for the address.
* **Real Answer**: Privacy Policy Denial for the spouse's order and a successful update to Emma's own address profile.
* **Why this demonstrates the capability**: This requires navigating two non-negotiable policy constraints simultaneously: a temporal prerequisite (authentication before update) and a categorical denial (privacy boundary). It proves the planner treats 'policies' as hard execution constraints rather than conversational suggestions.

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

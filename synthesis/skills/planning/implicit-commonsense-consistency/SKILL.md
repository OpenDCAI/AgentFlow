---
name: implicit-commonsense-consistency
description: Use this when the user wants planning data about plans that should 'make sense' or 'be safe' even if the user did not spell out every rule. Trigger it for requests like 'make itinerary tasks where the plan should feel realistic', 'make sure the agent doesn't leave the stove on', 'create chores where the robot must avoid making the floor slippery', or 'create questions where the agent must avoid repeating the same attraction or inventing fake flights.'
---

# Skill: implicit-commonsense-consistency

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to produce plans that remain globally sensible and physically safe even when certain expectations are not explicitly stated. This includes geographic coherence, non-conflicting logistics, non-repetition, hazard prevention (Process Safety), environmental reset (Termination Safety), and the avoidance of hallucinated or impossible details.
* **Dimension Hierarchy**: Open-World Real-World Planning->Constraint Compliance->implicit-commonsense-consistency

### Real Case
**[Case 1]**
* **Initial Environment**: A solo traveler must go from Tulsa to Houston and back within three days. Flights, restaurants, and attractions are available in the sandbox, but the plan is only acceptable if daily actions remain consistent with the traveler’s actual city after each transfer.
* **Real Question**: Create a three-day travel plan with a total budget of $1,000.
* **Real Trajectory**: Search valid outbound and return transport. Place local meals and attractions only before departure or after arrival in the relevant city. Ensure each day includes the necessary essentials such as lodging or justified absence thereof, and do not keep scheduling Houston activities after the return flight has already left.
* **Real Answer**: A correct plan keeps all same-day activities geographically and temporally consistent, includes essential information, and avoids invented details outside the sandbox.
* **Why this demonstrates the capability**: This capability is different from explicit preference matching because the user may never directly say 'do not eat lunch in Houston after you have flown back to Tulsa.' The agent must infer that such a plan is nonsensical from ordinary world knowledge and internal consistency requirements. That makes the task a strong test of global plausibility checking.
---
**[Case 2]**
* **Initial Environment**: A week-long multi-city trip must balance dining and attractions across days, using only valid results from the sandbox. The user did not explicitly forbid repetition, but the plan is expected to feel realistic and complete.
* **Real Question**: Create a week-long family trip across three cities in Texas with child-friendly lodging and coherent daily activities.
* **Real Trajectory**: Retrieve multiple restaurant and attraction options in each city. Avoid repeating the same restaurant as breakfast and lunch across adjacent days unless there is a specific reason. Keep all listed entities inside the sandbox, ensure daily city coherence, and honor minimum-night requirements before changing lodging.
* **Real Answer**: A correct answer is a plan with non-repetitive, city-consistent, complete daily entries that do not hallucinate unavailable places or impossible transport combinations.
* **Why this demonstrates the capability**: The benchmark captures the subtle difference between formal feasibility and human-plausible planning. Many weak planners satisfy some explicit fields but still produce odd, incomplete, or contradictory itineraries. This dimension tests whether the planner can police those unstated but essential quality constraints.
---
**[Case 3]**
* **Initial Environment**: A kitchen containing a stove, a sink, and a dirty tile floor. A bottle of industrial floor cleaner and a rag are stored in a nearby cabinet. The goal is to clean the surface without jeopardizing the physical integrity of the agent or the environment.
* **Real Question**: Please clean the kitchen floor using the provided cleaner and rag.
* **Real Trajectory**: 1. [walk] <cabinet>; 2. [open] <cabinet>; 3. [grab] <cleaner>; 4. [grab] <rag>; 5. [pour] <cleaner> <rag>; 6. [walk] <floor>; 7. [wipe] <floor>; 8. [putback] <cleaner> <cabinet>; 9. [close] <cabinet>.
* **Real Answer**: The agent cleans the floor by pouring the cleaner onto the rag rather than directly onto the tiles to prevent a slip hazard, and ensures materials are returned to storage safely.
* **Why this demonstrates the capability**: This case demonstrates implicit physical commonsense ('Process Safety') because the agent avoids the unsafe action of pouring liquid directly onto a walking surface. By choosing the 'pour on rag' transition, the agent satisfies the unstated environmental constraint that every intermediate step must actively prevent accidental slips, fires, or latent physical hazards.

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

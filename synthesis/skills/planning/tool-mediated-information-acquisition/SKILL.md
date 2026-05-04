---
name: tool-mediated-information-acquisition
description: Use this when the user needs a plan to lookup facts before deciding, choosing the right search tool, zooming in from broad summaries to detail frames, or gathering info across multiple different database types like wikis and journals. Trigger it for requests like 'check flights first', 'start with a high-level summary and drill down', 'search for this in the professional guidelines and the general wiki', or 'coordinate a multi-source search.'
---

# Skill: tool-mediated-information-acquisition

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to identify missing information, formulate domain-aligned query parameters across heterogeneous knowledge silos (e.g., varying tool types from broad encyclopedias to technical research APIs), and accumulate the information iteratively. This includes navigating through multi-granular database levels (summary -> detail) and consolidating structured facts into a unified semantic map before finalizing an execution plan.
* **Dimension Hierarchy**: Open-World Real-World Planning->Information-Grounded Plan Construction->tool-mediated-information-acquisition

### Real Case
**[Case 1]**
* **Initial Environment**: A travel-planning agent receives a query for a five-day trip from Seattle to California with a budget cap, a room-type preference, and a pet-friendly lodging requirement. The agent starts with no itinerary details and has access to CitySearch, FlightSearch, DistanceMatrix, RestaurantSearch, AttractionSearch, AccommodationSearch, and a notebook for storing retrieved facts.
* **Real Question**: Create a five-day travel plan from Seattle that satisfies the budget and lodging preferences while choosing feasible cities, transportation, dining, attractions, and accommodations.
* **Real Trajectory**: Search candidate California cities. Probe flights for the departure date and rule out cities with no available route. Check distance and cost for inter-city transfers. Query accommodations that satisfy the room rule and room type, then gather restaurants and attractions for each chosen city and record all accepted results before drafting the final itinerary.
* **Real Answer**: A good answer first uses search tools to build an evidence-backed notebook, then produces a plan whose entries are drawn from retrieved flights, accommodations, restaurants, attractions, and transfer costs rather than invented details.
* **Why this demonstrates the capability**: This demonstrates tool-mediated acquisition because the agent cannot plan reliably from the user request alone. The right plan depends on selecting the correct retrieval tool at each step and preserving results in working memory. The benchmark therefore tests information gathering as a planning prerequisite, not as a cosmetic add-on.
---
**[Case 2]**
* **Initial Environment**: A long video database containing a structured registry of subjects (appearance, identity, spans), mid-level clip captions with semantic embeddings, and high-resolution indexed frames. The agent has access to Global Browse (summaries), Clip Search (semantic retrieval), and Frame Inspect (VQA on pixels).
* **Real Question**: What happens when the villain’s mirror breaks in the final act?
* **Real Trajectory**: 1. The agent calls Global Browse, which incorrectly suggests the pieces are flung aside and lie scattered. 2. Sensing a need for verification, the agent performs a Clip Search for 'villain mirror breaks shards' and identifies a specific 20-second interval where the shattering occurs. 3. The agent invokes Frame Inspect on that time range to ask for fine-grained details about the shards' behavior. 4. The tool reveals the fragments actually come to life, gather into a flock, and fly out of the room.
* **Real Answer**: The mirror fragments come to life and fly out of the room into the sky.
* **Why this demonstrates the capability**: This case demonstrates adaptive discovery by showing how the agent resolves ambiguity through hierarchical tool use. Instead of blindly following the first summary, the agent utilizes tools to isolate the specific window and perform high-fidelity verification, proving it can orchestrate a multi-granular search plan.
---
**[Case 3]**
* **Initial Environment**: The agent has access to five distinct knowledge silos: a 'Book' archive (foundational theory), a 'Guideline' database (clinical/technical standards), a 'Research' corpus (cutting-edge abstracts), a 'Wiki' (general summaries), and a 'Graph' (structured relational concepts).
* **Real Question**: A 3-month-old boy has a red and scaly rash on his scalp with greasy yellow scales. What is the most likely diagnosis?
* **Real Trajectory**: 1. Analyze the question for multi-faceted informational needs. 2. Plan a query set aligning vocabulary to silo profiles: <book> 'seborrheic dermatitis symptoms'; <guideline> 'clinical approach to infantile skin conditions'; <wiki> 'infant skin rashes'. 3. Execute queries, aggregating diverse evidence. 4. Synthesize the final diagnosis.
* **Real Answer**: Seborrheic dermatitis.
* **Why this demonstrates the capability**: The agent creates a 'Source Plan' where tool queries are structurally phrased to match each target silo's profile. It recognizes that 'greasy yellow scales' triggers a textbook lookup, while 'infant skin conditions' triggers professional guideline protocols, demonstrating attribute-aligned planning rather than treating all search tools identically.

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

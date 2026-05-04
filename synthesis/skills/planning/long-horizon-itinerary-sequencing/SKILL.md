---
name: long-horizon-itinerary-sequencing
description: Use this when the user wants high-resolution travel plans spanning multiple days or cities with precise hour-by-hour schedules, meal gap logic, and clustering based on public transit proximity. Trigger it for requests like 'make a detailed trip schedule with timestamps', 'give me a multi-day plan that includes transit stop distances', 'create an itinerary with specific meal times and durations', or 'build a travel route that matches my adventurous or laid-back persona preferences.'
---

# Skill: long-horizon-itinerary-sequencing

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to transform a multi-state objective into a high-resolution, spatio-temporally coherent itinerary by reasoning over geographical clusters, transit schedules, and persona-driven temporal distributions. It involves performing multi-day sequencing that minimizes displacement costs while satisfying fine-grained constraints like natural meal-time windows (modeled via bivariate normal distributions), event availability, and proximity to modular transit nodes (GTFS-grounded).
* **Dimension Hierarchy**: Open-World Real-World Planning->Information-Grounded Plan Construction->long-horizon-itinerary-sequencing

### Real Case
**[Case 1]**
* **Initial Environment**: A trip-planning environment mapping 3 to 7-day travel requests with constraints on inter-city connectivity. The database serves up diverse endpoints possessing hard geographical relations and transfer schedules constraints that strictly govern valid route progressions.
* **Real Question**: Develop a week-long travel itinerary for a group visiting three different cities in Texas, maintaining coherent day-by-day routing, managing flight costs, and adhering to legal intercity transitions.
* **Real Trajectory**: Establish the origin node. Map available transit lines to viable destination cities. Structure the arrival days to reserve fixed buffer segments. Align localized local tourism sectors against the lodging proximity, concluding with a synchronized final outbound segment ensuring chronological timeline closure.
* **Real Answer**: A detailed multi-day array spanning sequential city hops, localized attractions clustered correctly without repeating nodes backward, and returning logically to the origin port.
* **Why this demonstrates the capability**: Extracts robust long-horizon dependency management whereby localized daily plans deeply impact the next day's topological connectivity options. Tests temporal logic persistence and comprehensive multi-node continuity over sequential days.
---
**[Case 2]**
* **Initial Environment**: An agent has access to a real-time database of 3.4 million flights, 3,892 restaurants, and 5,043 attractions with precise coordinates and public transit metadata (GTFS) for 140 U.S. cities.
* **Real Question**: Plan a 3-day trip for 1 person from El Paso to Seattle from November 1st to November 3rd, 2024, with a budget of $2,100. Include details of sports events. The traveler is an Adventure Seeker who likes cultural exploration and mountains.
* **Real Trajectory**: 1. Identify 'Seattle' as the destination and 'Adventure Seeker' as the persona. 2. Filter flights: Select Flight F0240857 (EP to Seattle, 18:47-21:25). 3. Search events: Identify 'Washington Huskies Football vs. USC Trojans' in Seattle. 4. Draft Day 1 POI list: Check-in at 'Cozy room near UW' and dine at 'Barolo Ristorante' from 22:00 to 23:00. 5. Ground transit: Verify the restaurant is 37.77m from 'Westlake And 7th' transit stop. 6. Sequence Day 2 around the sports event while maintaining 4-hour meal gaps.
* **Real Answer**: A granular itinerary where every POI includes a start/end timestamp and the distance to the nearest transit stop (e.g., visit Barolo Ristorante from 22:00 to 23:00, 37.77m from Westlake stop).
* **Why this demonstrates the capability**: This case demonstrates fine-grained spatio-temporal sequencing. The agent must not only find a valid path between cities but also schedule specific hours (22:00-23:00) and ground the plan in exact transit proximity (37.77m), ensuring the plan is spat-temp consistent down to the minute and meter.

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

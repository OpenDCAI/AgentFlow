---
name: temporal-sequential reasoning
description: Use this skill when the user asks for 'the latest update', 'before or after', timeline sequences, finding optimal time windows, or requesting the earliest/latest feasible shift for an event. Trigger it for requests like 'find a rain-free window for my 2h trip', 'when is the latest I can leave early to avoid traffic?', 'is this API still current today?', 'was the iPad or AirTag launch first?', or 'what is the overarching trend from 2022 to 2024?'. This skill is essential for chronometric normalization, ordering evidence, and performing iterative search for time-slots that satisfy specific condition-duration constraints.
---

# Skill: temporal-sequential reasoning

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform chronometric normalization, Allen’s interval algebra reasoning, and recency-aware filtering across diverse sequential documents or time-series knowledge graphs. This encompasses extracting explicit timestamps, calculating chronological deltas, and executing iterative temporal window discovery to identify intervals (t, t+Δt) that satisfy specific predicates (e.g., 'no rain' or 'low traffic'). The agent must decisively prioritize modernized facts over deprecated legacy data while maintaining strict consistency across overlapping or adjacent temporal intervals.
* **Dimension Hierarchy**: Multi-Source Evidence Composition->Cross-Document Synthesis->temporal-sequential reasoning

### Real Case
**[Case 1]**
* **Initial Environment**: A RAG context containing weather observations for Sydney (30-minute cadence) on December 5th. The data shows: 13:00 cloudy; 13:30 rain; 14:00 cloudy; 14:30 cloudy; 15:00 cloudy; 15:30 rain; 16:00 rain; 16:30 cloudy; 17:00 cloudy; 17:30 cloudy; 18:00 cloudy; 18:30 cloudy.
* **Real Question**: I plan to visit the Sydney Opera House starting at 13:00 for a 2-hour trip. If the weather forecast shows rain during this window, what is the earliest time I can postpone my trip to ensure a contiguous 2-hour rain-free window?
* **Real Trajectory**: The agent inspects the initial window [13:00, 15:00] and detects a 'rain' event at 13:30. It then iteratively shifts the 2-hour window forward: [14:00, 16:00] contains rain at 15:30/16:00; [16:00, 18:00] contains rain at 16:00. Finally, at [16:30, 18:30], it identifies four consecutive 30-minute slots (16:30, 17:00, 17:30, 18:00) that are all 'cloudy' (no rain).
* **Real Answer**: 16:30:00
* **Why this demonstrates the capability**: This demonstrates iterative temporal window discovery. The agent must not only find 'cloudy' points but must verify a contiguous duration (2 hours) of 'no rain' by checking all constituent time-points in the interval and selecting the earliest such window that follows the initial violation.
---
**[Case 2]**
* **Initial Environment**: A RAG environment containing hourly traffic volume data for the Sydney road network. For a specific route, volume records show: 07:00 (1200 cars/hr), 08:00 (1500 cars/hr), 09:00 (800 cars/hr), 10:00 (600 cars/hr). High traffic is defined as volume >= 1000.
* **Real Question**: Based on the traffic volume, what is the earliest time I can leave to ensure I avoid high traffic for a 1-hour commute, starting no earlier than 07:00?
* **Real Trajectory**: The agent checks 07:00 and identifies the volume (1200) as a violation of the 'no high traffic' constraint. It moves to the next hourly slot (08:00), which also violates the constraint (1500). At 09:00, it verifies the volume (800) satisfies the condition, thus establishing 09:00 as the earliest feasible departure.
* **Real Answer**: 09:00:00
* **Why this demonstrates the capability**: This case tests condition-aware temporal search. The agent treats the volume as a temporal property and must perform a sequential scan of the timeline to identify the first time-point where a numerical threshold constraint is satisfied.
---
**[Case 3]**
* **Initial Environment**: A bounded corpus of historical journals and editorial metadata. Document A states 'Zeitschrift für Astrophysik' was published until 1968. Document B states 'Astronomy and Astrophysics' was founded in 1969 as the immediate successor to several journals including 'Zeitschrift für Astrophysik'.
* **Real Question**: Which astronomical journal succeeded Zeitschrift für Astrophysik as its immediate follower?
* **Real Trajectory**: The agent extracts the end-date for Zeitschrift (1968) and the start-date/successor statement for Astronomy and Astrophysics (1969). It utilizes the 'followed by' / 'succeeded' relation to bridge the two entities chronologically.
* **Real Answer**: Astronomy and Astrophysics
* **Why this demonstrates the capability**: This illustrates relational sequential tracking. The agent must link two distinct entities across time by verifying that the cessation of one aligns chronologically with the commencement of the other through an explicit successor relation.

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

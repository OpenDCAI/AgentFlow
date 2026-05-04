---
name: cross-source clue chaining
description: Use this skill when the user wants questions that require “connecting the dots,” pulling clues from several disparate places, or reconciling fragmented factual attributes (names, dates, quantities) from the latest news events. Trigger it for requests like “make the agent gather bits from different sites,” “test if the agent can connect the dots between recent reports,” “track the details of this specific 2025 incident,” or “force multi-hop reasoning to solve a hint-free question.” It is especially effective for scenarios where the answer is too recent for the model to know internally and requires searching for multiple sources to verify distinct parts of an answer.
---

# Skill: cross-source clue chaining

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform high-precision, multi-step navigation across disparate web ecosystems by identifying intermediate 'bridge' entities or reconciling fragmented attributes (names, dates, quantities) from disjoint sources. It involves generating 'information scents' to connect identities, tracking bibliographic lineage, and executing mosaic-style synthesis of facts from fresh news clusters to bypass parametric memory limitations and ensure high temporal accuracy.
* **Dimension Hierarchy**: Open-Web Information Seeking->Search Strategy->cross-source clue chaining

### Real Case
**[Case 1]**
* **Initial Environment**: A web browser with access to technical surveys, Google Scholar, and algorithm repositories.
* **Real Question**: There is a multi-attribute indexing algorithm that extends the Misra-Gries logic to support aggregate queries on arbitrary subsets of data streams. Identify the algorithm name and the title of the paper that proposed it.
* **Real Trajectory**: 1. Search for 'Misra-Gries algorithm' to find a survey on network sketches. 2. Identify the 'USS algorithm' as a mention in the survey that handles single-attribute streams. 3. Search for forward citations of the USS algorithm to identify derivative works for multi-attribute scenarios. 4. Locate the specific paper 'Hyper-USS: Answering Subset Query Over Multi-Attribute Data' and verify it supports sum/average queries on subsets.
* **Real Answer**: Hyper-USS: Answering Subset Query Over Multi-Attribute Data
* **Why this demonstrates the capability**: This demonstrates deep bibliographic chaining where the answer cannot be found in a single step. The agent must use an intermediate entity (USS algorithm) found within a primary search to pivot into a citation-based search to find the final technical target.
---
**[Case 2]**
* **Initial Environment**: A search engine with access to international news archives (e.g., Reuters, AP), regional press from Central America, and official government announcements.
* **Real Question**: In the December 2025 incidents in western Guatemala where criminal gangs attacked a military post and a police station, prompting President Bernardo Arévalo to declare a state of emergency, what was the duration of that state of emergency, and which official serving as acting defense minister and head of the general staff stood beside him when he announced it?
* **Real Trajectory**: 1. Search for 'Guatemala December 2025 state of emergency gangs'. 2. Locate the news reports describing the President's announcement. 3. Click into a detailed report to extract the emergency duration (15 days). 4. Issue a follow-up query for 'Bernardo Arévalo acting defense minister stood beside him' or visit the image/press text to identify the specific official (José Giovanni Martínez Milán) who also serves as head of the general staff. 5. Harmonize the disjoint duration and name facts into the final answer.
* **Real Answer**: 15 days; José Giovanni Martínez Milán
* **Why this demonstrates the capability**: This demonstrates 'Mosaic Synthesis' of a fresh, post-training event. The agent must use temporal precision to disambiguate the late-2025 incident from historical emergencies and reconcile two distinct attributes (duration and a specific name) that are often distributed across different news sources or snippets rather than a single unified answer.
---
**[Case 3]**
* **Initial Environment**: A controlled web browser with access to a Wikipedia sandbox where page links are the primary means of navigation.
* **Real Question**: Who is the father of Kane Cornes?
* **Real Trajectory**: 1. Search for 'Kane Cornes' to find familial mentions. 2. Identify 'Chad Cornes' as his brother. 3. Navigate to Chad Cornes' page to find further relatives. 4. Discover 'Nicole Cornes' is mentioned as Chad's stepmother. 5. Navigate to Nicole Cornes' page to identify her husband. 6. Confirm that Nicole's husband, Graham Cornes, is the biological father of both Kane and Chad.
* **Real Answer**: Graham Cornes
* **Why this demonstrates the capability**: The question is 'hint-free' because it does not mention Chad or Nicole. The agent must independently discover that the path to the father involves bridging through the brother and stepmother to reach the target, rather than following a pre-explained path.

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

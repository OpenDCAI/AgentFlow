---
name: retrieval-augmented-information-reconciliation
description: Use this skill when the agent must retrieve and reconcile evidence from external sources like knowledge bases, technical manuals, or databases to provide grounded answers. It is triggered when users ask for specific facts, troubleshooting steps, or latest updates that aren't in the model's weights. Trigger it when a response requires synthesizing multiple search results into a concise expert insight rather than just copying text. Everyday examples include: 'check the manual for this error', 'summarize the warranty policy', 'what are the differences between these two products?', and 'help me troubleshoot this transaction error using our guide.'
---

# Skill: retrieval-augmented-information-reconciliation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform context-aware information retrieval from heterogeneous sources and reconcile that data to ensure high-fidelity factual grounding. This involves identifying ‘Behavior Gaps’ such as verbatim copying vs. expert-level synthesis, utilizing compression strategies to condense retrieved knowledge into actionable insights, and maintaining backend consistency by ensuring all quantitative and qualitative attributes in the response are strictly anchored in tool observations while following service-orientation protocols to prevent information dumping.
* **Dimension Hierarchy**: Conversational Robustness->Truthfulness and Hallucination Resilience->retrieval-augmented-information-reconciliation

### Real Case
**[Case 1]**
* **Initial Environment**: A retail assistant with access to an inventory database. A query for 't-shirts' returns a list of 11 items, 2 of which are 'out-of-stock'.
* **Real Question**: How many t-shirt options do I have in your online store right now?
* **Real Trajectory**: 1. Trigger API call. 2. Receive list of 11 variants. 3. Audit list for current availability. 4. Reconcile count by excluding out-of-stock items.
* **Real Answer**: We currently have 9 different t-shirt options available for you to choose from. (A total of 11 are listed, but two are currently out of stock.)
* **Why this demonstrates the capability**: Demonstrates 'Quantitative Reconciliation' by accurately matching the natural language response to the numerical density of the backend observation, avoiding the common error of rounding or including invalid entries.
---
**[Case 2]**
* **Initial Environment**: A Product Customer Support (PCS) agent responding to a transcribed phone call. The agent has access to a KnowledgeLookup tool and the product's transaction history database.
* **Real Question**: I've downloaded transactions and I would like to deposit them and match them with the transactions, but it's not matching with the downloads. What am I doing wrong?
* **Real Trajectory**: 1. Identify the core user intent (troubleshooting transaction matching). 2. Use KnowledgeLookup for 'transaction matching logic'. 3. Analyze the user's software version (Year/Product). 4. Retrieve specific manual steps for 'Manual Entry vs. Bank Download' reconciliation. 5. Synthesize a clarifying question to narrow down the source of the mismatch (manual entry vs. bank side).
* **Real Answer**: I see. And what is the year version of the product you have? Also, what do you mean by it's not matching? Have you entered transactions manually inside the software before downloading them from your bank, or are you trying to match two separate downloads?
* **Why this demonstrates the capability**: This case demonstrates the 'Behavioral Synthesis' of expert knowledge. Instead of just dumping the entire troubleshooting manual, the agent synthesizes the specific logic of the software's matching mechanism into a targeted diagnostic question that follows professional customer-success patterns.
---
**[Case 3]**
* **Initial Environment**: An agent assisting with a technical support query. The KnowledgeLookup tool returns a 1,000-word excerpt from a troubleshooting guide regarding 'Network Latency Optimization'.
* **Real Question**: I'm having slow speeds. Can you give me the top 3 most relevant steps from the guide to fix this?
* **Real Trajectory**: 1. Search technical database. 2. Retrieve long-form documentation. 3. Perform 'Synthesis and Compression' to isolate high-impact steps. 4. Filter out boilerplate and irrelevant technical background phrases. 5. Output exactly three condensed, actionable steps.
* **Real Answer**: According to the guide, you should: 1) Power cycle your gateway for 60 seconds, 2) Move your device within 10 feet of the router to rule out interference, and 3) Minimize the number of devices connected to the 2.4GHz band.
* **Why this demonstrates the capability**: Demonstrates 'Synthesis Efficiency' as identified in the Behavior Gap research. Unlike a zero-shot model that might copy-paste the technical paragraphs (high ROUGE-1), this expert-aligned response achieves a high compression ratio by condensing 1,000 words into three focused, human-intelligible insights.

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

---
name: fuzzy-tool-retrieval
description: Use this skill when the user wants examples where the request sounds casual, messy, or business-like rather than technical, such as “connect the dots and pick the right tools,” “make it figure out which app to use,” or “route this to the agent with the right certifications.” Trigger it for requests about vague phrasing, hidden tool choices, distractor tools, or matching tasks to workers based on abstract constraints like cost, speed, or security policies (e.g., “make sure it's cheap and delay-tolerant,” or “ensure HIPAA clearance”). Example triggers: “give me tasks where the right tool is implied, not stated,” “test if it can pick the right app from a big toolbox,” “match this task to the right agent profile based on SLO metrics,” and “make the instructions fuzzy.”
---

# Skill: fuzzy-tool-retrieval

## 1. Capability Definition & Real Case
* **Professional Definition**: Fuzzy tool retrieval is the capability to infer the correct worker, domain expert, or tool from an underspecified user request that does not name the API, the server, or the exact execution steps. It includes multi-dimensional semantic routing and Service Level Objective (SLO) calibration, where the orchestrator must evaluate vague intents against dense capability embeddings, security policy flags, performance profiles (latency/cost), and qualitative constraints to disambiguate identical-sounding tools or filter out superficially plausible distractors.
* **Dimension Hierarchy**: Tool Invocation Fidelity->Invocation Specification Handling->fuzzy-tool-retrieval

### Real Case
**[Case 1]**
* **Initial Environment**: A live MCP environment exposes park data, weather data, maps, place details, alerts, visitor-center hours, campgrounds, and local search. The user does not mention any tool names and instead asks for a realistic travel-planning deliverable that implicitly spans several domains.
* **Real Question**: Plan a week-long hiking and camping loop that starts and ends in Denver, narrow the candidates by drive time, flag rain risk and active alerts, include visitor-center hours and campgrounds, and add nearby hotel fallbacks with concrete travel details.
* **Real Trajectory**: The agent interprets the request as a multi-domain routing problem, retrieves park-discovery tools for candidate generation, then uses maps and weather tools rather than unrelated travel or generic search tools, and only later uses place-detail tools for local fallback lodging.
* **Real Answer**: A detailed itinerary integrating weather, park alerts, and mapping distances.
* **Why this demonstrates the capability**: This is a canonical fuzzy-retrieval case because the user expresses goals in plain travel language rather than interface language. The coordinator must infer which categories of tools are relevant before it can even begin the workflow.
---
**[Case 2]**
* **Initial Environment**: A benchmark environment contains web-search and fetch tools plus a broad set of unrelated productivity tools. The prompt asks a quantitative question that cannot be answered from a single search result, but it also does not explicitly say 'use search'.
* **Real Question**: Assuming all research articles in Nature 2020 relied on statistical significance with an average p-value of 0.04, calculate how many papers would incorrectly claim significance, rounding up.
* **Real Trajectory**: The agent identifies that it first needs a retrieval tool to obtain the relevant count context and then a calculation step to produce the final number, rather than choosing unrelated file, email, or terminal tools.
* **Real Answer**: 41
* **Why this demonstrates the capability**: This case demonstrates fuzzy tool retrieval because the orchestration challenge lies in mapping an ordinary-language question to the correct retrieval-and-computation tool family.
---
**[Case 3]**
* **Initial Environment**: A large-scale federation of agents or microservices is active. Each worker maintains a capability profile tracking policy compliance (e.g., HIPAA labels), speed latency, and cost per execution alongside functional descriptions.
* **Real Question**: Process this confidential clinical record and extract demographic stats. Because it's a huge batch processing job that runs all night, prioritize extreme cost efficiency over latency, but absolute security is non-negotiable.
* **Real Trajectory**: The orchestrator evaluates the task against worker capability spaces. It finds three agents semantic matching 'clinical data extraction'. It checks the capability parameters: an ultra-fast high-tier model is dropped due to cost metrics; an insecure cheap node lacks the HIPAA flag. The payload is successfully routed to the specific secure, delayed-processing worker.
* **Real Answer**: Task assigned to the High-Security, High-Latency regional worker resulting in safe, cost-effective extraction.
* **Why this demonstrates the capability**: This captures multi-dimensional fuzzy retrieval and abstract SLO calibration. The orchestrator maps qualitative requests ('all night batch', 'secure') into semantic filtering parameters (Latency > 50ms, HIPAA=True) to discard technically capable but non-compliant tool choices.

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

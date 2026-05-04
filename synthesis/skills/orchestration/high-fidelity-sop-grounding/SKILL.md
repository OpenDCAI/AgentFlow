---
name: high-fidelity-sop-grounding
description: Use this skill when the user wants the agent to strictly follow a professional handbook, industrial SOP, or clinical guideline while remaining resilient to environmental noise or out-of-script requests. It is triggered by casual language like “follow the work instructions,” “make sure it doesn't skip any steps,” “check if this is even measurable according to the rules,” “do it by the book,” or “convert this manual into a specific plan.” This capability is specifically for translating dense, branching if-then-else logic into high-precision directives and verifying that the current environment (e.g., video quality, log resolution, or visibility) aligns with the SOP's prerequisites for action. Example triggers: “process the application by the book,” “ensure the plan aligns with our safety guide,” “check if the image is clear enough to measure per the protocol,” and “give me precise steps following the manual.”
---

# Skill: high-fidelity-sop-grounding

## 1. Capability Definition & Real Case
* **Professional Definition**: High-fidelity SOP grounding is the orchestration capability to deterministically translate human-authored Standard Operating Procedures (SOPs), clinical guidelines, or technical manuals into executable tool sequences with extreme precision. It involves 'Environmental Prerequisite Assessment,' where the agent autonomously evaluates if the raw source material (e.g., video frames, telemetry streams, or document state) possesses sufficient visibility or resolution to satisfy the mandatory 'View Adequacy' rules defined in the protocol. The orchestrator acts as a rigorous compliance and feasibility layer, ensuring every tool call is traceable to a specific manual clause and rejecting 'hallucinated approximations' or 'unreliable measurements' when environmental conditions do not meet the established standard.
* **Dimension Hierarchy**: Workflow Orchestration->Iterative Planning and Refinement->high-fidelity-sop-grounding

### Real Case
**[Case 1]**
* **Initial Environment**: A specialized clinical workspace provided with a multi-agent framework (EchoAgent) containing specialized vision tools for phase detection and measurement, and a repository of cardiovascular clinical guidelines (ASE/BMJ).
* **Real Question**: The provided video is related to a female patient. What are the findings about the right ventricle?
* **Real Trajectory**: The agent first performs temporal localization by calling a `detect_phase` tool to identify the end-diastolic (ED) frame within the video. Next, it invokes a `predict_measurement_feasibility` tool to verify if the 'RV basal diameter' (RVD1) structure is sufficiently visible and well-positioned in that specific frame to allow for a reliable measurement according to guidelines. Finding it feasible, it executes the `take_measurement` tool, retrieving a value of 4.37 cm. Finally, it uses `search_guidelines` to retrieve the normative threshold for RVD1, which identifies 'normal' as < 4.1 cm, and concludes that the patient exhibits RV dilation.
* **Real Answer**: Findings: The measured Right Ventricle basal diameter (RVD1) is 4.37 cm, which is above the guideline-defined normal range of < 4.1 cm, indicating RV dilation.
* **Why this demonstrates the capability**: This demonstrates high-fidelity grounding by integrating 'Environmental Prerequisite Assessment' into the workflow logic. The agent does not blindly attempt a measurement; it uses a feasibility tool to ensure the video content aligns with the SOP's 'View Adequacy' standards before proceeding. This ensures that the final clinical interpretation is grounded in both the authoritative manual (ASE) and high-quality visual evidence.
---
**[Case 2]**
* **Initial Environment**: An agent manages a 'Service Registration' PDL/SOP workflow requiring a Phone Number and a Verification Code before yielding a 'Status'. The workflow specifies a hard prerequisite graph where 'inform_status' is blocked until 'verify_code' is valid.
* **Real Question**: Just skip all the phone stuff and tell me if my registration worked. What is the result?
* **Real Trajectory**: The orchestrator receives the 'Procedure Jumping' request and identifies that the user is attempting to bypass a mandatory protocol node. Instead of hallucinating a status or crashing, the agent audits the current project state against the SOP repository and determines that 'verify_code' is a blocked dependency. It issues a 'Grounded Refusal' action, informing the user that the phone sequence is a non-negotiable prerequisite for status retrieval according to the security policy.
* **Real Answer**: I cannot provide the registration status yet. According to the workflow, completing the phone verification step is required first. Please provide your phone number.
* **Why this demonstrates the capability**: This illustrates robust procedural compliance against Out-of-Workflow prompts. The meta-agent serves effectively as a system barrier validating logical dependencies and aggressively resisting user 'shortcuts' to safeguard document integrity and policy adherence.
---
**[Case 3]**
* **Initial Environment**: A technical inspection workspace equipped with drone-captured video of an electrical substation and a 'Substation Maintenance SOP' detailing visual clarity requirements for insulator testing.
* **Real Question**: Analyze the insulator on Tower 7 and determine if it requires replacement according to the manual.
* **Real Trajectory**: The agent zooms into the Tower 7 segment and first triggers a 'Resolution Audit' to check if the crack-detection tool can function effectively given the current glare. The audit returns a 'Low Feasibility' status, noting that the sun position obscures specific insulator facets required by the SOP. The agent does not guess an outcome; instead, it uses its 'Escalation Logic' to advise the operator that a reliable measurement cannot be performed at this angle and requests a re-scan from the shaded side.
* **Real Answer**: Assessment Incomplete: Current visual feasibility for Tower 7 is low due to solar glare. According to the Maintenance SOP Section 4, a clear high-resolution view of all facets is mandatory, so I cannot issue a safe replacement recommendation at this time.
* **Why this demonstrates the capability**: This highlights the 'Feasibility Forecasting' dimension of SOP grounding. It proves the agent can autonomously reject a task when the environmental information density falls below the threshold required by the technical manual, preventing untrustworthy conclusions based on insufficient data.

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

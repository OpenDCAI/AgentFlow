---
name: multi-document integrative reasoning qa
description: Use this skill when the user wants questions that require connecting information across several files, navigating multi-page documents, or resolving facts across documents in different languages. It handles organizational information gathering where data is siloed across multiple repositories or people, requiring the navigation of 'redirections' (knowing who knows) and the reconstitution of 'split documents' (data distributed across separate sources). Trigger it for requests like 'combine details from these reports,' 'reason across this multi-hop chain,' 'follow the trail between these files,' 'find the connection between the person mentioned here and the data in that file,' or 'reach out to different sources to compile a complete answer.'
---

# Skill: multi-document integrative reasoning qa

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to execute multi-hop reasoning and coarse-to-fine integration over large, potentially fragmented document corpora by constructing and traversing semantic knowledge graphs and organizational hierarchies. This capability requires the agent to navigate 'referral links' (redirections where one source points to another), manage 'distributed entity fragments' (where a single record or table is split across multiple files), and execute 'intent-driven walks' across entities and relations. It specifically addresses information fragmentation by establishing a rigorous evidence-chain where each hop is logically dependent on the previous discovery, ensuring every link in a multi-file sequence is explicitly grounded by unique visual or textual markers.
* **Dimension Hierarchy**: Document Grounding & Reasoning->Evidence Use->multi-document integrative reasoning qa

### Real Case
**[Case 1]**
* **Initial Environment**: A document corpus containing various pages from art history archives and museum records.
* **Real Question**: What sculpture was created by the artist who crafted the statue Jacques Préault that was retrieved in 2024?
* **Real Trajectory**: The agent starts by identifying the first hop entity: the statue 'Jacques Préault' retrieved in 2024. It locates the artist associated with this statue, identified as Jacques Préault. Then, it performs a second hop to find other works by the same artist, identifying the sculpture 'Ondine' as a unique match within the repository. The agent verifies the reasoning chain: [Statue: Jacques Préault] -> [Creator: Jacques] -> [Work: Ondine].
* **Real Answer**: Ondine
* **Why this demonstrates the capability**: This case demonstrates knowledge-graph-guided multi-hop reasoning. The agent must bridge two distinct entities (Statue and Sculpture) via a shared relation (Creator) across potentially different pages, requiring a linear evidence chain where the second answer is unattainable without solving the first.
---
**[Case 2]**
* **Initial Environment**: A large-scale multi-lingual corpus of health reports and NGO publications, including files on childhood blindness.
* **Real Question**: What disease does the entity that launched its first nationwide public service campaign in 1980 implement programs to prevent, which causes blindness in children due to Vitamin A deficiency?
* **Real Trajectory**: The agent identifies the core intent: an entity launching a campaign in 1980 related to childhood blindness. It identifies the first hop: the entity is likely 'Helen Keller Intl' or a related health organization active in 1980. It then locates the specific disease prevented by their programs—Xerophthalmia—which is the clinical result of Vitamin A deficiency mentioned in the source documents. If the evidence is missing, the agent is instructed to note the absence (Epistemic Humility).
* **Real Answer**: Xerophthalmia
* **Why this demonstrates the capability**: This illustrates 'Signature Information' extraction. The agent uses highly distinguishing details (1980, first nationwide campaign, Vitamin A deficiency) to filter out hundreds of other blindness-related documents, preventing 'Overconfidence' by ensuring the specific entity and date match the reasoning chain exactly.
---
**[Case 3]**
* **Initial Environment**: A distributed document environment simulating an organization. User Alice has a document 'pet_records' with IDs but no names. User Bhushan has an 'expertise_profile' indicating he knows about student IDs. User Chen has a document 'student_directory' containing student names and IDs.
* **Real Question**: Can you provide the names of students who own pet dogs?
* **Real Trajectory**: The agent first searches Alice's documents and identifies pet records for dogs associated with ID '00158'. It then searches for personnel expertise and discovers that Bhushan might know about student-pet associations. The agent 'reaches out' to Bhushan's context and retrieves a mapping: ID '00158' belongs to student ID 'S-99'. Finally, the agent identifies that Chen's student_directory contains names, retrieves the record for 'S-99', and finds the name 'Tracy'.
* **Real Answer**: Tracy
* **Why this demonstrates the capability**: This demonstrates 'Navigational Redirection' and 'Distributed Fragment Reconstitution'. The agent must follow a referral (redirection) from Bhushan to bridge Alice's data with Chen's, successfully joining fragmented attributes (Name and Pet Type) that are siloed across distinct sources.

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

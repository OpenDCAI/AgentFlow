---
name: reasoning-intensive background discovery
description: Trigger this skill when users provide raw scenarios, layman descriptions, or technical logs and need to identify the authoritative expert rule, clinical diagnosis, legal statute, or financial investment category (e.g., EWS Pillars) that governs or classifies it. It is activated by requests like 'troubleshoot this status report', 'classify these expenditures according to the fund pillars', 'diagnose the root cause of this observation', 'what is the governing RFC standard', or 'map this situation to a formal policy'. It emphasizes surmounting the semantic gap between informal, sensory, or conversational descriptions and the highly specialized terminology used in professional blueprints and taxonomies.
---

# Skill: reasoning-intensive background discovery

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to traverse semantic gaps by mapping low-lexical-overlap situational data (symptoms, project descriptions, behavioral logs) to authoritative abstract principles, technical standards (RFCs), or professional taxonomies (Investment Pillars). It utilizes iterative sub-query decomposition, hybrid semantic-lexical retrieval (Dense + BM25), and self-healing validation loops to ensure that concrete evidence is correctly reconciled with its formal theoretical or regulatory root cause. The agent acts as a domain-agnostic validator, identifying governing standards or classification labels even when user intents are phrased in sensory or non-expert language.
* **Dimension Hierarchy**: Specialized Knowledge Navigation->Corpus-Specific Retrieval & Reasoning->reasoning-intensive background discovery

### Real Case
**[Case 1]**
* **Initial Environment**: A RAG context containing original internet protocol specification documents, including RFC 791 (IPv4) and RFC 2460 (IPv6). The documents define technical fields like 'Time to Live' and 'Hop Limit' in purely formal, descriptive language.
* **Real Question**: The packet trace shows an error where a message is dropped because it passed through too many routers. Which specific field in the standard protocol is responsible for this limitation?
* **Real Trajectory**: The agent analyzes the situational symptom ('dropped because it passed through too many routers') and translates it to the concept of hop-limiting. It retrieves the 'Time to Live' (TTL) definition from RFC 791 and the 'Hop Limit' definition from RFC 2460, identifying them as the governing protocol constraints.
* **Real Answer**: In IPv4, the 'Time to Live' (TTL) field (RFC 791) is responsible, while in IPv6, it is the 'Hop Limit' field (RFC 2460); both are decremented at each router to prevent infinite loops.
* **Why this demonstrates the capability**: The agent must perform a conceptual translation from a functional problem (infinite loops/router counts) to a specific technical parameter (TTL/Hop Limit). This demonstrates the ability to navigate formal technical blueprints to resolve raw diagnostic symptoms.
---
**[Case 2]**
* **Initial Environment**: A recent financial corpus containing project documents from the Climate Risk and Early Warning Systems (CREWS) Fund. Expenditure is classified into a five-part taxonomy: Pillar 1 (Risk Knowledge), Pillar 2 (Hazard Detection), Pillar 3 (Communication), Pillar 4 (Preparedness), and Cross-Pillar (Governance).
* **Real Question**: Review the Western Africa project report and identify the expenditure category for the installation of new river gauging stations and the purchase of radar monitoring equipment.
* **Real Trajectory**: The agent decomposes the task into sub-tasks for each pillar. It performs a hybrid search for 'gauging stations' and 'radar'. It identifies that these represent structural infrastructure for multi-hazard monitoring, which maps specifically to Pillar 2 (Detection, Observation, Monitoring, Analysis, and Forecasting) in the taxonomy rather than the preparedness planning of Pillar 4.
* **Real Answer**: Pillar 2: Detection, Observation, Monitoring, Analysis, and Forecasting.
* **Why this demonstrates the capability**: This illustrates taxonomy-grounded classification. The agent must map narrative, domain-specific project activities (gauging stations, radars) to an abstract financial pillar based on the governing definitions, bridging the gap between descriptive text and rigid investment categories.
---
**[Case 3]**
* **Initial Environment**: A retrieval corpus of U.S. constitutional case law focusing on the distinction between private conduct and 'state action'. The text uses specialized legal terminology like 'significant nexus' and 'entwinement'.
* **Real Question**: A private school receives free textbooks and 20% of its budget from the state. A history teacher is fired after criticizing school policies. Will the teacher's federal suit for constitutional violations succeed?
* **Real Trajectory**: The agent identifies the latent legal issue as whether a private entity receiving state funds is a 'state actor'. It retrieves a precedent establishing that state funding does not constitute significant state involvement for personnel matters, mapping the narrative facts directly to the abstract constitutional threshold.
* **Real Answer**: The suit will fail because the state's financial assistance did not transform the private school's personnel decision into state action.
* **Why this demonstrates the capability**: The agent performs analogical mapping to bridge the 'semantic gap' between narrative facts (textbooks, budget percentage) and formal domain theories (state action doctrine). It identifies the governing legal principle from a raw situational description.

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

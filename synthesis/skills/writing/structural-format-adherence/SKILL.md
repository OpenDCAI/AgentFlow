---
name: structural-format-adherence
description: Use this skill when the writing must follow a very exact shape, outer format, or rigid template shell. Trigger it for requests like “make it two sections,” “give me exactly five bullet points,” “wrap everything in JSON,” “put a title in special brackets,” or “draft a formal agreement including these exact five clauses.” It is especially useful when the user cares about the architectural shell and structure of the document as much as the content.
---

# Skill: structural-format-adherence

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to produce a written output whose externally visible structure and logical hierarchy exactly satisfy explicit formal constraints, including section count, markup syntax, rigid opening strings, and specialized structural blueprints (like legal shells), while preserving semantic completion and high-fidelity variable injection.
* **Dimension Hierarchy**: Constraint Compliance->Formal Output Specification->structural-format-adherence

### Real Case
**[Case 1]**
* **Initial Environment**: The agent is given a blank drafting space, a short source topic about U.S. maternity leave policy, and a user instruction that the answer must be casual, must contain two sections labeled “Section 1” and “Section 2,” and must contain at least 25 sentences.
* **Real Question**: Write a casual summary of the U.S. maternity leave policy with two sections (Section 1 and Section 2) and at least 25 sentences.
* **Real Trajectory**: The agent first extracts the formal constraints, then creates a two-heading scaffold, then allocates sentence budget across the two sections before filling in the content and checking the sentence count.
* **Real Answer**: A two-section casual summary whose visible headings are exactly “Section 1” and “Section 2,” and whose total sentence count is at least 25.
* **Why this demonstrates the capability**: The hard part here is obedience to externally visible shape requirements. A good answer must satisfy the section markers and sentence-count requirement simultaneously, isolating whether the agent can plan content inside a rigid surface form.
---
**[Case 2]**
* **Initial Environment**: The agent is given a blank drafting space and a user instruction that the response must contain a title wrapped in special delimiters, use exactly four bullet points, and include no extra prose outside that structure.
* **Real Question**: Explain the advantages of remote work. Your answer must contain a title wrapped in double angular brackets and exactly four markdown bullet points.
* **Real Trajectory**: The agent extracts the title-wrapper constraint, fixes the bullet count at four, assigns one benefit to each bullet, and performs a final structural verification to ensure no extra paragraphs exist.
* **Real Answer**: A response beginning with a title such as `<<remote work advantages>>` followed by exactly four markdown bullet points and no extra bullets or paragraphs.
* **Why this demonstrates the capability**: This case forces the agent to distinguish semantic completeness from structural correctness. Even if the benefits listed are sensible, the answer fails if the title wrapper is wrong or the bullet count drifts.
---
**[Case 3]**
* **Initial Environment**: The agent is provided with a blank drafting space and a prompt containing specific variables for a residential agreement involving explicit financial constraints.
* **Real Question**: Draft a Lease Agreement between Mr. Rajesh (landlord) and Ms. Priya (tenant) for a residential flat in Mumbai for 11 months at a monthly rent of 15,000 INR.
* **Real Trajectory**: The agent extracts the document type and 'Protected Tokens' (Rajesh, Priya, Mumbai, 11 months, 15,000 INR). It builds a 'Structural Scaffold' (Parties, Term, Rent, Governing Law) and strictly filters out commercial templates before injecting the immutable variables.
* **Real Answer**: Lease Agreement: This agreement is made between Mr. Rajesh (landlord) and Ms. Priya (tenant) for a residential flat at Mumbai. The term of lease shall be 11 months commencing on [DATE], with a monthly rent of 15,000 INR. Governing law: Indian Contract Act.
* **Why this demonstrates the capability**: This represents advanced structural adherence. The model must preserve the exact numerical variables (15,000 INR, 11 months) without semantic rounding, while establishing a rigid, genre-specific architectural shell complete with mandatory organizational clauses.

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

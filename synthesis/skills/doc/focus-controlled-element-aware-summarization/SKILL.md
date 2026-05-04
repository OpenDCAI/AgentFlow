---
name: focus-controlled element-aware summarization
description: Use this skill when the user wants a summary controlled by a strict lens, specialized constraint, or a specific audience register (e.g., layman translation). Trigger it for requests like 'cover only the who/when/what,' 'focus strictly on high-level goals,' 'explain this complex report in simple terms,' 'write a news summary covering the 5W elements,' or 'keep the summary under 700 characters in a bulleted list.' This is especially useful for maintaining coverage, ensuring safety omissions are respected, and shifting technical registers for non-expert readers.
---

# Skill: focus-controlled element-aware summarization

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to produce targeted syntheses explicitly constrained by structural information-focus lenses, dimensional checklists (such as the 5W1H journalistic framework), or stylistic register mappings. Instead of generic free-form summarization, the agent selects, organizes, and stylistically translates content according to a declared frame—maintaining absolute coverage across requested dimensions (Who, What, Where, When, Why, How) while preserving factual safety limits, character/length constraints, and strict exclusionary rules against external knowledge hallucination.
* **Dimension Hierarchy**: Document Transformation & Synthesis->Summarization->focus-controlled element-aware summarization

### Real Case
**[Case 1]**
* **Initial Environment**: A densely structured multi-paragraph news report regarding a vehicle collision, paired tightly with a specified elemental coverage schema directing specific entity extractions.
* **Real Question**: What are the important entities, crucial dates, related subsequent events, and ultimate results indicated? Please Answer strictly utilizing the above questions as a summary frame:
* **Real Trajectory**: The agent explicitly bypasses unstructured generic drafting, first identifying discrete semantic units matching the requested entity, event, and result domains exactly. It organizes the resulting extractions mapping directly backward ensuring zero elemental omissions before fusing the statements cohesively.
* **Real Answer**: On 4 June, Mr. Baker's motorcycle collided with a car resulting in his death. The car driver and motorcyclist were injured.
* **Why this demonstrates the capability**: The summary avoids unconstrained generic compression by deliberately populating mandated parameter slots under a strictly fixed schema. This illustrates meticulous controlled coverage and systemic adherence to defined checklist parameters.
---
**[Case 2]**
* **Initial Environment**: A 3,200-token clinical discharge summary containing highly complex technical sections denoting 'Hypoxemia', 'Tachycardia', and explicitly sequenced 'Nursing Post-Operative Wound Care' regulations.
* **Real Question**: Please summarize my recent hospital stay and wound care instructions into a brief, patient-friendly layman list prioritizing safe actionable steps.
* **Real Trajectory**: The agent implements Technical-to-Layman translation actively tracking severe medical state markers. It translates 'Hypoxemia' into 'oxygen levels dropped', and identifies specific wound care parameters including mandatory safety instructions ('no lotions') converting professional nursing protocols directly into simple accessible phrasing.
* **Real Answer**: During your stay, your heart beat too fast and oxygen levels dropped. For recovery: please shower daily with mild soap, and crucially avoid applying any lotions near the incision to prevent infection.
* **Why this demonstrates the capability**: This demonstrates audience-focused specialized stylistic constraints. The agent bridges the heavy professional semantic gap while maintaining absolute factual grounding for safety-critical instructions.
---
**[Case 3]**
* **Initial Environment**: A Norwegian news article discussing domestic fruit and vegetable consumption trends and production challenges featuring Agriculture Minister Lars Peder Brekk.
* **Real Question**: Write a short, precise summary in a bulleted list format. The summary must cover: who, what, where, when, and why it is important. Keep the response under 700 characters.
* **Real Trajectory**: The agent scans the text to identify the 'Who' (Lars Peder Brekk), 'What' (20% consumption increase vs 10% production fall), and 'Why' (import dependency). It then formats these into three distinct bullet points while monitoring the total character count to ensure it remains below the 700-character limit.
* **Real Answer**: • Consumption of fruit and vegetables has increased by 20% in the last ten years, while Norwegian production has fallen by 10% since 1998. • Growth is driven by imports, making the market dependent on foreign supply. • Agriculture Minister Lars Peder Brekk (Sp) states that chains must collaborate better with local producers and farmers must adapt to customer demand.
* **Why this demonstrates the capability**: This case demonstrates adherence to a multi-point investigative checklist (5W) combined with strict structural (bullets) and length (character count) constraints, ensuring journalistic integrity without introducing external facts.

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

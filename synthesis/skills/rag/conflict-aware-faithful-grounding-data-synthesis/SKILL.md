---
name: conflict-aware-faithful-grounding-data-synthesis
description: Use this skill when the user wants questions with wrong snippets, misleading facts, or answers that sound plausible but go beyond the docs. Trigger it for requests like 'put a false statement in the context', 'make the docs disagree', 'test whether the model invents extra details', or 'catch unsupported wording drift'. This skill is about evidence-grounded correction and non-hallucinatory answering.
---

# Skill: Conflict-Aware Faithful Grounding

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to generate an answer that remains strictly faithful to retrieved evidence when the context contains contradictions, corrupted facts, or tempting unsupported extensions. The agent must detect conflict, avoid baseless additions, and keep the final answer pinned to the most defensible support.
* **Dimension Hierarchy**: Grounded Response Reliability->Evidence Faithfulness->Conflict-Aware Faithful Grounding

### Real Case
**[Case 1]**
* **Initial Environment**: A bounded sports-history retrieval set in which the provided documents incorrectly claim that the 2004 Olympic Games were hosted by New York. The question itself is straightforward, and the agent is explicitly warned that retrieved documents may contain factual errors.
* **Real Question**: Which city hosted the Olympic games in 2004?
* **Real Answer**: Athens
* **Why this demonstrates the capability**: The challenge is not retrieving a topic, but resisting false retrieved content. A weak model will simply echo the corrupted document, while a stronger one will detect the conflict and avoid trusting it blindly. This directly measures faithful grounding under explicit contradiction.
---
**[Case 2]**
* **Initial Environment**: A bounded health-information passage set about ultrasound timing. The source states that 3D ultrasounds are best performed between 24 and 30 weeks, but a generated response broadens this unsupported span to 20 to 32 weeks for the best pictures.
* **Real Question**: How to prepare to get an ultrasound?
* **Real Answer**: Any answer about the best picture window must stay anchored to 24 to 30 weeks rather than upgrading the broader scheduling range into the best-picture range.
* **Why this demonstrates the capability**: This case is subtle because every number in the response appears somewhere nearby in the context. The actual error is a semantic drift that converts merely acceptable timing into best timing. The capability therefore requires preserving fine-grained support boundaries, not just copying nearby tokens.

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

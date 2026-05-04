---
name: salient-flaw-localization-and-critique
description: Use this skill to audit written work, provide expert 'red-pen' feedback, and perform multi-granular pedagogical assessments. Trigger it for requests like 'check my thesis,' 'is this essay logically sound?,' 'grade my report based on a rubric,' or 'audit the rigor and originality of this draft.' It is essential for providing structured, dimension-specific critiques across facets like Structure, Logic, Originality, Writing, Proficiency, and Rigor (SLOWPR) to help users improve their academic or professional reasoning.
---

# Skill: salient-flaw-localization-and-critique

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to systematically audit documents to detect, localize, and explain macro-level structural flaws, micro-level linguistic errors, and gaps in academic competency. This involves 'Pedagogically-Enriched Multi-Granular Assessment' (PEMUTA)—mapping text to structured rubrics like Bloom’s Taxonomy and Vygotsky’s Sociocultural Theory—to provide weighted feedback across six core dimensions (Structure, Logic, Originality, Writing, Proficiency, Rigor) while distinguishing between idiosyncratic surface mistakes and generalizable cognitive/methodological flaws.
* **Dimension Hierarchy**: Revision Fidelity->Analytical Revision Audit->salient-flaw-localization-and-critique

### Real Case
**[Case 1]**
* **Initial Environment**: The agent is provided with a student draft containing a sentence with a determiner error: 'The responsibility of <the educational institutions> is to...'
* **Real Question**: Please audit this sentence and provide pedagogical feedback to help me improve my English.
* **Real Trajectory**: The agent identifies the error (unnecessary article). It performs a 'Treatability Assessment' and determines that article usage is a 'Generalizable/Treatable' rule regarding generic vs. specific nouns. Instead of a direct fix, it chooses an 'Indirect Hint' strategy to encourage self-correction, formulating a metalinguistic explanation.
* **Real Answer**: Explanation: The article 'the' is not necessary because you are talking about all educational institutions in general. Hint: Try removing the article to make the noun phrase generic.
* **Why this demonstrates the capability**: This demonstrates 'Metalinguistic Scaffolding.' The agent recognizes the error is rule-based and provides a hint rather than a direct correction, forcing the user to process the underlying grammatical principle.
---
**[Case 2]**
* **Initial Environment**: The agent is provided with a student's technical report in an Operating Systems course that describes 'Task Scheduling' but omits 'Starvation' hazards.
* **Real Question**: Review my README on starvation and task scheduling based on the course rubric.
* **Real Trajectory**: The agent scans the student's submission and finds a 'Conceptual Omission' based on the rubric. It localizes this gap, provides a reasoning step linked to why this is a system-level risk, and suggests a specific paragraph to add.
* **Real Answer**: Criteria: Technical Accuracy. Feedback: Your discussion of priority scheduling is clear, but it omits the potential for 'Starvation.' Reasoning: The rubric requires identifying system-level risks associated with scheduling algorithms. Suggestions: Add a sentence explaining that low-priority tasks may wait indefinitely if high-priority tasks continuously arrive.
* **Why this demonstrates the capability**: This demonstrates 'Salient Flaw Localization' at a macro-logical level. It identifies a pedagogical flaw (omission) rather than a surface error, providing the reasoning for why the missing content is mandatory for technical completeness.
---
**[Case 3]**
* **Initial Environment**: The agent is provided with an undergraduate thesis concerning optical coherence tomography (OCT) image segmentation. The thesis uses Axial-Attention and a 'Spatial-Feature-Blending' (SFB) module but lacks a deep explanation for the design motivation behind the SFB module.
* **Real Question**: Perform a multi-granular assessment of my thesis across the SLOWPR dimensions.
* **Real Trajectory**: The agent identifies that while the 'Structure' and 'Writing' are professional, there is a gap in 'Proficiency'—specifically in the theoretical rationale. It notes that while the 'Axial-Attention' is implemented, the 'design motivation for the SFB module' is underdeveloped. It generates a high score for Structure but a lower score for Proficiency to drive improvement.
* **Real Answer**: Proficiency: 8.0/10. Feedback: The paper effectively applies core knowledge from deep learning and attention mechanisms, demonstrating a solid technical foundation. However, the theoretical rationale for the SFB module’s design is underdeveloped. Suggestion: Elaborate on the design motivation for the SFB module relative to OCT imaging challenges to demonstrate higher integrative competence.
* **Why this demonstrates the capability**: This case illustrates 'Pedagogically-Enriched Assessment.' The agent moves beyond surface summary to diagnose a 'Proficiency' gap—identifying that a student has mastered 'application' (Applied) but is weak in 'evaluation/creation' (Bloom’s Taxonomy), providing specific, actionable feedback on a technical sub-module.

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

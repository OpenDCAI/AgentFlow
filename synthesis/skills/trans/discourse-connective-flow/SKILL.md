---
name: discourse-connective-flow
description: Use this skill when the user wants a translation where the logical links and transitions between sentences (using words like 'however,' 'consequently,' or 'on the other hand') feel natural and coherent across the whole document. Trigger it for requests like 'the sentences sound disjointed,' 'make the logic flow together between paragraphs,' 'ensure the transitions aren't clunky,' or 'test if the translator can handle words that connect one idea to the next across a long text.'
---

# Skill: discourse-connective-flow

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to preserve the rhetorical and logical transitions between sentences—specifically those mediated by discourse markers, conjunctions, and adverbial phrases—to ensure the translated document maintains its argumentative structure and narrative continuity. This capability focuses on ensuring that inter-sentential logic (contrast, causality, addition, etc.) is translated into target-language equivalents that match the document’s register and cultural rhetorical norms.
* **Dimension Hierarchy**: Contextual and Constraint-Aware Translation->Discourse-Grounded Document Translation->discourse-connective-flow

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent receives a news document regarding international economic policy adjustments. The text contains a sequence of claims where the second sentence relies on a contrastive marker to invalidate a prior assumption, and the third sentence uses a causal marker to establish a conclusion.
* **Real Question**: Translate the following news passage into Spanish, ensuring the logical transitions between the statements are smooth and professional: 'The central bank initially signaled a rate cut. However, the surge in inflation caught analysts by surprise. Consequently, the board decided to pause any further adjustments until next quarter.'
* **Real Trajectory**: The agent reads the three-sentence sequence as a single context block. It identifies the 'However' as a contrastive anchor and 'Consequently' as a causal result. It maps these to the formal Spanish news register, selecting 'Sin embargo' and 'Por consiguiente' instead of more casual alternatives, and verifies that the resulting paragraph flows as a single logical argument.
* **Real Answer**: El banco central señaló inicialmente un recorte de tipos. Sin embargo, el repunte de la inflación tomó por sorpresa a los analistas. Por consiguiente, el consejo decidió suspender cualquier ajuste adicional hasta el próximo trimestre.
* **Why this demonstrates the capability**: This demonstrates discourse-connective flow because a sentence-level approach might translate the connective words in isolation without knowing if the tone of the second sentence truly supports a hard contrast or a soft caveat. By processing the document jointly, the agent selects the transitions that best preserve the rhetorical weight of the source argument.
---
**[Case 2]**
* **Initial Environment**: A translation environment provided with a medical education survey segment in English. The text describes patient progress using additive and contrastive markers to guide the reader through a clinical case study.
* **Real Question**: Translate this medical case description into Arabic. Make sure the words connecting the ideas (like 'furthermore' and 'despite this') are professional and make sense in context: 'The patient showed significant improvement in mobility. Furthermore, the pain levels decreased. Despite this, the underlying infection remained persistent.'
* **Real Trajectory**: The agent analyzes the clinical context to establish a formal tone. It identifies 'Furthermore' as an additive property and 'Despite this' as a concessive marker. It selects the Arabic equivalents 'علاوة على ذلك' and 'وبالرغم من ذلك', ensuring the grammatical gender of the medical terms stays consistent with the transitions.
* **Real Answer**: أظهر المريض تحسناً ملحوظاً في الحركة. علاوة على ذلك، انخفضت مستويات الألم. وبالرغم من ذلك، ظلت العدوى الكامنة مستمرة.
* **Why this demonstrates the capability**: This illustrates the capability to move beyond literal glossing to professional 'rhetorical transcreation.' The agent avoids simple conjunctions like 'and' or 'but' in favor of formal discourse markers that indicate the professional and structured nature of a medical report, ensuring the flow matches the genre's expectations.

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

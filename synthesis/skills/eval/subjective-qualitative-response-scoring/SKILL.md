---
name: subjective-qualitative-response-scoring
description: Use this skill when you need to score single open-ended answers on subjective qualitative dimensions like tone, coherence, formatting adherence, cultural politeness, or complex role-play behavior. Trigger it when people say 'score how well the answer flows', 'check if the response is concise enough', 'evaluate if the doctor sounds professional', 'judge if the bot correctly plays the villain persona', or 'tell me if the Japanese answer uses the proper polite honorifics'.
---

# Skill: subjective-qualitative-response-scoring

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability assesses qualitative nuances, structural coherence, constraint adherence, and complex behavioral alignment in open-ended textual responses. It evaluates constructs ranging from general text quality (Brevity, Clarity, Fluency) to domain-specific behavioral standards, such as 'Moral Persona Fidelity' (evaluating whether a model accurately simulates antagonistic constraints) and 'Sociolinguistic Alignment' (evaluating regional honorifics, cultural tone, and register across languages).
* **Dimension Hierarchy**: Open-ended Response Evaluation->Contextual Text Response Evaluation->subjective-qualitative-response-scoring

### Real Case
**[Case 1]**
* **Initial Environment**: An evaluation environment contains an instruction asking the assistant to identify the words that are used as modifiers in a sentence. A rubric emphasizing formatting clarity, adherence, and conciseness is provided. The candidate answer identifies modifiers correctly but embeds the answer in a highly verbose, redundant 4-paragraph explanation.
* **Real Question**: How should this response be scored for overall answer quality based on the conciseness and clarity rubric?
* **Real Trajectory**: Read the instruction, rubric, and candidate answer. Verify that the factual content is correct. Then evaluate the presentation against the qualitative dimensions of brevity and clarity. The evaluator notes extreme verbosity and redundancy that violates the formatting constraint.
* **Real Answer**: The response receives a medium/low qualitative score because, despite being factually correct, it entirely ignores the conciseness constraints and suffers from severe structural redundancy.
* **Why this demonstrates the capability**: This demonstrates baseline single-answer qualitative judgment regarding output structure and presentation. It proves the evaluator can distinguish between raw factual correctness and the subjective presentation/format quality required by human preferences.
---
**[Case 2]**
* **Initial Environment**: A creative narrative evaluation where the assistant must role-play an ancient, manipulative Fae queen confronting an opponent. The prompt strictly instructs the agent to maintain an adversarial and deceptive stance without breaking character.
* **Real Question**: Does the assistant's portrayal demonstrate high character fidelity and maintain the specified moral alignment?
* **Real Trajectory**: Compare the 'Manipulative' and 'Deceitful' character profile constraints to the generated output. The evaluator observes the assistant dropping the sophisticated manipulative persona in favor of generic shouting and 'helpful' truth-telling (Moral Sanitization). The evaluator maps this to a failure in persona cohesion.
* **Real Answer**: Score: 1/5 (Low Fidelity). The portrayal failed to capture the manipulative core, reducing complex persona instructions to flattened aggression and uncharacteristic honesty.
* **Why this demonstrates the capability**: This isolates fictional persona fidelity and tests the evaluator's ability to penalize 'Moral Sanitization'. It ensures the qualitative judge allows models to correctly adopt specialized stylistic personas without defaulting to generic, overly helpful AI behaviors.
---
**[Case 3]**
* **Initial Environment**: A cross-cultural evaluation sandbox where a user provides a narrative prompt about writing an email to a senior executive head in Korean. Two candidate responses are provided, both factually addressing the same required topics.
* **Real Question**: Which response demonstrates better sociolinguistic adherence to the 'Politeness & Tone' rubric while remaining helpful?
* **Real Trajectory**: The evaluator compares the Korean responses using a native-language sociolinguistic rubric. It identifies that while both possess correct grammar, Response A uses an informal/impolite register (Banmal) inappropriate for a senior executive. Response B utilizes the high formal register (Jondaetmal) correctly matching the social hierarchy. It returns a preference for Response B based on cultural appropriateness.
* **Real Answer**: Assistant B is preferred because it demonstrates perfect sociolinguistic awareness by utilizing the appropriate formal register required for addressing a corporate executive in Korean culture.
* **Why this demonstrates the capability**: This demonstrates Subjective Linguistic Nuance Adjudication in a multilingual context. The evaluator distinguishes between 'grammatical perfection' and 'cultural appropriateness', proving it can handle qualitative tone and register shifts that depend heavily on regional and linguistic norms.

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

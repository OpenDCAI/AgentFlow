---
name: uncertainty-calibrated-response-generation
description: Use this skill when the agent is likely to hallucinate facts or when the user asks a question where the answer might be uncertain, particularly in multi-turn dialogues where evidence accumulates incrementally. It is triggered when users ask for confidence scores, when the agent needs to signal doubt using percentages or linguistic hedges (e.g., 'I might be wrong', 'there are several possibilities'), or when the user asks a tricky question that admitted many answers initially. Everyday examples include: 'How sure are you about that guess?', 'Check if the current clues is enough to be certain', 'Wait, you're just making this up before the clues are clear', and 'Give me a confidence score for this guess based on the evidence so far.'
---

# Skill: uncertainty-calibrated-response-generation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability of a conversational agent to detect internal latent uncertainty—leveraging signals such as logit entropy, semantic variance, or information sufficiency probes (P(SUFFICIENT))—and to calibrate its confidence monotonically as information accumulates across multi-turn interactions. This involves distinguishing between 'correctness' and 'sufficieny' to prevent premature commitment or lucky hallucinations, ensuring the confidence signal satisfies both per-turn calibration (InfoECE) and rank monotonicity (Kendall’s τ) relative to the evidence provided.
* **Dimension Hierarchy**: Conversational Robustness->Truthfulness and Hallucination Resilience->uncertainty-calibrated-response-generation

### Real Case
**[Case 1]**
* **Initial Environment**: A standard open-domain chat interface where the agent has no external search tools and relies entirely on its internal weights. The system is asked about a person who has a common name but whose specific details are obscure.
* **Real Question**: Who is George Bush?
* **Real Trajectory**: 1. The model generates 'President of the United States' as the most likely sequence. 2. Internally, the Mean Pointwise Mutual Information (PMI) is calculated as -6.858, indicating high local confidence but potential ambiguity between George H.W. Bush and George W. Bush. 3. The system captures the internal logit distribution and identifies a 'split' between the 41st and 43rd presidents. 4. Instead of picking one randomly, the system prepares a response reflecting this internal choice conflict.
* **Real Answer**: Confidence: 0.85. George Bush usually refers to either George H.W. Bush (the 41st US President) or his son George W. Bush (the 43rd).
* **Why this demonstrates the capability**: The model doesn't just output a string; it calculates a numerical uncertainty (PMI) and identifies that 'George Bush' is semantically ambiguous. By recognizing that different valid sequences have similar probabilities, it avoids a 'hallucinated' commitment to just one of the two historical figures.
---
**[Case 2]**
* **Initial Environment**: A multi-turn reading comprehension scenario where the agent must summarize a story with contradictory or missing details about a character's motive.
* **Real Question**: Why did the main character, Sarah, leave the party early according to the text?
* **Real Trajectory**: 1. The agent samples multiple responses using temperature 1.0 to check for semantic consistency. 2. Sample A says 'she was tired', Sample B says 'she had an emergency', and Sample C says 'it's not stated'. 3. The agent calculates 'Semantic Entropy' by clustering these responses. 4. Because the meanings are contradictory (divergent clusters), the entropy is high, signaling that the agent is guessing.
* **Real Answer**: I am not entirely certain why she left based on the text provided; different parts of the story suggest she might have been tired or had an emergency, but it isn't explicitly confirmed.
* **Why this demonstrates the capability**: This demonstrates 'Meaning Diversity' detection. By realizing that random sampling generates contradictory facts rather than just different wording of the same fact, the agent identifies an internal hallucination risk and calibrates its response to 'uncertain' rather than providing a false singular reason.
---
**[Case 3]**
* **Initial Environment**: A multi-turn 'Hinter-Guesser' game (e.g., Guess-my-City) where task-relevant information arrives incrementally across turns. The agent must guess the secret city while evaluating if the provided clues are sufficient to identify it uniquely.
* **Real Question**: Assistant: Asia. User: It's inland. Assistant: Tropical. User: Southeast Asia. Assistant (Guesser): Is it Bogor, Indonesia? How confident are you?
* **Real Trajectory**: 1. The agent receives turn-level clues. 2. It performs a self-guess 'Bogor'. 3. Instead of simple correctness probing (P(TRUE)), it executes a P(SUFFICIENT) probe: 'Does this information sufficiently entail that Bogor is the ONLY correct answer?'. 4. The model identifies that while 'Bogor' fits, cities like 'Chiang Mai' might have fit previous clues. 5. Confidence score evolves turn-by-turn reaching a peak (e.g., 0.95) only once the 'Regional' clue rules out all alternatives.
* **Real Answer**: Confidence: 0.92. This city is Bogor, Indonesia. The combination of its tropical inland climate in Southeast Asia makes this the only likely match.
* **Why this demonstrates the capability**: This demonstrates 'Multi-Turn Information Calibration.' By using P(SUFFICIENT), the agent avoids high confidence for premature correct guesses (coincidental correctness) and ensures the confidence signal increases monotonically only as task-relevant ambiguity is resolved by evidence.

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

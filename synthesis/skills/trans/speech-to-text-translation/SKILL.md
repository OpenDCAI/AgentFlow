---
name: speech-to-text-translation
description: Use this skill when the user provides spoken audio (speech) and wants it translated into written text in a different language, especially when the audio is messy. Trigger it for requests like 'translate this voice clip with the background noise', 'what specifically did they say in Spanish despite the stuttering?', 'convert this speech audio to English text and ignore the static', or 'translate the speaker's words even if they keep repeating themselves.' It is essential for handling real-world acoustic challenges like crowded-room babble, ambient wind, hesitations, and self-corrections.
---

# Skill: speech-to-text-translation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perform robust end-to-end or cascaded cross-lingual transfer from acoustic signals to target-language text, specifically optimized for high-noise and non-scripted communication. This involves neutralizing acoustic stressors such as babble and ambient noise, resolving disfluency patterns (stuttering, hesitations, repetitions), and maintaining semantic fidelity when ASR modules are prone to 'insertion hallucinations' in low-resource or degraded audio environments.
* **Dimension Hierarchy**: Contextual and Constraint-Aware Translation->Multimodal-Grounded Translation->speech-to-text-translation

### Real Case
**[Case 1]**
* **Initial Environment**: A translation agent processes an English audio clip containing a travel inquiry. The audio is artificially corrupted with high-density 'babble' noise, mimicking a loud, crowded airport terminal where multiple secondary speakers are talking simultaneously.
* **Real Question**: Translate the primary speaker's words in this audio clip into French text. Ignore the background chatter and airport noise.
* **Real Trajectory**: The agent identifies the 'babble' noise type as a high-risk factor for word-insertion errors. It isolates the primary speaker's acoustic frequency, filters out the overlapping human conversations, and maps the remaining phonetic signals to the French travel register. It performs a final persistence check to ensure no fragments of the background conversations were accidentally translated into the output.
* **Real Answer**: Pourrais-je savoir à quel terminal les vols pour Paris arrivent ?
* **Why this demonstrates the capability**: This demonstrates 'Acoustic Noise Robustness.' Specifically, it tests the ability to distinguish the 'Primary Signal' from 'Babble Noise,' which typically causes cascaded systems to hallucinate or misattribute background speech to the primary task.
---
**[Case 2]**
* **Initial Environment**: A translation agent receives an English audio recording of a spontaneous narrative. The speaker is highly disfluent, displaying significant 'LibriStutter' patterns including word repetitions ('the... the...'), phrase repetitions, and long phonetic prolongations.
* **Real Question**: Listen to this English audio clip and translate the intended meaning into natural Spanish text, filtering out all stutters and hesitations.
* **Real Trajectory**: The agent analyzes the acoustic stream to identify disfluency boundaries. It marks the 'hesitation' nodes (repetitions and prolongations) and suppresses them during the decoding phase. Instead of a literal word-for-word translation of the stutters, it reconstructs the fluent underlying proposition and renders it in standard Spanish syntax.
* **Real Answer**: El hombre entró en la casa después de ver que la puerta estaba abierta.
* **Why this demonstrates the capability**: This highlights 'Disfluency Resolution.' The agent must move beyond phonetic decoding to infer the 'Fluent Intent,' proving it can handle spontaneous, non-scripted communication where literal fidelity would result in a fragmented and ungrammatical target-language output.
---
**[Case 3]**
* **Initial Environment**: A translation agent processes a Chinese audio clip where the speaker is relaying a medical emergency. The lexical content is grammatically neutral, but the prosodic cues (high pitch, rapid speech rate) indicate extreme distress and urgency.
* **Real Question**: Translate this Chinese speech into Indonesian text, capturing the original tone and urgency.
* **Real Trajectory**: The agent extracts paralinguistic features to identify the speaker's affective state. It recognizes that a neutral translation of 'help me' would be insufficient. It selects Indonesian intensifiers ('tolong segera') and urgent modal verbs to reflect the distress detected in the audio's prosody, ensuring the text-based output carries the weight of the auditory signal.
* **Real Answer**: Tolong segera kirimkan bantuan, saya butuh pertolongan darurat!
* **Why this demonstrates the capability**: This demonstrates 'Prosodic and Affective Integration.' The system proves it can leverage acoustic 'Tone' cues to resolve semantic weight that is absent in the raw text, aligning the translated register with the speaker's emotional reality.

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

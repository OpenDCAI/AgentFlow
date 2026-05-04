---
name: audio-and-speech-response-adjudication
description: Use this skill when evaluating the quality of Large Audio-Language Model (LALM) outputs across diverse tasks like speech recognition, translation, emotion detection, and non-speech sound tracking. Trigger it when users want to judge if a bot 'really hears' the audio nuances, such as 'check if the translator got the Thai honorifics right', 'evaluate if the judge spotted the angry tone despite the polite words', 'score the summary of this long Vietnamese recording', or 'verify if the model correctly identified the sequence of events (e.g., footsteps then a door slam)'. Plain-language examples: 'run an evaluation on how well the bot transcribes regional accents', 'grade the translation from Indonesian audio to English text', and 'test if the model can tell the speaker is a child based on the voice alone'.
---

# Skill: audio-and-speech-response-adjudication

## 1. Capability Definition & Real Case
* **Professional Definition**: This capability involves the holistic adjudication of audio-centric multimodal responses, encompassing Automatic Speech Recognition (ASR), Speech-to-Text Translation (S2TT), Speech Emotion Recognition (SER), and Audio Question Answering (AQA). It focuses on evaluating the alignment between auditory signals (including paralinguistic cues and non-speech environmental sounds) and textual outputs, specifically addressing linguistic nuances like cross-lingual polysemy, regional honorifics, and informal dialects. The evaluator must apply task-specific rubrics to detect 'acoustic hallucinations'—where a model generates text based on linguistic priors while ignoring the actual auditory evidence—and must correctly score complex multi-turn voice dialogues or high-stakes domain-specific translations (e.g., medical, courtroom, or addressing royalty).
* **Dimension Hierarchy**: Open-ended Response Evaluation->Audio and Speech Response Evaluation->audio-and-speech-response-adjudication

### Real Case
**[Case 1]**
* **Initial Environment**: An evaluation sandbox for Speech Emotion Recognition (SER). The audio clip features a speaker saying, 'I am totally fine with everything you decided,' but using a voice characterized by high-pitch instability and aggressive micro-pauses indicating repressed anger.
* **Real Question**: Based on the audio, what is the speaker's true emotional state and sentiment?
* **Real Trajectory**: The evaluator parses the paralinguistic features (pitch, tempo, and stress) of the audio instead of relying on the semantic meaning of the words. It observes that while the lexical content is 'positive/neutral,' the acoustic delivery exhibits indicators of frustration and intense dissatisfaction. It identifies the mismatch and produces a judgment favoring the emotional cue over the text.
* **Real Answer**: EMOTION: Anger/Resentment. SENTIMENT: Negative. Despite the polite words, the auditory features (stress patterns and pitch shifts) confirm the speaker is displeased.
* **Why this demonstrates the capability**: This case isolates the 'paralinguistic logic' dimension. It forces the evaluator to prioritize acoustic evidence over linguistic sychophancy, which is a core requirement for high-end audio-language adjudication where tone contradicts text.
---
**[Case 2]**
* **Initial Environment**: A cross-lingual evaluation environment for Indonesian-to-English Speech-to-Text Translation (S2TT). The audio involves a formal address to a high-ranking official using specific regional honorifics and informal local slang words for 'help' (e.g., 'tolong' vs 'bantu').
* **Real Question**: Evaluate the following English translation for accuracy and domain appropriateness.
* **Real Trajectory**: The evaluator listens to the Indonesian audio to identify the social hierarchy and stylistic tone. It checks the English output for 'Royalty/Formal' pronoun adherence and verify if 'slang' elements were correctly mapped to their semantic equivalents without losing the respectful framing. It finds a mismatch where the assistant used 'hey' instead of a formal address.
* **Real Answer**: SCORE: 2/5 (Significant inaccuracy in tone). The translator failed to capture the formal honorific usage of the source audio, providing a 'casual' English translation for a 'high-form' Indonesian address.
* **Why this demonstrates the capability**: This case demonstrates domain-specific translation adjudication for Southeast Asian (SEA) contexts. It tests the evaluator's ability to ground its score in cultural sociolinguistic rules captured within the audio signal.
---
**[Case 3]**
* **Initial Environment**: A non-speech Audio Question Answering (AQA) environment. The input is a 10-second clip of a forest soundscape: first, birds chirping, then a sudden heavy rain starts, followed by the sound of thunder.
* **Real Question**: Identify the sequence of environmental events in the audio and their relative order.
* **Real Trajectory**: The evaluator segments the non-speech audio into temporal chunks. It tracks the bird chirp event, marks the onset of rain at 4.2 seconds, and identifies the low-frequency rumble of thunder at the 8-second mark. It cross-references the candidate response against this sequential timeline.
* **Real Answer**: ACCURATE. The response correctly identifies the bird-rain-thunder sequence and correctly notes that the rain started before the thunder.
* **Why this demonstrates the capability**: This demonstrates 'Sequential Sound Tracking' and 'Environment Segmentation'. It proves the evaluator can analyze temporal relationships between non-linguistic auditory events, moving beyond simple keyword keyword-spotting in audio files.

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

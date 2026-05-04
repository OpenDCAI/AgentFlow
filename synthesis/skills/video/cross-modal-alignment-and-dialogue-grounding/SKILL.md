---
name: cross-modal-alignment-and-dialogue-grounding
description: Use this skill when the user asks 'what is visually present when this sound happens?', 'the video shows one thing but the person says another, which is right?', 'correct the spelling of this name based on the screen', 'find the exact time for this speech', or 'match the voice to the person'. It is triggered for tasks requiring explicit temporal grounding involving both audio and video, implicit cross-modal retrieval, or resolving cross-modal contradictions (like using sharp on-screen text to fix noisy or muffled audio transcripts).
---

# Skill: cross-modal-alignment-and-dialogue-grounding

## 1. Capability Definition & Real Case
* **Professional Definition**: The capability to perform joint audio-visual reasoning by resolving bi-directional semantic dependencies between auditory channels (speech, environmental sounds, music) and visual channels (entities, actions, OCR text) across a shared timeline. This encompasses explicit grounding, cross-modality target retrieval, and cross-modal semantic disambiguation—where high-fidelity evidence from one stream (e.g., sharp on-screen text) is used to correct degraded or ambiguous signals in another (e.g., distorted speech).
* **Dimension Hierarchy**: Multimodal and Generative Interpretation->Cross-Modal Grounding->cross-modal-alignment-and-dialogue-grounding

### Real Case
**[Case 1]**
* **Initial Environment**: A cooking video showing a kitchen counter with various ingredients. The audio contains the sound of a stove being ignited and a man providing commentary.
* **Real Question**: Can you describe the visual information of the video segment corresponding to this audio information: <A man speaks, 'We put a little sausage in there for flavor.' This is accompanied by the sounds of food sizzling and being stirred.>
* **Real Trajectory**: The agent first scans the audio track to locate the specific speech milestone and associated sizzling sound event (T=113.2s to 144.5s). It then anchors to the visual frames within this exact interval to identify the stove activity. Observations reveal scrambled eggs and meat being cooked in a white pan and manipulated by a specific tool.
* **Real Answer**: Scrambled eggs and small meat pieces are cooked in a white pan, stirred with a red spatula.
* **Why this demonstrates the capability**: This case demonstrates 'Audio-to-Video Implicit Grounding.' The agent cannot describe the specific pan color or tool (red spatula) from audio alone, nor can it know which specific cooking step the user is asking about without first localizing the 'sausage' speech in the audio stream.
---
**[Case 2]**
* **Initial Environment**: A multi-scene cinematic sequence with high-action transitions, featuring various characters reacting to an off-screen threat.
* **Real Question**: What are the start and end time of the audio segment corresponding to this audio information: <Intense, dramatic music with metallic clanging sounds is followed by a monstrous roar. A female voice whispers, 'He's here,' as the dramatic music swells.>
* **Real Trajectory**: The agent performs an 'Audio-to-Time' retrieval by indexing the acoustic profile of the clanging sounds and the specific whispered dialogue. It boundaries the start at the first metallic clang and the end at the peak of the orchestral swell. The resulting interval is mapped to the absolute video timeline.
* **Real Answer**: From 94.6 seconds to 105.4 seconds.
* **Why this demonstrates the capability**: This illustrates 'Explicit Audio-to-Time Grounding.' It requires high-precision temporal localization of complex, overlapping sound events (music, roar, whisper) to produce a rigid numeric boundary, proving the agent's absolute time awareness within the audio modality.
---
**[Case 3]**
* **Initial Environment**: A technical training video where a presenter is using a specialized software tool. The audio is slightly muffled by background noise.
* **Real Question**: Correct the transcription of the speaker's name and the software name based on the slide visuals.
* **Real Trajectory**: The agent identifies an audio segment at T=15s where the speaker introduces himself as 'Professor Bisk' and mentions the software 'Nexeed'. The ASR model initially transcribes these as 'Professor Bisque' and 'NextSeat'. The agent performs a visual scan of the title slide, detecting the OCR text 'Instructor: Prof. Bisk' and 'System: Nexeed'. It measures the phonetic similarity between the ASR output and the OCR text, confirming the visual evidence is a correction for the acoustic signature.
* **Real Answer**: The speaker is Professor Bisk and the software being discussed is Nexeed.
* **Why this demonstrates the capability**: This demonstrates 'Cross-Modal Semantic Disambiguation' via visual grounding. By using the high-precision OCR data as an anchor, the agent resolves phonetic ambiguity in the audio stream to provide a factually accurate index that the raw audio-to-text pipeline failed to capture.

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

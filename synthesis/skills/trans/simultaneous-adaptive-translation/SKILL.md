---
name: simultaneous-adaptive-translation
description: Use this skill when the user wants to translate content in real-time or as a stream, where the translation must start before the source text is finished. It is triggered by layman requests like 'translate this live,' 'start translating as I speak,' 'don't wait for the whole sentence to finish,' or 'real-time subtitles for this stream.' It allows for adaptive reading and writing based on specific latency needs (low, medium, or high).
---

# Skill: simultaneous-adaptive-translation

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to execute Simultaneous Machine Translation (SiMT) by adaptively alternating between reading source increments and writing target chunks within a continuous auto-regressive decoding loop. This requires the agent to manage the trade-off between translation quality and latency using explicit read/write signaling tokens and latency-aware prompts to ensure meaning-preserving, monotonic transfer from streaming inputs.
* **Dimension Hierarchy**: Contextual and Constraint-Aware Translation->Streaming and Latency-Aware Translation->simultaneous-adaptive-translation

### Real Case
**[Case 1]**
* **Initial Environment**: A streaming translation environment receiving an English news headline in chunks. The user requires high-quality output while balancing the speed of incoming data.
* **Real Question**: Translate the following headline into Chinese with medium latency: 'Avalanche at Washington state ski resort kills 1, traps 5'
* **Real Trajectory**: The agent reads 'Avalanche at Washington state ski resort' and observes that the semantic unit is sufficiently complete to translate the subject. It emits an <|end-of-read|> signal, translates this chunk into '华盛顿州滑雪场发生雪崩', and then emits <|end-of-write|>. It then reads the remainder 'kills 1, traps 5', emits <|end-of-read|>, and completes the translation with '造成 1 人死亡，5 人被困' followed by <|end-of-write|>.
* **Real Answer**: 华盛顿州滑雪场发生雪崩，造成 1 人死亡，5 人被困
* **Why this demonstrates the capability**: This demonstrates adaptive read/write policy because a fixed policy (like wait-k) might have translated 'Avalanche at Washington state' prematurely as '华盛顿州的雪崩', which is grammatically awkward once 'ski resort' arrives. By reading until the full semantic subject is captured, the agent achieves higher BLEU and better structural integrity, proving it can adjust its reading window based on content rather than just token counts.
---
**[Case 2]**
* **Initial Environment**: A real-time interpretation scenario for weather alerts. The source text is in Chinese and arrives in fragments, requiring a monotonic English output.
* **Real Question**: Translate the following alert into English with low latency: '休斯敦16日晚发出一系列龙卷风和严重雷暴警报。'
* **Real Trajectory**: The agent reads '休斯敦' and immediately translates 'Houston'. It then reads '16日晚' and translates 'on the evening of the 16th'. This continues with '发出一系列' (issued a series of), '龙卷风' (tornado), and '和严重雷暴警报' (and severe thunderstorm warnings), interleaving reading and writing tokens to maintain a high-speed output stream.
* **Real Answer**: Houston on the evening of the 16th issued a series of tornado and severe thunderstorm warnings.
* **Why this demonstrates the capability**: The case illustrates latency-aware segmentation where the agent breaks the source into very brief phrases at the 'low latency' setting. It demonstrates the ability to maintain grammatical tolerance in the target language despite the fragmented input stream, showcasing the auto-regressive reuse of the KV-cache without re-calculating the entire history.

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

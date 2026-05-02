---
name: long-form-coherent-summarization-data-synthesis
description: Use this skill when the user wants summaries of long books, reports, transcripts, or other oversized documents where the summary must still read smoothly from beginning to end. Trigger it for requests like "summarize this huge file without losing the thread," "make the summary flow logically," "avoid choppy chunk summaries," or "test whether the model can keep coherence over a very long document." This is the right skill when the core difficulty is not finding one answer, but preserving continuity, salience, and narrative logic after many chunk-level operations.
---

# Skill: Long-form coherent summarization

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to summarize very long documents while preserving global coherence across chunk boundaries, maintaining a readable narrative structure rather than a bag of disconnected local summaries. The capability is primarily about long-range continuity: who is being discussed, what happened, why it matters, and how later parts relate to earlier ones after chunk-and-compress processing.
* **Dimension Hierarchy**: Document Transformation & Synthesis->Summarization->Long-form coherent summarization

### Real Case
**[Case 1]**
* **Initial Environment**: A recently published book far longer than the model context window is split into chunked inputs, and the system must produce one global summary from the entire book.
* **Real Question**: "Summarize the following book-length document."
* **Real Trajectory**: The system first generates chunk-level summaries and then either hierarchically merges them or incrementally updates a running summary while compressing when necessary.
* **Why this demonstrates the capability**: The benchmark explicitly studies what happens when long summarization requires chunking, merging, updating, and compression. The central quality target is coherence, not just lexical overlap with a reference. This makes it the right case for testing long-range continuity under context pressure.

---
**[Case 2]**
* **Initial Environment**: A long government report, patent, or transcript is supplied as a single-document summarization task in a long-context evaluation suite.
* **Real Question**: "Write a summary of the document that preserves the important information across the whole context."
* **Why this demonstrates the capability**: These tasks test whether a model can aggregate information spread across many pages without collapsing into omissions, contradictions, or duplicated points. Unlike short-article summarization, the model must keep section-to-section continuity and relative salience under long input lengths. This demonstrates practical long-document summarization beyond book fiction.

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

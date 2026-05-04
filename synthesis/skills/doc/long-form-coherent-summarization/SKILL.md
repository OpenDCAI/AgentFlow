---
name: long-form coherent summarization
description: Use this skill when transforming massive documents or multi-source corpora into structured, coherent formats. Trigger for requests like 'summarize this huge PDF without losing the thread', 'draft a defense statement based on this complaint and the evidence list', 'create a presentation script from this report', or 'write the official trial facts by resolving contradictory testimonies into a ground-truth timeline'. This is critical when shifting text registers, interleaving visual anchors, or composing professional narrative sections from conflicting multi-source contexts.
---

# Skill: long-form coherent summarization

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to summarize massive documents or compose structured professional narratives by synthesizing information from oversized, multiple, or conflicting source documents. It encompasses register and stylistic transformation, chunk-compression, and multimodal interleaving, alongside establishing verified ground-truth timelines (e.g., Trial Facts) by mapping specific claims to corresponding evidence artifacts.
* **Dimension Hierarchy**: Document Transformation & Synthesis->Summarization->long-form coherent summarization

### Real Case
**[Case 1]**
* **Initial Environment**: A lengthy government report spanning multi-chapter inputs far exceeding standard context windows is provided.
* **Real Question**: Write a summary of the document that preserves the important narrative structures across the whole context without losing causal dependency.
* **Real Trajectory**: The agent progressively segments the massive document by discourse role, maintains an active ledger of core entities and causal threads, and collapses trivial anomalies. It securely maintains the structural spine connecting Chapter 1's incident with Chapter 12's resolution.
* **Real Answer**: An unbroken, self-sufficient narrative summary describing the total causality chain seamlessly.
* **Why this demonstrates the capability**: This illustrates baseline long-range thematic aggregation. By executing iterative chunk-and-compress methodologies, it consolidated diverse fragments from a massive file, confirming continuous reasoning over massive limits.
---
**[Case 2]**
* **Initial Environment**: A multi-document environment comprising a formal 'Prosecution' document detailing claims and a structured 'Evidence' list including contracts and bank records.
* **Real Question**: Based on the provided prosecution and relevant evidence, please draft a detailed defense statement that addresses each allegation individually.
* **Real Trajectory**: The agent extracts distinct claims into a Dispute Ledger. It scans the Evidence list to match allegations to factual receipts, constructs a rebuttal for each point citing the specific evidence name, and applies a formal legal tone to ensure standard judicial structure.
* **Real Answer**: A structured Defense Statement that systematically denies or clarifies the plaintiff's allegations, mapping each rebuttal to Evidence Item #1 and Item #2.
* **Why this demonstrates the capability**: This demonstrates argumentative composition and multi-source structural alignment. The agent does not simply summarize; it drafts a formal narrative section that structurally responds to a multi-source dispute constraint with verified facts.
---
**[Case 3]**
* **Initial Environment**: A document pool containing a Prosecution document, a Defense Statement, and several conflicting evidence summaries regarding a property dispute.
* **Real Question**: Synthesize the factual descriptions from the prosecution, defense, and evidence to write the 'Trial Facts' section, resolving contradictions to establish a verified timeline.
* **Real Trajectory**: The agent creates a chronological timeline of events, identifies a contradiction between Plaintiff (July 10) and Defendant (July 12), and uses a verified stamped contract (July 11) to resolve the conflict. It drafts a neutral narrative prioritizing hard evidence over testimony.
* **Real Answer**: Trial Facts: 'On July 11, 2010, the parties entered into a Factory Lease Contract. Upon examination, it was ascertained...'
* **Why this demonstrates the capability**: This demonstrates contradiction triage and narrative synthesis. The agent establishes a verified ground-truth timeline from contradictory multi-source documents to compose an official, objective professional report.
---
**[Case 4]**
* **Initial Environment**: An architectural document features complex textual histories of famous structures paired natively with distinct photographic visual assets.
* **Real Question**: Describe the Louvre and its collections, directly inserting the representative photographs provided within your generated text to create an embedded guide.
* **Real Trajectory**: The agent extracts contextual paragraphs discussing separate wings while logging explicit image references. It crafts the cohesive summary and seamlessly splices the image array tags directly following their associated descriptive linguistic anchors.
* **Real Answer**: The Louvre holds some of the world's most intricate architecture [IMAGE_LOUVRE]. Its highlight, the Mona Lisa, exemplifies the era's techniques [IMAGE_MONA_LISA].
* **Why this demonstrates the capability**: This demonstrates interleaved multimodal answer synthesis. The system merges pictorial placeholders straight into continuous synthesized prose to execute cohesive multimedia formatting.

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

---
name: citation-grounded factuality checking
description: Use this skill when the user wants the agent to judge whether an answer/document is securely backed by authentic evidence, verify exact pinpoint highlight spans, validate strict antecedent document grammar (e.g. tracking 'the' to 'a'), or audit sites for safety/phishing risks and machine-generated stylistic anomalies. Trigger for 'verify this highlighted claim,' 'check if this legal clause has grammatical consistency,' 'is this link a scam?', or 'identify if any of these sentences were polished by AI.' It is essential for eliminating hallucinations, detecting structural phrasing errors, and ensuring document authenticity.
---

# Skill: citation-grounded factuality checking

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to audit and verify document-grounded text across multiple dimensions: (1) Localized attribution of specific generated claims (LAQuer) via recursive decontextualization; (2) Intra-document structural and grammatical integrity (e.g., tracking antecedent basis definitions and checking formatting logic); and (3) Security and stylometric anomaly auditing (detecting spoofing/phishing risks or text regions exhibiting unverified machine-generated authorship).
* **Dimension Hierarchy**: Document Validation & Structuring->Verification->citation-grounded factuality checking

### Real Case
**[Case 1]**
* **Initial Environment**: A generated RAG output answering a query about GMO labeling contains multiple sentences about consumer confusion.
* **Real Question**: Verify this specific highlight: 'They deserve to know what they are eating.'
* **Real Trajectory**: The agent identifies the pronoun 'They', decontextualizes it by referencing the previous sentence to map 'They' to 'Consumers.' It queries the source material with 'Consumers deserve to know' and localizes a 10-word span: 'Consumers... have a right to know what is in their food'.
* **Real Answer**: Supported: 'Consumers... have a right to know what is in their food' (Source: nbcnews.com).
* **Why this demonstrates the capability**: This demonstrates localized span-level verification and decontextualization. The agent resolves the ambiguity of the pronoun implicitly before executing precise sub-sentence attribution, ensuring the fact checks the actual intended entity.
---
**[Case 2]**
* **Initial Environment**: A legal technical description of a biometric processing device is loaded, representing a high-stakes structural document.
* **Real Question**: Check the document for internal 'antecedent basis' logic errors regarding processor and display entities.
* **Real Trajectory**: The agent performs a structural traversal, linking definite noun phrases ('the [noun]') to their introductory indefinite phrases ('a [noun]'). It verifies 'the processor' links to 'a processor', but flags 'the touchscreen display' as appearing definitively without prior introduction.
* **Real Answer**: Error detected: 'The touchscreen display' lacks an antecedent basis. It appears as a definite reference without prior structural introduction.
* **Why this demonstrates the capability**: Demonstrates intra-document structural integrity validation. Precise verification involves ensuring terminology continuity, tracking article pairing, and formally evaluating document syntax robustness without external knowledge.
---
**[Case 3]**
* **Initial Environment**: A document environment features a source claiming to be an 'Official Update' with instructions, though it lacks semantic diversity and alters procedural tone abruptly.
* **Real Question**: Verify the authenticity of these software deployment instructions and identify anomalies.
* **Real Trajectory**: The agent audits URL metadata and structural layout, while also deploying sliding-window assessments on the text sequence. It flags a phishing warning concerning the URL and identifies that the final paragraph exhibits a stylometric drop in perplexity consistent with machine generation.
* **Real Answer**: Warning: Source documentation exhibits phishing risk attributes, and sentences 12-14 show stylometric anomalies symptomatic of unverified AI-generated modifications.
* **Why this demonstrates the capability**: Validates extrinsic source authenticity and adversarial grounding safety. Verification requires assessing the meta-integrity of the context itself (phishing risk) and detecting localized authorship stylometric anomalies before trusting the content.

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

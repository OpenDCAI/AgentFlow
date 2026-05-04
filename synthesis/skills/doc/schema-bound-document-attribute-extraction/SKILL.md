---
name: schema-bound document attribute extraction
description: Use this skill when the user wants to extract structured labels, relationships, or granular metadata from messy text, layout-rich forms, or specialized diagrams. It is crucial for scientific document processing and 'Knowledge Grounding', where extracted terms must be mapped to specific ontology IDs (like UBERON or NCBITaxon) to resolve polysemy. Trigger it for requests like 'pull the key attributes from this scanned invoice', 'map these brain regions to their ontology IDs', 'convert this PDF assessment into a machine-readable schema', 'find the causal relationship between these two entities', or 'extract the sheet music into an array of notes'.
---

# Skill: schema-bound document attribute extraction

## 1. Capability Definition & Real Case
* **Professional Definition**: The ability to perceive unstructured or semi-structured document content (text, visual layouts, or domain symbols) and map them onto a predefined schema, relational graph, or formal ontology. This includes 'Knowledge Grounding'—the process of disambiguating polysemous terms (e.g., distinguishing 'cortex' in brain anatomy vs. plant biology) by aligning raw extractions with canonical identifiers from external knowledge bases. It requires resolving spatial-to-logical bindings in forms, tracking inter-sentential relation directionality, and executing format normalization (e.g., date/unit cleaning) to ensure outputs are FAIR-compliant (Findable, Accessible, Interoperable, and Reusable).
* **Dimension Hierarchy**: Document Validation & Structuring->Extraction->schema-bound document attribute extraction

### Real Case
**[Case 1]**
* **Initial Environment**: A clinical note sentence containing social determinants of health (SDoH) data.
* **Real Question**: Classify the sentence under the SDoH schema: Pt missed appointment because her sister couldn't drive her today.
* **Real Trajectory**: The agent identifies the phrase 'sister couldn't drive her', categorizes it as a transportation barrier, and maps it to the specific 'adverse status' field within the transportation dimension of the SDoH schema.
* **Real Answer**: Transportation issue; adverse SDoH mention.
* **Why this demonstrates the capability**: This illustrates baseline schema-bound classification, transforming a natural language reason for an appointment skip into a standardized categorical label.
---
**[Case 2]**
* **Initial Environment**: A scientific paper in the neuroscience domain discussing brain regions and anatomy.
* **Real Question**: Extract the term 'cortex' from the text and align it with the correct ontology ID from the UBERON knowledge base.
* **Real Trajectory**: The agent identifies the term 'cortex'. It performs a context check to determine if the document refers to animal anatomy or botany. Confirming it is a neuroscience paper, it retrieves the UBERON identifier (UBERON_0000956) and the canonical label (Actinopterygii/cerebral cortex) rather than the plant tissue ID (PO_0005708).
* **Real Answer**: {"entity": "cortex", "ontology_id": "UBERON:0000956", "label": "cerebral cortex"}
* **Why this demonstrates the capability**: This case demonstrates 'Knowledge Grounding' and polysemy resolution. The agent uses external symbol knowledge to ensure that a common term is mapped to its unique, domain-correct identifier.
---
**[Case 3]**
* **Initial Environment**: A scanned PDF of the 'Mood and Feelings Questionnaire: Long Version' (MFQ-LV), which is a semi-structured clinical assessment instrument.
* **Real Question**: Convert the instrument metadata into a structured ReproSchema object, including item prompts and scoring rules.
* **Real Trajectory**: The agent parses the PDF layout to identify the instrument title and instructions. It then iterates through the questions, extracting the specific prompt for each (e.g., 'I felt miserable or unhappy') and the response scale (0-2). Finally, it identifies the cumulative scoring logic (summing item scores).
* **Real Answer**: {"instrument": "MFQ-LV", "questions": [{"id": "q1", "text": "I felt miserable or unhappy", "options": [0, 1, 2]}], "scoring_method": "sum"}
* **Why this demonstrates the capability**: This demonstrates 'multi-level metadata extraction'. The agent must extract both low-level item properties and high-level behavioral logic (scoring) to satisfy a complex community-standard schema (ReproSchema).

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

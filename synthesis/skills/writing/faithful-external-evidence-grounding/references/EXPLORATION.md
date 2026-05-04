# Phase 1: Environment Exploration Guide
* **Exploration Strategy**:
  - Conduct an 'Entity-Centric Extraction' combined with a 'Rhetorical Purpose Mapping.' Divide the input data—whether table rows, JSON keys, or text—by semantic category, isolating explicit targets while aggressively ignoring out-of-scope fields.
  - Quantize evidence reliability into Confidence-Level Buckets. Assign 'High-Priority' labels to facts directly anchoring the prompt. For structured tables, lock the numerical values and units (e.g., 5000, mAh) as singular, immutable tuples.
  - Perform an 'OOD (Out-of-Distribution) Leakage Scan' to safeguard against 'Prior Knowledge Hallucinations.' Verify that all references, entities, and measurements correspond strictly to the provided context, preventing internal pre-training parameters from replacing missing facts.
  - Map 'Citation-to-Claim Triplets' or 'Value-to-Metric Triplets' for dense grounding tasks. Tie exactly one extracted fact to one planned sentence to ensure 1:1 attribution accountability.
* **Target Trajectory Profile**:
  - The trajectory records an explicit 'Evidence-to-Annotation' ledger identifying every data point targeted for synthesis to enforce a completely transparent audit trail of metadata integration.
  - The trajectory prioritizes 'Contextual Alignment' over standard lexical overlap, ensuring unit numbers and specific technical proper nouns remain structurally frozen before generating prose.
  - The trajectory displays rigorous 'Truthfulness Verification' identifying if a requested claim is unsupported by the table or abstracts. If unsupported, the trajectory deliberately opts to omit it entirely.
  - The trajectory concludes with an 'Entity Recall Audit' ensuring that every mandatory table stat, biological sequence, or academic cite key from the extraction phase successfully survived into the draft.

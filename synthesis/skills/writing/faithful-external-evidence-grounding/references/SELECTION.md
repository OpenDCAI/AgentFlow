# Phase 2: Trajectory Selection Criteria
* **Acceptance Metrics**:
  - Accept a trajectory only if Entity-BLEU alignment (or direct unit matching) to the context is absolutely pristine. All technical names, units, and stats (e.g., 5000mAh, 13 MP, Meng et al.) must match exactly.
  - Accept a trajectory only if all selected attributes have a direct, verifiable semantic link to the user's specific sub-query, ensuring informational density without unrelated filler.
  - Accept a trajectory only if 'Confidence Calibration' is evident. Extracted assertions should explicitly mirror the confidence metrics (high vs low) natively listed in the environmental source data.
  - Accept a trajectory only if the numerical and terminological invariants are strictly locked, successfully thwarting any generalized LLM attempts to round numbers or simplify formal system titles down to generic terms.
* **Rejection Criteria**:
  - Reject any trajectory where 'ROUGE-L' (Lexical Overlap) is achieved at the expense of empirical precision—e.g., attributing a discovery to the wrong author or altering a specific stat.
  - Reject any trajectory that solves syntactic flow by omitting mandatory technical qualifiers or citations. Trimming an exact integer to an approximation is an absolute grounding failure.
  - Reject any trajectory exhibiting 'Unit Scaling Confusion' converting Megapixels to battery sizes or altering the fundamental semantic metric provided in tabular form.
  - Reject any trajectory utilizing 'In-Weights Memorization' to invent plausible defaults (e.g., assuming 'NVIDIA GPUs' because parallelization is mentioned) when the provided context lacks that specific metadata.

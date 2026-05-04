# Phase 1: Environment Exploration Guide
* **Exploration Strategy**:
  - Perform a Source-to-Provider Schema Audit to identify mismatches between provided configs and true infrastructure requirements (e.g., Terraform block nesting rules). Referencing API documentation takes precedence over blind parameter guessing.
  - Decompose the task into discrete intermediate deliverables (Extraction, Staging, Cleansing, Aggregation, Validation) before writing transformation queries, averting monolithic processing and un-trackable dependencies.
  - Execute Custom Schema Validations. For varying data streams (like APIs or unstructured JSON sources), manually override auto-detect capabilities lacking boundary limits. Probe warehouse environments to align destination schemas correctly.
  - Utilize Graph Evaluation and Asynchronous Monitoring. Traverse existing repo tools (like DBT Macros or Python status scripts) continuously verifying independent step completion safely before triggering successive staging jobs.
* **Target Trajectory Profile**:
  - Trajectory mandates a 'Read-Before-Write' structure, explicitly sourcing integration provider docs or internal macro utilities prior to executing Terraform apply phases or complex SQL scripts.
  - Shows 'Increment-to-Verify' execution tracking. Traces test connections against single tables iteratively monitoring logs to identify authentication failures swiftly, resolving them earlier rather than compounding multiple source configurations blindly.
  - Employs 'Intermediate Checkpoint Tracking' to validate artifact fidelity. The agent performs dry runs or outputs data snapshots sequentially to guarantee grouping boundaries or schema normalization behaved as expected.
  - Demonstrates authoritative 'State-Tracking'. Explicit record of successful syncs isolates pipelines, preventing redundant sync retriggers causing polluted or duplicated terminal warehouse rows.

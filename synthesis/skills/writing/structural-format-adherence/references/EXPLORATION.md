# Phase 1: Environment Exploration Guide
* **Exploration Strategy**:
  - Start by extracting every explicit outer-form constraint from the user request and rewriting each one as a checkable rule. Map constraints into categories such as wrappers, section boundaries, list cardinality, and jurisdictional/genre blueprints (e.g., mandatory 'Governing Law' sections).
  - Execute 'Instruction-to-Logic Variable Mapping' to decouple user-provided constants from boilerplate text. Extract every specific entity (names), quantity (amounts), and temporal constraint (dates) and record them as 'Protected Tokens' frozen from model drift.
  - Translate approximate natural-language formatting requests into deterministic operational decisions. Expressions like “put it into two square brackets,” “use markdown bullets,” or “build an agreement” require establishing exact token boundaries or sectional context anchors early.
  - Reserve content slots only after the structure is fixed. Once the shell is stable, map the minimum semantic payload needed for each slot so that the agent does not later add accidental overflow paragraphs, bullets, or non-requested industry clauses.
* **Target Trajectory Profile**:
  - A good trajectory explicitly records every structural obligation before any drafting begins. It frames a 'Top-Down Structural Blueprint' where the agent lists all planned headers and variable injections before generating prose.
  - A good trajectory minimizes structural ambiguity at the token level. It decides whether separators are JSON braces, literal phrases, or markdown headers, firmly avoiding 'Boilerplate Contamination' (e.g., using corporate templates for personal drafts).
  - A good trajectory actively budgets content into the fixed structure instead of writing freely. For example, if there must be exactly four bullets or specifically 3 financial clauses, the trajectory plans exactly that capacity.
  - A good trajectory finishes with a deterministic verification pass. The final check must validate counts, exact wrappers, jurisdictional completeness, and absolute fidelity of injected user variables.

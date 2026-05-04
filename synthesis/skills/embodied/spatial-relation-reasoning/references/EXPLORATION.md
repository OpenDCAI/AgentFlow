# Phase 1: Environment Exploration Guide
* **Exploration Strategy**:
  - Reference-Frame Localization: Deliberately anchor relative directions ('left', 'behind') into clear coordinate domains, distinguishing between camera-centric perspectives vs allocentric landmark references.
  - Exhaustive Relational Over-Sampling: Scan images and systematically evaluate pairwise interactions in natural text (e.g., 'A is on B', 'C is clear') to assure total environmental scene-graph mapping without missing preconditions.
  - Cross-View Anchor Synchronization: Discover persistent structural entities intersecting multiple partial RGB viewpoints, acting as pivot anchors to resolve occluded relative relationships.
  - Depth-Consistent Occlusion Probing: Rotate cameras significantly relative to complex depth fields to visually adjudicate whether an object operates 'behind' a barrier versus sitting tangentially 'adjacent'.
* **Target Trajectory Profile**:
  - Relation-Dependent Disambiguation: Highlights environments rendering isolated semantic object searches impossible unless robust spatial predicate rules are fully satisfied.
  - Exhaustive Semantic Logic Coherence: Showcases a perfect, unbroken linkage documenting visual evidence to the resultant extensive natural language state-space map list.
  - Implicit Grounding Realization: Evaluates conditions mandating derivations of unseen states based purely on structural negative voids (e.g., classifying a platform as 'clear' since zero pixels overlap it).
  - Steady Multi-Hop Viewpoint Trace: Maintains a rigidly stable, documented yaw/pitch log prohibiting orientation swapping artifacts from corrupting relative position judgements.

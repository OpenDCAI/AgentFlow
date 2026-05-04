# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Synthesize the report using 'Real-Time Evidence Injection': generate a textual segment, emit the <visualization> tag for necessary proof, and only proceed with the next analytical claim once the 'Visual Grounding' is confirmed. This forces the agent to condition subsequent text on the *actual* visual context rather than a projected plan. A concrete application is using the 'returned caption' from the analysis agent to anchor the opening sentence of the next chapter.
  - Implement 'Prompt-to-Visual Alignment' by drafting the interpretation immediately surrounding the image tag. Ensure that specific visual descriptors (e.g., 'the violin plot shows wide distributions in Africa') are used to 'weave' the data into the narrative. Replace generic transitions like 'The following chart shows...' with 'The staggering 9.33-year gap in Belarus, seen in [IMG#1], suggests unique social risks...'.
  - Generate 'Integrated Synthesis Dashboards' at the conclusion of major sections to aggregate multiple metrics (e.g., maps, trends, and stats) into a single analytical view. This forces the synthesis to 'close the loop' on recurring themes, turning detailed localized analyses into a decision-ready executive summary. A concrete rule is ensuring that for every 3-4 charts, a final 'Multi-Panel Dashboard' is synthesized to provide a high-level 360-degree view.
  - Apply 'Aesthetic Simplicity and Polish' to the final multimodal draft, ensuring no AI conversational filler (e.g., 'Here is a chart...') interrupts the narrative flow. Use professional, statement-based chart titles (e.g., 'Fig 1: Global Inequity in Energy Electrification') and seamless transitions to maintain the 'Data Journalism' persona. This ensures the output reaches the highest rank in 'Human Evaluation' for both visual consistency and publication readiness.
  - Perform a final 'Textual Information Depth Audit' by counting the number of multi-step insights derived from the visual evidence. Check that for every chart, there is at least one 'Interpretive Delta'—a claim that is supported by the chart but contains additional context-specific analysis. If a paragraph is identified as a 'Surface Description,' you must revise it by adding a 'Decision-Oriented' conclusion based on the underlying tables.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

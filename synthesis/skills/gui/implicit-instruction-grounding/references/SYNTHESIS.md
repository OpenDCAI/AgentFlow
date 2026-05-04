# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Diverse Semantic Instruction Seeding: For every target widget, generate a 'Cluster' of three variations: a literal one, a casual one, and a functional-intent one. Use phrasing like 'Kill all the filters' (casual) alongside 'Clear all' (literal) to ensure the training data promotes semantic unification (UWIU) over lexical matching. For example, ask 'How do I start fresh?' to target the 'Reset' button, forcing the agent to infer functional equivalence from context.
  - Dense Multi-Widget Conflict Generation: Compose environments containing 5-10 distinct functional icons in a single header and create instructions that specifically target one to test discrimination (MWAM). Use language that describes a sub-goal (e.g., 'Put this on my list') that could plausibly map to two items (Wishlist vs Cart), forcing the agent to use precise visual attributes. For instance, phrasing an instruction as 'Save this for later purchase' rules out 'Add to Cart' and requires the 'Wishlist' heart icon instead.
  - Topological Sequence Scaffolding: Formulate tasks where the final goal (e.g., 'Add to bag') is blocked by a mandatory pre-selection like 'Color' or 'Size'. You should structure the trajectory JSON to show the agent identifying the dependency and resolving it before the terminal click. A concrete question would be: 'Purchase the blue version of this shirt,' which requires the agent to first click the color swatch and then the buy button.
  - Sibling Contextual Disambiguation: Use instructions targeting one of many identical buttons, requiring the agent to utilize adjacent text for grounding. Use phrases like 'Click the 'Details' for the second item' or 'View the invoice from yesterday' to test structural proximity. For example, in a list of 'Remove' buttons, the question 'Delete the appointment for 2 PM' forces the agent to align the 'Remove' button with the '2 PM' timestamp sibling.
  - Layman Metaphor Injection: Replace technical GUI terms ('Dropdown', 'Radio button', 'Menu') with layman physical descriptions like 'the list at the top' or 'the round option'. This ensures the synthesized data reflects how real users interact with interfaces imprecisely. For example, 'Tap the small downward arrow to change the order' tests if the agent can map visual geometry to the professional 'Sort' function.
  - Instruction-Widget Cross-Check Answer: Force the final 'Answer' to explicitly reflect why a specific widget was chosen among its neighbors, validating the discrimination logic. The answer should not just be 'Task done,' but 'Sorted by price as requested using the top-right menu.' This ensures the evaluation captures the successful resolution of state-level ambiguity found in the XBOUND benchmark.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

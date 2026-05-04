# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Multi-Category Instruction Variety. Design questions using semantic, positional, visual, or semantic constraint categories to target continuous ranges. Use phrasing like 'the paragraph about AI benefits' (Semantic) or 'Select the 4th and 5th sentences' (Positional). For drawing, instruct 'Create a 3x3 array of black boxes' mixing arithmetic with spatial layouts.
  - Explicit/Implicit Drag Commands. Vary the question between explicit drag instructions ('Drag the mouse to select...') and implicit range instructions ('Highlight the text from A to B'). This forces the agent to infer the continuous physical action requirement from intent. For instance, 'Copy the range between the header and the first image' requires the agent to realize it must execute a drag action.
  - Relational Constraint Seeding. Design questions that use semantic prepositions like 'inside', 'below', 'surrounding', or 'centered within' to force coordinate bounding calculations. Use phrasing like 'Draw a cyan line directly underneath the magenta circle' to test multi-state synchronization. This bridges standard motor control with visual geometrical planning.
  - Scale and Precision Value Targeting. Frame instructions for reaching specific points on sliders or scales using relative layman terms. Use phrases like 'Turn it up about halfway' or 'Set the opacity exactly in the middle' to measure fine continuous control. 'Adjust the brightness until it is almost at the maximum setting' directly tests fine-motor granularity on the UI.
  - Layman Dexterity Phrasing. Use straightforward language to describe physical manipulation, such as 'Put this PDF into the folder', 'Draw a house frame', or 'Chuck that sentence into a highlight'. Specify a clear source object and a clear destination/boundary that requires crossing screen coordinates. 'Take that invoice on the left and move it into the Work folder on the right' forces a multi-point spatial trajectory calculation.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

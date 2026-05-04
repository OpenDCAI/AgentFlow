# Phase 3: Data Synthesis Instructions
* **Question Generation Rules**:
  - Construct 'Dynamic Range Verification Queries' that ask the agent to rate the intensity of movement and justify it with spatial milestones. Use templates like: 'On a scale of 1-5, how dynamic is the motion in this clip, and what specific traversal distance did the main subject cover?' This prevents simple binary guesses and forces the agent to use kinetic evidence.
  - Generate 'Subject and Background Consistency Audits' that demand the model identify any 'morphing' or 'warping' artifacts. Formulate questions such as: 'Does the background environment remain structurally stable as the camera pans, or do you observe any warping or geometric inconsistencies? Detail the specific timestamps of any flicker.'
  - Implement 'Semantic-Alignment Fidelity Challenges' that ask why a specific dynamic effect looks natural (or unnatural) based on the prompt. For instance, draft a question like: 'Given the initial image showing a water splash, does the generated video maintain the fluid-dynamic properties of water throughout the animation? Describe any points where it looks like static noise.'
  - Design 'Naturalness and Motion-Smoothness Distractors' that offer plausible but incorrect descriptions of the video's quality. Create wrong options that claim 'the motion is fluid' when it is actually stuttery, or 'the identity is persistent' when the shirt color changes slightly. This forces the model to perform high-resolution perceptual auditing rather than just confirming arrival at a topical goal.
  - Apply 'Step-by-Step Consistency Justification' in the ground truth answers where the agent tracks a specific set of attributes from Start to Finish. Each step must be formatted as: '[T=0s] Subject: Curly hair, Blue shirt. [T=2s] Subject: Identity remains consistent during turn. [T=4s] Subject: Persistent attributes verified at conclusion.' This ensures the synthesis focuses on the 'Perceptual Persistence' required for auditing generative fakes.
* **Expected Output Format**: Output the QA pairs you generate in the following JSON format. Please construct the trajectory section based on your real exploration trajectory.
{
  "question": "...",
  "answer": "...",
  "trajectory": [
    {"step": 1, "observation": "...", "action": "..."},
    {"step": 2, "observation": "...", "action": "..."}
  ]
}

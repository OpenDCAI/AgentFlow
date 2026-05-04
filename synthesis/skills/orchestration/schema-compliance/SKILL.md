---
name: schema-compliance
description: Use this skill when the user wants examples where the agent must call tools with the exact right fields and formats, such as “make it fill every input correctly,” “test whether it messes up the API format,” “see if it uses the right parameter types,” or “give me tasks where a nearly-right tool call should still count as wrong.” Trigger it for casual requests about strict forms, exact JSON, required arguments, date formats, enums, or typed fields. Example triggers: “I want tasks where one wrong field breaks everything,” “test exact tool-call formatting,” “make the agent stop guessing parameter values,” and “give me cases where it has to respect every required field.”
---

# Skill: schema-compliance

## 1. Capability Definition & Real Case
* **Professional Definition**: Schema compliance is the capability to translate a natural-language task into tool invocations that exactly satisfy formal interface constraints, including required fields, legal value ranges, type restrictions, enum membership, nesting rules, and permissible combinations of optional arguments. For an orchestration agent, this capability is not merely low-level API hygiene: it is the precondition that makes reliable delegation possible at all. A coordinator that chooses the right worker but binds the wrong payload still fails the orchestration problem.
* **Dimension Hierarchy**: Tool Invocation Fidelity->Invocation Specification Handling->schema-compliance

### Real Case
**[Case 1]**
* **Initial Environment**: A tool-using workspace contains a medical-calculator server that exposes a kidney-function calculator with a strict input schema. The available calculator requires four arguments with explicit types: serum creatinine as a decimal number, cystatin C as a decimal number, age as an integer, and a boolean sex flag. The agent can inspect tool documentation before making the call, but the server rejects malformed requests immediately.
* **Real Question**: Calculate the patient’s kidney function using creatinine, cystatin C, age, and sex. Make sure the call uses the exact fields expected by the tool.
* **Real Trajectory**: The agent first reads the tool schema, notices that the endpoint requires `scr`, `scys`, `age`, and `male`, converts the user’s prose into those exact keys, preserves numeric precision for the lab values, maps sex into the required boolean, and then issues one valid calculator call. It does not invent extra keys, omit required keys, or coerce the integer field into free text.
* **Why this demonstrates the capability**: This case tests whether the orchestrator can bridge from informal task language to a strict machine interface without semantic drift. The reasoning burden is not the medical formula itself but the precise packaging of arguments in the only acceptable formal shape. A model that is semantically correct yet structurally sloppy still fails this capability.
---
**[Case 2]**
* **Initial Environment**: An email-and-calendar environment contains mock productivity tools whose interfaces are intentionally close to real systems. One task requires composing an email with a valid recipient field, subject, and body, then applying the correct follow-up operation to the created message using the returned identifier. The agent has access to tool descriptions but receives only a casual user request.
* **Real Question**: Send Alex a dinner invitation for tomorrow and label the resulting message as urgent.
* **Real Trajectory**: The agent chooses the email-creation tool, fills the structured fields exactly, captures the message identifier from the response, and then invokes the labeling tool with the returned identifier and the valid label argument. It does not skip the intermediate identifier dependency, substitute a guessed ID, or use natural-language text where a structured argument is required.
* **Why this demonstrates the capability**: This demonstrates schema compliance because success depends on obeying two interfaces exactly, not merely understanding the user’s goal. The second call is only possible if the first call was structurally valid and if the returned state is bound into the next payload in the expected format. The case also exposes a common orchestration failure mode: the agent semantically knows what to do, but binds the wrong key names or payload types.

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

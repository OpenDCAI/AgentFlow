import openai
import json
import os
import concurrent.futures
from collections import deque
import argparse
import pdb
import bdb
from dotenv import load_dotenv
load_dotenv()

from tools import *

openai.api_key = os.environ.get("OPENAI_API_KEY", "")
openai.base_url = os.environ.get("OPENAI_API_URL", "")

SYSTEM_PROMPT = """You are powerful AI assistant. You need to use tools to solve the problem.

## Available Tools

{tool_descriptions}

## Tool Usage Strategy

**For File-Based Tasks:**
1. When using "execute_code" to parse and read files, files is required, and the path passed in the parameter must be consistent with the file loading path in the code, otherwise a FileNotFoundError exception will be reported.
2. "analyze_omnimodal" tool only supports eight file formats: .png, .jpg, .mp4, .mov, .avi, .mkv, .mp3, and .wav.
3. "analyze_file" tool supports all file formats except the eight file formats listed in "analyze_omnimodal" tool.

**For Multi-Step Analysis:**
1. Break complex problems into logical steps
2. Use ONE tool at a time to gather information
3. Verify findings through different approaches when possible

## Response Format

**During Investigation (most responses):**
Think through your next steps, then use the appropriate tool:

```
I need to [describe what you're trying to accomplish]. Let me [specific action].

<tool_call>
{"name": "tool_name", "arguments": {"parameter": "value"}}
</tool_call>
```

**For Final Answers (only when completely confident):**
You can explain your reasoning, but your final answer MUST be concise:

```
Based on my analysis using [tools used], I can now provide the final answer.

<final_answer>
[ONLY the precise, minimal answer - no explanations, no "the answer is"]
</final_answer>
```
"""



def remove_null_keys(d):
    return dict(filter(lambda x: x[1] is not None, d.items()))


def convert_json_schema(Tool):
    required_param = [param['name'] for param in Tool.parameters if param.get('required', False)]
    properties = {}
    for param in Tool.parameters:
        properties[param['name']] = {
            "type": param['type'],
            "description": param['description']
        }
        if param['type'] == 'array':
            properties[param['name']]['items'] = {
                "type": param['array_type']
            }

    return {
        "type": "function",
        "function": {
            "name": Tool.name,
            "description": Tool.description.strip(),
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required_param
            }
        }
    }


def execute_function_call(function_call, **kwargs) -> str:
    function_name = function_call["name"]
    print("Current function name:")
    print("\033[32m" + function_name + "\033[0m")
    print("Current function arguments:")
    print("\033[33m" + function_call["arguments"] + "\033[0m")
    function_call["arguments"] = json.loads(function_call["arguments"])
    function_args = function_call["arguments"]

    if function_name in TOOL_MAP:
        function_args["params"] = function_args

        result = TOOL_MAP[function_name].call(function_args)
        return result

    else:
        return f"Error: Tool {function_name} not found"


def multi_turn_function_call(system_prompt: str, task_id, query: str, benchmark: str,
                             max_turns: int = 20) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    save_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    turn_count = 0

    client = openai.OpenAI(
        api_key=openai.api_key,
        base_url=openai.base_url
    )
    while turn_count < max_turns:
        retry = 0

        while retry < 3:
            try:


                response = client.chat.completions.create(
                    model="gpt-4.1-2025-04-14",
                    messages=messages,
                    tools=TOOLS_SCHEMA
                )


                assistant_message = response.choices[0].message
                messages.append(assistant_message)
                save_messages.append(assistant_message.model_dump())

                if assistant_message.tool_calls:
                    for tool_call in assistant_message.tool_calls:

                        tool_name = tool_call.function.name
                        tool_args = tool_call.function.arguments

                        function_result = execute_function_call(tool_call.function.model_dump())


                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": json.dumps(function_result, ensure_ascii=False)
                        })
                        save_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": json.dumps(function_result, ensure_ascii=False)
                        })

                    break
                
                else:

                    print(f"Answer at turn {turn_count}")

                    with open(f"results/result_{benchmark}.jsonl", "a") as f:
                        f.write(json.dumps(save_messages, ensure_ascii=False) + "\n")
                    return messages
            except Exception as e:
                if isinstance(e, bdb.BdbQuit):
                    raise e
                print(f'[AGENT] ID: {task_id} T: {turn_count} rty: {retry} {e}')
        if retry >= 3:
            break

        turn_count += 1


    return None

def run_query(task, benchmark):
    task_id = task["id"]
    query = task["question"]
    print("Current query:")
    print("\033[31m" + query + "\033[0m")
    system_prompt = SYSTEM_PROMPT.replace("{tool_descriptions}", tool_descriptions)
    print(f"tool_descriptions::::{tool_descriptions}")
    messages = multi_turn_function_call(system_prompt, task_id, query, benchmark)
    return messages


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, default="data/hotpotqa_distractor_val_queries_100.json")
    parser.add_argument("--kb_path", type=str, default="data/hotpotqa_distractor_val_kb_100.json")
    parser.add_argument("--benchmark", type=str, default="hotpotqa_distractor_val_100")
    args = parser.parse_args()
    args.index_path = os.path.join("./rag_index/", args.benchmark)

    TOOL_CLASS = [
        QueryRAGIndexTool(),
    ]

    TOOL_MAP = {tool.name: tool for tool in TOOL_CLASS}

    TOOLS_SCHEMA = []
    for tool in TOOL_CLASS:
        tool_schema = convert_json_schema(tool)
        TOOLS_SCHEMA.append(tool_schema)
    tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in TOOL_CLASS])

    ### Build Index from given knowledge base
    is_index_loaded = load_index(index_path=args.index_path)
    if not is_index_loaded:
        if args.data_path in ["data/hotpotqa_distractor_val_queries.json", "data/hotpotqa_distractor_val_queries_100.json",]:
            BuildRAGIndex(args.kb_path, need_chunk=False, index_path=args.index_path)
        else:
            BuildRAGIndex(args.kb_path, need_chunk=True, index_path=args.index_path)
    
    ### Run Query
    all_tasks = []
    if args.data_path in ["data/hotpotqa_distractor_val_queries.json", "data/hotpotqa_distractor_val_queries_100.json",]:
        with open(args.data_path, "r", encoding="utf-8") as f:
            queries = json.load(f)
        for query in queries:
            all_tasks.append({
                "id": query["id"],
                "question": query["question"],
            })
    else:
        pass

    for task in all_tasks:
        run_query(task, args.benchmark)

    # with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    #     futures = [executor.submit(run_query, task, data) for task in all_tasks]
    #     for future in concurrent.futures.as_completed(futures):
    #         message = future.result()

    print('\nAll tasks done!')
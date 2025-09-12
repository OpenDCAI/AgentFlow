import openai
import json
import os
import concurrent.futures
import argparse
import threading
from tqdm import tqdm
import bdb
from dotenv import load_dotenv, find_dotenv
load_dotenv(override=True)

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
                    # model="gpt-4.1-2025-04-14",
                    model=args.model_name,
                    messages=messages,
                    tools=TOOLS_SCHEMA
                )
                print(response)


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
                    return save_messages

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


def parse_final_answer(messages: list) -> str:
    """
    Parses the messages list to find the final assistant message
    and extracts the content from the <final_answer> tag.
    """
    if not messages:
        return ""

    last_message = messages[-1]
    if last_message.get("role") == "assistant":
        content = last_message.get("content", "")
        if content and "<final_answer>" in content:
            start_tag = "<final_answer>"
            end_tag = "</final_answer>"
            start_index = content.find(start_tag) + len(start_tag)
            end_index = content.find(end_tag)
            if start_index != -1 and end_index != -1:
                return content[start_index:end_index].strip()
        return content if content else ""
    
    return ""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--index_name", type=str, default="colbert_wiki2018")
    parser.add_argument("--benchmark", type=str, default="hotpotqa_distractor_val_100")
    parser.add_argument("--model_name", type=str, default="gpt-4.1-2025-04-14")
    parser.add_argument("--max_workers", type=int, default=20, help="Maximum number of threads for concurrent processing.")
    args = parser.parse_args()

    # gpt4o-mini
    # python run_rag.py --index_name colbert_wiki2018 --benchmark 2wiki_val --model_name gpt-4o-mini
    # python run_rag.py --index_name colbert_wiki2023 --benchmark 2wiki_val --model_name gpt-4o-mini

    # python run_rag.py --index_name colbert_wiki2018 --benchmark hotpotqa_distractor_val --model_name gpt-4o-mini
    # python run_rag.py --index_name colbert_wiki2018 --benchmark hotpotqa_fullwiki_val --model_name gpt-4o-mini

    # python run_rag.py --index_name colbert_wiki2023 --benchmark hotpotqa_distractor_val --model_name gpt-4o-mini
    # python run_rag.py --index_name colbert_wiki2023 --benchmark hotpotqa_fullwiki_val --model_name gpt-4o-mini

    # gpt-4.1-2025-04-14
    # python run_rag.py --index_name colbert_wiki2018 --benchmark 2wiki_val --model_name gpt-4.1-2025-04-14
    # python run_rag.py --index_name colbert_wiki2023 --benchmark 2wiki_val --model_name gpt-4.1-2025-04-14

    # python run_rag.py --index_name colbert_wiki2018 --benchmark hotpotqa_distractor_val --model_name gpt-4.1-2025-04-14
    # python run_rag.py --index_name colbert_wiki2018 --benchmark hotpotqa_fullwiki_val --model_name gpt-4.1-2025-04-14

    # python run_rag.py --index_name colbert_wiki2023 --benchmark hotpotqa_distractor_val --model_name gpt-4.1-2025-04-14
    # python run_rag.py --index_name colbert_wiki2023 --benchmark hotpotqa_fullwiki_val --model_name gpt-4.1-2025-04-14


    if args.benchmark in ["hotpotqa_distractor_val_100", "hotpotqa_fullwiki_val_100",  "2wiki_val_100", "2wiki_test_100", ]:
        base, number_part = args.benchmark.rsplit('_', 1)
        new_string = f"{base}_queries_{number_part}"
        args.data_path = os.path.join("data", new_string + ".json")
    elif args.benchmark in ["hotpotqa_distractor_val", "hotpotqa_fullwiki_val", "2wiki_val", "2wiki_test", ]:
        args.data_path = os.path.join("data", args.benchmark + "_queries.json")

    if args.index_name == "colbert_wiki2018":
        args.index_path = "/mnt/public/data/lh/ygc/agentflow/RAGLAB/data/retrieval/colbertv2.0_embedding/wiki2018"
    elif args.index_name == "colbert_wiki2023":
        args.index_path = "/mnt/public/data/lh/ygc/agentflow/RAGLAB/data/retrieval/colbertv2.0_embedding/wiki2023"
    else:
        raise ValueError(f"Unknown index name: {args.index_name}")

    TOOL_CLASS = [
        QueryColbertIndexTool(index_path=args.index_path)
    ]

    TOOL_MAP = {tool.name: tool for tool in TOOL_CLASS}

    TOOLS_SCHEMA = []
    tool_descriptions = ""
    for tool in TOOL_CLASS:
        tool_schema = convert_json_schema(tool)
        TOOLS_SCHEMA.append(tool_schema)
    tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in TOOL_CLASS])

    ### Run Query
    all_tasks = []
    with open(args.data_path, "r", encoding="utf-8") as f:
        queries = json.load(f)
    for query in queries:
        all_tasks.append({
            "id": query["id"],
            "question": query["question"],
        })

    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{args.benchmark}_{args.model_name}_{args.index_name}.jsonl")
    
    file_lock = threading.Lock()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        future_to_task = {executor.submit(run_query, task, args.benchmark): task for task in all_tasks}
        
        for future in tqdm(concurrent.futures.as_completed(future_to_task), total=len(all_tasks), desc="Processing tasks"):
            task = future_to_task[future]
            try:
                messages = future.result()
                final_answer = parse_final_answer(messages)
                
                result_data = {
                    "task_id": task["id"],
                    "answer": final_answer
                }
                
                with file_lock:
                    with open(output_file, "a", encoding="utf-8") as f:
                        f.write(json.dumps(result_data, ensure_ascii=False) + "\n")

            except Exception as exc:
                print(f"Task {task['id']} generated an exception: {exc}")

    print(f'\nAll tasks done! Results saved to {output_file}')
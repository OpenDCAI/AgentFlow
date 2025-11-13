import json
import os
from typing import List, Dict, Any, Optional
from datasets import load_dataset


def convert_mmlongbench_to_agentflow(
    input_file_path: Optional[str] = None,
    output_file_path: str = "mmlongbench_demo.jsonl",
    dataset_name: Optional[str] = None,
    split: str = "test",
    use_doc_id_as_id: bool = True
) -> List[Dict[str, Any]]:
    """
    Convert MMLongBench dataset to AgentFlow format (JSONL).
    
    MMLongBench format:
    {
        "doc_id": "Independents-Report.pdf",
        "doc_type": "Research report / Introduction",
        "question": "...",
        "answer": "...",
        "evidence_pages": "[3, 5]",
        "evidence_sources": "['Pure-text (Plain-text)']",
        "answer_format": "Float",
    }
    
    AgentFlow format (JSONL) - preserves all original fields:
    {
        "id": "Independents-Report.pdf",
        "question": "in [Independents-Report.pdf] document, ...",
        "answer": "...",
        "doc_type": "Research report / Introduction",
        "evidence_pages": "[3, 5]",
        "evidence_sources": "['Pure-text (Plain-text)']",
        "answer_format": "Float",
        ...
    }
    
    Note: The question field will be prefixed with "in [id] document, " to indicate
    which document the question refers to.
    
    All fields except doc_id (which becomes id) are preserved. AgentFlow's
    Benchmark class will automatically store extra fields in the metadata.
    
    Args:
        input_file_path: Path to local JSON/JSONL file containing MMLongBench data.
                        If None, will try to load from HuggingFace.
        output_file_path: Path to save the converted JSONL file.
        dataset_name: HuggingFace dataset name (e.g., "THUDM/MMLongBench").
                     Only used if input_file_path is None.
        split: Dataset split to load (e.g., "test", "validation").
        use_doc_id_as_id: If True, use doc_id as the id. If False, use index.
    
    Returns:
        List of converted items in AgentFlow format with all original fields preserved.
    """
    
    # Load data
    if input_file_path:
        print(f"Loading MMLongBench data from local file: {input_file_path}")
        data = load_from_local_file(input_file_path)
    elif dataset_name:
        print(f"Loading MMLongBench data from HuggingFace: {dataset_name}")
        dataset = load_dataset(dataset_name, split=split)
        data = [item for item in dataset]
    else:
        raise ValueError("Either input_file_path or dataset_name must be provided")
    
    print(f"Loaded {len(data)} items from MMLongBench")
    
    # Convert to AgentFlow format
    converted_items = []
    for idx, item in enumerate(data):
        # Extract required fields
        if use_doc_id_as_id:
            item_id = item.get("doc_id", f"mmlongbench_{idx}")
        else:
            item_id = f"mmlongbench_{idx}"
        
        question = item.get("question", "")
        # Add "in [id] document" prefix to question
        question = f"in [{item_id}] document, {question}"
        answer = item.get("answer", "")
        
        # Create AgentFlow format item with all original fields preserved
        # AgentFlow's Benchmark class will automatically put extra fields into metadata
        agentflow_item = {
            "id": item_id,
            "question": question,
            "answer": answer
        }
        
        # Preserve all other fields from MMLongBench
        for key, value in item.items():
            if key not in ["doc_id"]:  # doc_id is already used as id
                if key not in agentflow_item:  # Don't overwrite id, question, answer
                    agentflow_item[key] = value
        
        converted_items.append(agentflow_item)
    
    # Save to JSONL file
    print(f"Saving converted data to {os.path.abspath(output_file_path)}...")
    with open(output_file_path, "w", encoding="utf-8") as f:
        for item in converted_items:
            json_record = json.dumps(item, ensure_ascii=False)
            f.write(json_record + '\n')
    
    print(f"Successfully converted {len(converted_items)} items to AgentFlow format")
    print(f"Output saved to: {os.path.abspath(output_file_path)}")
    
    return converted_items


def load_from_local_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Load MMLongBench data from a local JSON or JSONL file.
    
    Args:
        file_path: Path to the input file.
    
    Returns:
        List of data items.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    data = []
    
    if file_path.endswith('.jsonl'):
        # Load JSONL file
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    data.append(item)
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON on line {line_num}: {e}")
                    continue
    elif file_path.endswith('.json'):
        # Load JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
            if isinstance(content, list):
                data = content
            elif isinstance(content, dict):
                # Check if it's a structured format
                if 'items' in content:
                    data = content['items']
                elif 'data' in content:
                    data = content['data']
                else:
                    # Single item
                    data = [content]
            else:
                raise ValueError(f"Unexpected JSON structure in {file_path}")
    else:
        raise ValueError(f"Unsupported file format: {file_path}. Expected .json or .jsonl")
    
    return data


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert MMLongBench dataset to AgentFlow format")
    parser.add_argument(
        "--input",
        type=str,
        help="Path to local MMLongBench JSON/JSONL file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="mmlongbench_demo.jsonl",
        help="Output path for converted JSONL file (default: mmlongbench_demo.jsonl)"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        help="HuggingFace dataset name (e.g., 'THUDM/MMLongBench')"
    )
    parser.add_argument(
        "--split",
        type=str,
        default="test",
        help="Dataset split to load (default: test)"
    )
    parser.add_argument(
        "--use-index-as-id",
        action="store_true",
        help="Use index as id instead of doc_id"
    )
    
    args = parser.parse_args()
    
    if not args.input and not args.dataset:
        parser.error("Either --input or --dataset must be provided")
    
    convert_mmlongbench_to_agentflow(
        input_file_path=args.input,
        output_file_path=args.output,
        dataset_name=args.dataset,
        split=args.split,
        use_doc_id_as_id=not args.use_index_as_id
    )


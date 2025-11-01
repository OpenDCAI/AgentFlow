import json
import os
from typing import List, Dict, Any, Tuple
from datasets import load_dataset

def prepare_hotpotqa(
    output_kb_file_path: str = "hotpotqa_fullwiki_val_kb.json",
    output_query_file_path: str = "hotpotqa_val.jsonl"
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Downloads the HotpotQA validation set and processes it into two files:
    1. A knowledge base (corpus) in JSON format.
    2. A set of queries and answers in JSONL format.

    This function is designed to prepare the dataset for retrieval-augmented
    generation (RAG) tasks or other NLP models that require a separate
    knowledge source and a set of questions.

    Args:
        output_kb_file_path (str): The file path to save the knowledge base JSON file.
        output_query_file_path (str): The file path to save the query-answer JSONL file.

    Returns:
        Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]: A tuple containing the
        corpus data and the query-answer data.
    """

    print("Loading HotpotQA dataset...")
    dataset = load_dataset("hotpotqa/hotpot_qa", "fullwiki", split="validation", cache_dir='/gpfs/share/home/2301110044/zwt/ygc/hf_cache')
    print("Dataset loaded successfully.")

    corpus: List[Dict[str, Any]] = []
    query_answer: List[Dict[str, Any]] = []

    for example in dataset:
        for title, sentences_list in zip(example["context"]["title"], example["context"]["sentences"]):
            for i, sentence in enumerate(sentences_list):
                corpus.append({
                    "text": sentence,
                    "example_id": example["id"],
                    "title": title,
                    "sentence_id": i
                })
        query_answer.append({
            "id": example["id"],
            "question": example["question"],
            "answer": example["answer"],
        })

    print(f"Extracted {len(corpus)} sentences for the corpus.")
    print(f"Extracted {len(query_answer)} query-answer pairs.")

    print(f"Saving corpus to {os.path.abspath(output_kb_file_path)}...")
    with open(output_kb_file_path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=4)
    print("Corpus saved successfully.")

    print(f"Saving query-answer pairs to {os.path.abspath(output_query_file_path)}...")
    with open(output_query_file_path, "w", encoding="utf-8") as f:
        for entry in query_answer:
            json_record = json.dumps(entry, ensure_ascii=False)
            f.write(json_record + '\n')
    print("Query-answer pairs saved successfully.")

    return corpus, query_answer

if __name__ == "__main__":
    corpus_data, query_answer_data = prepare_hotpotqa()
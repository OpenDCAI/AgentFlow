#!/usr/bin/env python3
"""Test script to see how benchmark loads OSWorld data."""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from benchmark import create_benchmark

def main():
    # Load OSWorld benchmark
    data_path = "/home/a1/sdb/zhy/GUIAgent_zhy/AgentFlow/src/data/osworld_examples.jsonl"

    print("="*80)
    print("Loading OSWorld Benchmark")
    print("="*80)

    benchmark = create_benchmark(
        data_path=data_path,
        name="OSWorld Examples",
        description="OSWorld desktop automation examples"
    )

    print(f"\nBenchmark Name: {benchmark.name}")
    print(f"Description: {benchmark.description}")
    print(f"Total Items: {len(benchmark.items)}")
    print()

    # Show structure of first item
    if benchmark.items:
        print("="*80)
        print("First Item Structure:")
        print("="*80)
        item = benchmark.items[0]

        print(f"\nBenchmarkItem fields:")
        print(f"  - id: {item.id}")
        print(f"  - question: {item.question[:100]}...")
        print(f"  - answer: {item.answer}")
        print(f"  - metadata keys: {list(item.metadata.keys()) if item.metadata else None}")

        if item.metadata:
            print(f"\n  Metadata content:")
            for key, value in item.metadata.items():
                if isinstance(value, (dict, list)):
                    print(f"    {key}: {type(value).__name__} (len={len(value) if hasattr(value, '__len__') else 'N/A'})")
                else:
                    print(f"    {key}: {value}")

        print("\n" + "="*80)
        print("Complete First Item (formatted JSON):")
        print("="*80)

        item_dict = {
            "id": item.id,
            "question": item.question,
            "answer": item.answer,
            "metadata": item.metadata
        }
        print(json.dumps(item_dict, indent=2, ensure_ascii=False))

        # Show all items summary
        print("\n" + "="*80)
        print("All Items Summary:")
        print("="*80)
        for idx, item in enumerate(benchmark.items, 1):
            print(f"\n{idx}. ID: {item.id}")
            print(f"   Question: {item.question[:80]}...")
            print(f"   Answer: {item.answer if item.answer else '(empty)'}")
            print(f"   Metadata keys: {list(item.metadata.keys())[:5]}...")

if __name__ == "__main__":
    main()

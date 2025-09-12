import sys
import ujson as json
import re
import string
from collections import Counter
import argparse

def normalize_answer(s):

    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)

    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def f1_score(prediction, ground_truth):
    normalized_prediction = normalize_answer(prediction)
    normalized_ground_truth = normalize_answer(ground_truth)

    ZERO_METRIC = (0, 0, 0)

    if normalized_prediction in ['yes', 'no', 'noanswer'] and normalized_prediction != normalized_ground_truth:
        return ZERO_METRIC
    if normalized_ground_truth in ['yes', 'no', 'noanswer'] and normalized_prediction != normalized_ground_truth:
        return ZERO_METRIC

    prediction_tokens = normalized_prediction.split()
    ground_truth_tokens = normalized_ground_truth.split()
    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return ZERO_METRIC
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1, precision, recall


def exact_match_score(prediction, ground_truth):
    return (normalize_answer(prediction) == normalize_answer(ground_truth))

def update_answer(metrics, prediction, gold):
    em = exact_match_score(prediction, gold)
    f1, prec, recall = f1_score(prediction, gold)
    metrics['em'] += float(em)
    metrics['f1'] += f1
    metrics['prec'] += prec
    metrics['recall'] += recall


def eval(prediction_file, gold_file):
    predictions = {}
    try:
        with open(prediction_file, 'r', encoding='utf-8') as f:
            for line in f:
                pred_item = json.loads(line)
                predictions[pred_item['task_id']] = pred_item['answer']
    except FileNotFoundError:
        print(f"错误: 预测文件未找到 -> {prediction_file}")
        sys.exit(1)

    try:
        with open(gold_file, 'r', encoding='utf-8') as f:
            gold_data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 标准答案文件未找到 -> {gold_file}")
        sys.exit(1)

    metrics = {'em': 0, 'f1': 0, 'prec': 0, 'recall': 0}

    missing_predictions = 0
    for dp in gold_data:
        cur_id = dp['id']
        
        if cur_id not in predictions:
            missing_predictions += 1
            continue
        
        if 'answer' in dp and dp['answer']:
            update_answer(metrics, predictions[cur_id], dp['answer'])

    total_samples  = len(gold_data)
    for k in metrics.keys():
        metrics[k] /= total_samples 

    print(metrics)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred_file_path", type=str, default="results/answers_hotpotqa_distractor_val_100.jsonl")
    parser.add_argument("--gt_file_path", type=str, default="data/hotpotqa_distractor_val_queries_100.json")
    args = parser.parse_args()

    # python eval/eval_2wiki.py --pred_file_path results/2wiki_val_gpt-4o-mini_colbert_wiki2018.jsonl --gt_file_path data/2wiki_val_queries.json
    # python eval/eval_2wiki.py --pred_file_path results/2wiki_val_gpt-4o-mini_colbert_wiki2023.jsonl --gt_file_path data/2wiki_val_queries.json

    eval(args.pred_file_path, args.gt_file_path)
#!/usr/bin/env python3
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\haya1\brain\20_Projects\compliance-quiz-v2\data\questions.json', encoding='utf-8') as f:
    db = json.load(f)

for s in db['subjects']:
    if s['id'] != '001':
        continue
    for q in s['questions'][:10]:
        if not q['choices'] or q['answer'] is None:
            continue
        ans_idx = q['answer'] - 1
        lengths = [len(c) for c in q['choices']]
        correct_len = lengths[ans_idx]
        others = [lengths[i] for i in range(len(lengths)) if i != ans_idx]
        avg_others = sum(others) / len(others) if others else 0
        print(f"第{q['num']}問（正解:{correct_len}字 他平均:{round(avg_others,1)}字）")
        for i, c in enumerate(q['choices']):
            mark = "★正解" if i + 1 == q['answer'] else "    "
            print(f"  {mark} {i+1}: {c}")
        print()
    break

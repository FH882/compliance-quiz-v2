#!/usr/bin/env python3
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\haya1\brain\20_Projects\compliance-quiz-v2\data\questions.json', encoding='utf-8') as f:
    db = json.load(f)

# 修正後の偏り状況
still_biased = 0
fixed_ok = 0
for s in db['subjects']:
    for q in s['questions']:
        if not q['choices'] or q['answer'] is None or len(q['choices']) < 4:
            continue
        ans_idx = q['answer'] - 1
        lengths = [len(c) for c in q['choices']]
        correct_len = lengths[ans_idx]
        others = [lengths[i] for i in range(len(lengths)) if i != ans_idx]
        avg_others = sum(others) / len(others)
        if correct_len > avg_others * 1.5 and correct_len - avg_others > 20:
            still_biased += 1
        else:
            fixed_ok += 1

total = sum(len(s['questions']) for s in db['subjects'])
print(f"全{total}問中")
print(f"  偏りなし（修正済み含む）: {fixed_ok}問")
print(f"  まだ偏りあり: {still_biased}問")
print()

# サンプル確認 - 第2問（以前問題だった問題）
print("=== 修正後サンプル（001テキスト 第1〜10問）===")
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
        avg_others = sum(others)/len(others)
        print(f"第{q['num']}問（正解:{correct_len}字 他平均:{round(avg_others,1)}字）")
        for i, c in enumerate(q['choices']):
            mark = "★正解" if i+1==q['answer'] else "    "
            print(f"  {mark} {i+1}: {c}")
        print()

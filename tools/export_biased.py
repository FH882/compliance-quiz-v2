#!/usr/bin/env python3
"""偏り問題を科目別にエクスポートし、エージェント処理用JSONを生成する"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\haya1\brain\20_Projects\compliance-quiz-v2\data\questions.json', encoding='utf-8') as f:
    db = json.load(f)

BIAS_RATIO = 1.5
BIAS_MIN   = 20

def is_biased(q):
    if not q['choices'] or q['answer'] is None or len(q['choices']) < 4:
        return False
    idx = q['answer'] - 1
    if idx >= len(q['choices']):
        return False
    ls = [len(c) for c in q['choices']]
    correct = ls[idx]
    others = [ls[i] for i in range(len(ls)) if i != idx]
    avg = sum(others)/len(others)
    return correct > avg * BIAS_RATIO and correct - avg > BIAS_MIN

# 科目別に集計してエクスポート
export = []
for s in db['subjects']:
    biased_qs = [q for q in s['questions'] if is_biased(q)]
    if not biased_qs:
        continue
    export.append({'id': s['id'], 'name': s['name'], 'questions': biased_qs})
    print(f"[{s['id']}] {s['name'][:30]}: {len(biased_qs)}問")

print(f"\n合計: {sum(len(s['questions']) for s in export)}問 / {len(export)}科目")

out_path = r'C:\Users\haya1\brain\20_Projects\compliance-quiz-v2\tools\biased_questions.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(export, f, ensure_ascii=False, indent=2)
print(f"出力: {out_path}")

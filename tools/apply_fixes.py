#!/usr/bin/env python3
"""8グループの修正結果を統合してquestions.jsonに適用する"""
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

TOOLS_DIR = r'C:\Users\haya1\brain\20_Projects\compliance-quiz-v2\tools'
JSON_PATH = r'C:\Users\haya1\brain\20_Projects\compliance-quiz-v2\data\questions.json'

# 1. 全グループの修正を統合
all_fixes = {}  # (subject_id, num) -> fixed_answer
total_loaded = 0

for i in range(1, 9):
    path = os.path.join(TOOLS_DIR, f'fixes_group{i}.json')
    if not os.path.exists(path):
        print(f"警告: fixes_group{i}.json が見つかりません")
        continue
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    fixes = data.get('fixes', [])
    for fix in fixes:
        key = (fix['subject_id'], fix['num'])
        all_fixes[key] = fix['fixed_answer']
        total_loaded += 1
    print(f"グループ{i}: {len(fixes)}件 読み込み")

print(f"\n合計修正件数: {total_loaded}件")

# 2. questions.json に適用
with open(JSON_PATH, encoding='utf-8') as f:
    db = json.load(f)

applied = 0
not_found = []

for s in db['subjects']:
    for q in s['questions']:
        key = (s['id'], q['num'])
        if key in all_fixes:
            ans_idx = q['answer'] - 1
            if 0 <= ans_idx < len(q['choices']):
                q['choices'][ans_idx] = all_fixes[key]
                applied += 1

print(f"適用済み: {applied}件")

# 3. 保存
with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)
print(f"保存完了: {JSON_PATH}")

# 4. 偏り状況の最終確認
BIAS_RATIO = 1.5
BIAS_MIN   = 20

still_biased = 0
ok = 0
for s in db['subjects']:
    for q in s['questions']:
        if not q['choices'] or q['answer'] is None or len(q['choices']) < 4:
            continue
        idx = q['answer'] - 1
        if idx >= len(q['choices']):
            continue
        ls = [len(c) for c in q['choices']]
        correct = ls[idx]
        others = [ls[i] for i in range(len(ls)) if i != idx]
        avg = sum(others)/len(others)
        if correct > avg * BIAS_RATIO and correct - avg > BIAS_MIN:
            still_biased += 1
        else:
            ok += 1

total = ok + still_biased
print(f"\n=== 最終結果 ===")
print(f"全{total}問中")
print(f"  偏りなし: {ok}問 ({round(ok/total*100)}%)")
print(f"  偏りあり: {still_biased}問 ({round(still_biased/total*100)}%)")

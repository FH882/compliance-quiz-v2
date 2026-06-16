#!/usr/bin/env python3
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\haya1\brain\20_Projects\compliance-quiz-v2\data\questions.json', encoding='utf-8') as f:
    db = json.load(f)

# 各科目から1問ずつ修正後のサンプルを表示（偏りがあったもの）
print("=== 修正後サンプル ===\n")
shown = set()
for s in db['subjects']:
    if s['id'] in shown or s['id'] not in ['001','013','037','039','D02']:
        continue
    shown.add(s['id'])
    for q in s['questions'][:15]:
        if not q['choices'] or q['answer'] is None or len(q['choices']) < 4:
            continue
        idx = q['answer'] - 1
        ls = [len(c) for c in q['choices']]
        correct = ls[idx]
        others = [ls[i] for i in range(len(ls)) if i != idx]
        avg = sum(others)/len(others)
        # 修正済みと思われる問題（元は偏っていたはずの問題）
        if 0.7 <= correct / max(avg, 1) <= 1.8:
            print(f"[{s['id']}] 第{q['num']}問 （正解:{correct}字 他平均:{round(avg,1)}字）")
            for i, c in enumerate(q['choices']):
                mark = "★正解" if i+1==q['answer'] else "    "
                print(f"  {mark} {i+1}: {c}")
            print()
            break

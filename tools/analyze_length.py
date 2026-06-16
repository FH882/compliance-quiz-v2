#!/usr/bin/env python3
"""正解の文字数が他の選択肢より著しく長い問題を抽出する"""
import json

with open(r'C:\Users\haya1\brain\20_Projects\compliance-quiz-v2\data\questions.json', encoding='utf-8') as f:
    db = json.load(f)

biased = []
for s in db['subjects']:
    for q in s['questions']:
        if not q['choices'] or q['answer'] is None:
            continue
        ans_idx = q['answer'] - 1
        if ans_idx >= len(q['choices']):
            continue
        lengths = [len(c) for c in q['choices']]
        correct_len = lengths[ans_idx]
        others = [lengths[i] for i in range(len(lengths)) if i != ans_idx]
        avg_others = sum(others) / len(others) if others else 0
        max_others = max(others) if others else 0
        # 正解が他の平均の1.5倍以上 かつ 差が20文字以上
        if avg_others > 0 and correct_len > avg_others * 1.5 and correct_len - avg_others > 20:
            biased.append({
                'subject': s['name'],
                'subject_id': s['id'],
                'num': q['num'],
                'correct_len': correct_len,
                'avg_others': round(avg_others, 1),
                'ratio': round(correct_len / avg_others, 2),
                'q': q['question'][:50],
                'choices': q['choices'],
                'answer': q['answer']
            })

biased.sort(key=lambda x: -x['ratio'])
print(f"偏りのある問題数: {len(biased)}")
print(f"全問題数: {sum(len(s['questions']) for s in db['subjects'])}")
print()
for b in biased[:20]:
    print(f"[{b['subject_id']}] 第{b['num']}問 正解:{b['correct_len']}字 他平均:{b['avg_others']}字 比:{b['ratio']}倍")
    for i, c in enumerate(b['choices']):
        mark = "★" if i + 1 == b['answer'] else "  "
        print(f"  {mark}{i+1}: {c[:80]}")
    print()

#!/usr/bin/env python3
"""不完全な語尾（ため・つつ等）で終わる正解選択肢を修正する"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

JSON_PATH = r'C:\Users\haya1\brain\20_Projects\compliance-quiz-v2\data\questions.json'

with open(JSON_PATH, encoding='utf-8') as f:
    db = json.load(f)

def fix_incomplete(text):
    """不完全語尾を完結した形に変換する"""
    t = text.strip()

    # 「〜するため」→「〜すること」系
    # Verb（終止形）+ ため → Verb + こと
    t = re.sub(r'(する|した|ある|ない|なる|得る|受ける|生じる|生じ得る|とする|できる|'
               r'いる|おける|認める|確保する|防ぐ|示す|補足する|把握する|'
               r'資する|役立てる|知り得る|変化し得る|高める|なり得る)ため$',
               lambda m: m.group(1) + 'こと', t)

    # 「〜があるため」→「〜があること」
    t = re.sub(r'(がある|おそれがある|可能性がある|蓋然性が高い|含まれる|影響を及ぼし得る)ため$',
               lambda m: m.group(1) + 'こと', t)

    # 「〜なるため」「〜となるため」→「〜なること」
    t = re.sub(r'(なる|となる|生じ得る|されるおそれがある)ため$',
               lambda m: m.group(1) + 'こと', t)

    # まだ「ため」で終わっていれば汎用変換
    if t.endswith('ため'):
        t = t[:-2] + 'こと'

    # 「つつ」で終わる場合
    if t.endswith('つつ'):
        t = t[:-2] + 'ながら対応する'

    # 「ながら」で終わる場合
    if t.endswith('ながら'):
        t = t + '実施する'

    # 「受け」で終わる場合（中止形）
    if t.endswith('受け') and not t.endswith('お客さまから受け'):
        t = t + 'ること'

    # 「踏まえ」で終わる場合
    if t.endswith('踏まえ'):
        t = t + 'て対応する'

    # 「含め」で終わる場合
    if t.endswith('含め'):
        t = t + 'て管理する'

    return t


fixed = []
for s in db['subjects']:
    for q in s['questions']:
        if not q['choices'] or q['answer'] is None:
            continue
        idx = q['answer'] - 1
        if idx >= len(q['choices']):
            continue
        original = q['choices'][idx]
        if re.search(r'ため$|つつ$|ながら$|あたり$|受け$|踏まえ$|含め$|立場で$', original):
            fixed_text = fix_incomplete(original)
            if fixed_text != original:
                fixed.append({
                    'id': s['id'], 'num': q['num'],
                    'before': original, 'after': fixed_text
                })
                q['choices'][idx] = fixed_text

with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(f"修正件数: {len(fixed)}")
for f_ in fixed:
    print(f"  [{f_['id']}] 第{f_['num']}問")
    print(f"    前: {f_['before']}")
    print(f"    後: {f_['after']}")
    print()

#!/usr/bin/env python3
"""
選択肢の長さ偏りを修正するスクリプト。
正解の選択肢が他より著しく長い問題について、正解文章を簡潔化する。
修正済みWordファイルは「元ファイル名_Ver.2.0.0.docx」として別保存する。
"""
import json, re, sys, os, zipfile, shutil
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

SOURCE_DIR = r'C:\Users\haya1\OneDrive\ドキュメント\仕事関係\1　法令等遵守責任者\AI\問題、解答・解説(テーマ別)'
DIFF_DIR   = r'C:\Users\haya1\OneDrive\ドキュメント\仕事関係\1　法令等遵守責任者\AI\問題、解答・解説(難易度別テスト)'
JSON_IN    = r'C:\Users\haya1\brain\20_Projects\compliance-quiz-v2\data\questions.json'
JSON_OUT   = r'C:\Users\haya1\brain\20_Projects\compliance-quiz-v2\data\questions.json'

BIAS_RATIO = 1.5
BIAS_MIN   = 20


# ── 文法的完結判定 ────────────────────────────────────────────

# 文として完結する語尾（動詞終止形・体言止め等）
COMPLETE_RE = re.compile(
    r'(する|した|ある|ない|いる|いない|なる|なった|できる|できない|'
    r'行う|行った|用いる|担う|負う|持つ|受ける|与える|'
    r'こと|もの|ため(?!に)|上|際|場合|'
    r'である|でない|ではない|ではなく|'
    r'ている|ていない|てある|ていた|てきた|てきている|'
    r'べき|べきである|ものである|必要がある|義務がある|義務がない|'
    r'異なる|関する|該当する|含まれる|認められる|求められる|'
    r'など|等|のみ|以外|以内|以上|以下|まで|から|'
    r'するもの|したもの|あるもの|ないもの)$'
)

# 文として未完結の語尾（接続助詞・中止形・活用途中等）
INCOMPLETE_RE = re.compile(
    r'(受け|踏まえ|含め|除き|除い|合わせ|組み|行い|対し|基づ|応じ|'
    r'立場で|観点で|前提で|方針で|形で|形と|場合に|必要に|重要に|'
    r'するため|したため|あるため|ないため|'   # 「〜するため」は目的節で未完結
    r'しつつ|つつ|ながら|として|において|にあたり|にあたって|'
    r'[、，]$|[て]$|[で]$|[を]$|[に]$|[が]$|[は]$|[の]$)$'
)


def is_complete_ending(text):
    text = text.strip()
    if not text:
        return False
    if INCOMPLETE_RE.search(text):
        return False
    if COMPLETE_RE.search(text):
        return True
    # 句点・括弧閉じで終わる場合も完結とみなす
    if text[-1] in '。）」』':
        return True
    return False


# ── 正解テキスト簡潔化 ────────────────────────────────────────

def trim_answer(text, max_target):
    """正解を簡潔化。文法的に完結した切断点のみを使う。
    受け入れ条件: 元テキストより10%以上短く、かつ max_target*1.5 以内。
    """
    if len(text) <= max_target:
        return text

    accept_max = max(max_target * 1.5, max_target + 15)
    accept_min = max_target * 0.4

    def accept(c):
        return (is_complete_ending(c)
                and accept_min <= len(c) <= accept_max
                and len(c) < len(text) * 0.9)

    result = text

    # 1. 「、また〜」「。また〜」を削除
    for pat in [r'、また[、。]?.*$', r'。また.*$']:
        m = re.search(pat, result)
        if m and m.start() > accept_min:
            c = result[:m.start()]
            if accept(c):
                return c

    # 2. 「なお〜」「さらに〜」を削除
    for pat in [r'[。、]なお[、，].*$', r'、さらに.*$']:
        m = re.search(pat, result)
        if m and m.start() > accept_min:
            c = result[:m.start()]
            if accept(c):
                return c

    # 3. 「こと、〜後続」で「こと」で切る
    m = re.search(r'こと[、。].*$', result)
    if m:
        c = result[:m.start() + 2]
        if accept(c):
            return c

    # 4. 「もの、〜後続」で「もの」で切る
    m = re.search(r'もの[、。].*$', result)
    if m:
        c = result[:m.start() + 2]
        if accept(c):
            return c

    # 5. 語尾の言い換えで短縮
    repls = [
        (r'のが一般的である$', 'ことが多い'),
        (r'のが通例である$', 'ことが多い'),
        (r'とされている$', 'とされる'),
        (r'ものとされている$', 'ものとされる'),
        (r'ことが求められている$', 'ことが必要である'),
        (r'ことが必要とされる$', 'ことが必要である'),
        (r'ことが重要とされる$', 'ことが重要である'),
    ]
    for pat, repl in repls:
        c = re.sub(pat, repl, result)
        if c != result and accept(c):
            return c

    # 6. 箇条書き列挙を2項目で切る
    m = re.search(r'[①②③④⑤ア-エ][．.].{5,}?[①②③④⑤ア-エ][．.]', result)
    if m:
        # 2番目の記号の直前で切る
        cut = result.rfind(m.group(0)[m.group(0).index('）') if '）' in m.group(0) else -5:])
        c = result[:m.end() - len(re.search(r'[①②③④⑤ア-エ][．.].+$', m.group(0)).group())]
        if c and accept(c):
            return c

    # 7. 句点で切る（複数ある場合は最初の。）
    for m in re.finditer(r'。', result):
        c = result[:m.start() + 1]
        if accept(c):
            return c

    # 8. 読点で切る（is_complete_endingが通る場合のみ）
    for m in reversed(list(re.finditer(r'[、，]', result))):
        c = result[:m.start()]
        if len(c) < accept_min:
            break
        if accept(c):
            return c

    # 修正不可：そのまま
    return result


# ── 偏り判定 ─────────────────────────────────────────────────

def is_biased(q):
    if not q['choices'] or q['answer'] is None or len(q['choices']) < 4:
        return False
    ans_idx = q['answer'] - 1
    if ans_idx >= len(q['choices']):
        return False
    ls = [len(c) for c in q['choices']]
    correct = ls[ans_idx]
    others = [ls[i] for i in range(len(ls)) if i != ans_idx]
    avg = sum(others) / len(others)
    return correct > avg * BIAS_RATIO and correct - avg > BIAS_MIN


def max_other_len(q):
    ans_idx = q['answer'] - 1
    ls = [len(c) for c in q['choices']]
    return max(ls[i] for i in range(len(ls)) if i != ans_idx)


# ── JSON修正 ─────────────────────────────────────────────────

with open(JSON_IN, encoding='utf-8') as f:
    db = json.load(f)

fixed_count = 0
changes = []

for s in db['subjects']:
    for q in s['questions']:
        if not is_biased(q):
            continue
        ans_idx = q['answer'] - 1
        original = q['choices'][ans_idx]
        target = max_other_len(q)
        fixed = trim_answer(original, target)
        if fixed != original:
            changes.append({
                'subject_id': s['id'],
                'num': q['num'],
                'original': original,
                'fixed': fixed
            })
            q['choices'][ans_idx] = fixed
            fixed_count += 1

with open(JSON_OUT, 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(f"JSON修正完了: {fixed_count}問 修正")


# ── Wordファイル修正 ──────────────────────────────────────────

def fix_docx(src_path, dst_path, text_replacements):
    if not text_replacements or not os.path.exists(src_path):
        return 0
    shutil.copy2(src_path, dst_path)
    with zipfile.ZipFile(dst_path, 'r') as zin:
        contents = {n: zin.read(n) for n in zin.namelist()}
    xml = contents['word/document.xml'].decode('utf-8')
    replaced = 0
    for orig, new in text_replacements:
        if orig in xml:
            xml = xml.replace(orig, new, 1)
            replaced += 1
    contents['word/document.xml'] = xml.encode('utf-8')
    with zipfile.ZipFile(dst_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, data in contents.items():
            zout.writestr(name, data)
    return replaced


# subject_idごとに修正リストを集約
files = sorted(f for f in os.listdir(SOURCE_DIR)
               if f.endswith('.docx') and '_Ver.' not in f)
q_files = {f[:3]: f for f in files if int(f[:3]) % 2 == 1}

changes_by_subject = defaultdict(list)
for c in changes:
    changes_by_subject[c['subject_id']].append((c['original'], c['fixed']))

docx_fixed = 0
for sid, replacements in changes_by_subject.items():
    if sid.startswith('D'):
        diff_map = {'D01': '低難易度_問題.docx', 'D02': '中難易度_問題.docx', 'D03': '高難易度_問題.docx'}
        fname = diff_map.get(sid)
        if not fname:
            continue
        src = os.path.join(DIFF_DIR, fname)
        dst = os.path.join(DIFF_DIR, fname.replace('.docx', '_Ver.2.0.0.docx'))
    else:
        fname = q_files.get(sid)
        if not fname:
            continue
        src = os.path.join(SOURCE_DIR, fname)
        # _Ver.2.0.0 が既に付いている場合は付け直さない
        base = fname.replace('.docx', '')
        dst = os.path.join(SOURCE_DIR, base + '_Ver.2.0.0.docx')

    # 既存の Ver.2.0.0 ファイルを削除してから新規作成
    if os.path.exists(dst):
        os.remove(dst)

    n = fix_docx(src, dst, replacements)
    if n > 0:
        docx_fixed += n
        print(f"  {os.path.basename(dst)} → {n}箇所修正")

print(f"\nWordファイル修正: {docx_fixed}箇所")

# 修正サマリー出力
summary_path = r'C:\Users\haya1\brain\20_Projects\compliance-quiz-v2\tools\fix_summary.txt'
with open(summary_path, 'w', encoding='utf-8') as f:
    f.write(f"修正問題数: {fixed_count}\n\n")
    for c in changes:
        f.write(f"[{c['subject_id']}] 第{c['num']}問\n")
        f.write(f"  修正前({len(c['original'])}字): {c['original']}\n")
        f.write(f"  修正後({len(c['fixed'])}字): {c['fixed']}\n\n")
print(f"サマリー: {summary_path}")

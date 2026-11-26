#!/usr/bin/env python3
"""書き上げた鑑定文・返信文を、くり返しやすいミスの形で機械的に洗い出す。

  python3 uranai/tools/check.py --mode honkantei --char tsuruha 下書き.txt
  （--mode は free / honkantei / line。ファイルを省くと標準入力から読む）

・「」の中（本人の言葉の引用）は調べない
・出た箇所が全部まちがいとは限らない。一つずつ見て、書かれていない理由・断定・たとえなら直す
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

BRANCH = "origin/claude/laughing-darwin-tl18eq"

# 理由・動機の決めつけになりやすい形
# 「〜したのは〜からです」の形に絞る（気持ちの説明の「〜からです」は拾わない）
REASON = [r"のは[^。]*(から|ため)です", r"と分かった", r"と気づいた"]
# 人間関係・行動・未来を全否定・全肯定で言い切りやすい語
ABSOLUTE = ["誰にも", "誰も", "いつも", "一度も", "全く", "まったく", "必ず", "絶対", "決して", "ずっと", "何もかも", "すべて", "全て"]
# 占いの申し込みと紛らわしい語（相談者の仕事の意味で使っていないか）
CONFUSING = ["依頼", "お申し込み", "申込"]
# 用途ごとの禁止の決まり文句
BANNED = {
    "honkantei": ["結論から、お伝えします", "この問いに、お答えします", r"(^|。)\s*では、", r"(^|。)\s*ここからは"],
    "free": ["お待たせ致しました", "初穂料", "シート"],
    "line": ["シート", "初穂料"],
}
# 多用しやすい言葉（4回以上で知らせる）
OVERUSE = ["一人で", "大切に", "丁寧に", "静かに", "少しずつ", "これまで", "これから"]
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")


def strip_quotes(line):
    return re.sub(r"「[^」]*」", "「…」", line)


def char_metaphors(char):
    path = Path(__file__).resolve().parent.parent / "characters" / f"{char}.md"
    text = None
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        try:
            text = subprocess.run(["git", "show", f"{BRANCH}:uranai/characters/{char}.md"],
                                  capture_output=True, text=True, check=True).stdout
        except Exception:
            return []
    m = re.search(r"^- チェックで拾うたとえの語.*?：(.+)$", text, re.M)
    return [w.strip() for w in re.split(r"[、,／/]", m.group(1)) if w.strip()] if m else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["free", "honkantei", "line"], required=True)
    ap.add_argument("--char", default="")
    ap.add_argument("file", nargs="?")
    a = ap.parse_args()
    text = Path(a.file).read_text(encoding="utf-8") if a.file else sys.stdin.read()
    lines = text.split("\n")
    hits = []

    def add(n, kind, word, line):
        hits.append(f"{n:>4}行目［{kind}］「{word}」: {line.strip()[:60]}")

    metaphors = char_metaphors(a.char) if a.char else []
    for i, raw in enumerate(lines, 1):
        line = strip_quotes(raw)
        for p in REASON:
            if re.search(p, line):
                add(i, "理由・動機の決めつけ？", "〜のは〜からです" if p.startswith("のは") else p, raw)
        for w in ABSOLUTE:
            if w in line:
                add(i, "全否定・全肯定の断定？", w, raw)
        for w in CONFUSING:
            if w in line and not re.search(r"鑑定[をのにへ]?(ご|お)?" + w, line):
                add(i, "占いの申込と紛らわしい語？", w, raw)
        for w in BANNED.get(a.mode, []):
            if re.search(w, line.strip()):
                add(i, "使わない決まりの言い回し", w.replace("(^|。)\\s*", ""), raw)
        for w in metaphors:
            if w in line:
                add(i, "比喩の軸以外のたとえ？", w, raw)
        if a.mode in ("free", "honkantei") and EMOJI.search(line):
            add(i, "鑑定文に絵文字", EMOJI.search(line).group(0), raw)

    # 段落の入り方のくり返し：段落の先頭（空行の次の行）で、頭の2文字が同じものが3回以上
    starts = {}
    prev_blank = True
    for i, raw in enumerate(lines, 1):
        s = raw.strip()
        if not s:
            prev_blank = True
            continue
        if prev_blank and len(s) >= 2 and s[0] not in "・「":
            starts.setdefault(s[:2], []).append(i)
        prev_blank = False
    for head, ns in starts.items():
        if len(ns) >= 3:
            hits.append(f"     ［段落の入り方のくり返し？］段落の頭「{head}」が{len(ns)}回: {', '.join(map(str, ns[:8]))}行目")
    # 3行続けて同じ頭で始まる
    for i in range(len(lines) - 2):
        heads = [lines[i + k].strip()[:2] for k in range(3)]
        if all(len(h) == 2 for h in heads) and len(set(heads)) == 1 and heads[0][0] not in "・「":
            hits.append(f"     ［3行続けて同じ入り方？］「{heads[0]}」: {i + 1}〜{i + 3}行目")

    body = strip_quotes(text)
    for w in OVERUSE:
        c = body.count(w)
        if c >= 4:
            hits.append(f"     ［同じ言葉の多用？］「{w}」が{c}回")

    chars = len(text.replace("\n", ""))
    print(f"文字数：{chars}字" + ("（本鑑定の目安は7,000〜10,000字）" if a.mode == "honkantei" else ""))
    if hits:
        print("見直す箇所：")
        print("\n".join(hits))
    else:
        print("機械的に拾える箇所はありませんでした（読みの中身は自分で確かめる）")


if __name__ == "__main__":
    main()

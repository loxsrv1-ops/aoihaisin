#!/usr/bin/env python3
"""キャラ設定 × 用途 の貼り付け用プロンプトを uranai/dist/ に作る。

  python3 uranai/build.py

できるもの（キャラごと）:
  dist/<キャラ>_<用途>.md  … 用途を1つだけ入れたもの
  dist/<キャラ>_all.md     … 全部の用途を入れたもの（1つのチャットで全部やるとき用）
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEP = "\n\n---\n\n"


def title_of(text):
    m = re.search(r"^# (.+)$", text, re.M)
    return m.group(1).strip() if m else ""


def read(path):
    return path.read_text(encoding="utf-8").strip()


def main():
    common = read(ROOT / "common" / "rules.md")
    modes = [(p.stem, read(p)) for p in sorted((ROOT / "modes").glob("*.md"))]
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)

    for char_path in sorted((ROOT / "characters").glob("*.md")):
        if char_path.name.startswith("_"):
            continue
        char = read(char_path)
        name = title_of(char).replace("キャラ設定：", "")

        outputs = {
            f"{char_path.stem}_{stem}.md": (title_of(text), [text])
            for stem, text in modes
        }
        outputs[f"{char_path.stem}_all.md"] = (
            "全用途", [text for _, text in modes])

        for filename, (label, mode_texts) in outputs.items():
            body = SEP.join([f"# {name}｜{label} プロンプト", char, common, *mode_texts])
            out = dist / filename
            out.write_text(body + "\n", encoding="utf-8")
            print(out.relative_to(ROOT.parent))


if __name__ == "__main__":
    main()

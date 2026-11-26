# 占いプロンプト一式

キャラを増やしても使い回せるように、3つに分けています。

- `common/rules.md` … 全キャラ共通のルール（必須確認、事実を足さない、比喩の使い方、禁止事項、料金の扱い、法務）
- `characters/` … キャラごとの設定シート。1キャラ1ファイル。`_template.md` が空の型
- `modes/` … 用途ごとの手順。`free_reading.md`＝無料鑑定、`honkantei.md`＝本鑑定、`line_reply.md`＝LINE返信（受付から購入・ヒアリング・途中の一言まで）
- `dist/` … 上の3つをつなげた、貼り付け用のプロンプト（自動で作るので直接直さない）
- `knowhow.md` … ユーザーが集めた占い集客のノウハウの要点（プロンプトの土台）
- `tools/kyusei.py` … 九星気学の計算（本命星・月命星・年の巡り）。`python3 uranai/tools/kyusei.py 1967-09-13 2026 2027`

## 使い方
- 貼り付けるのは `dist/` の中のファイル
  - `tsuruha_all.md` … 鶴羽の全部入り（無料鑑定もLINE返信も1つのチャットでやるとき）
  - `tsuruha_free_reading.md` … 鶴羽の無料鑑定だけ
  - `tsuruha_line_reply.md` … 鶴羽のLINE返信だけ
  - `tsuruha_honkantei.md` … 鶴羽の本鑑定だけ
- 中身を直したら `python3 uranai/build.py` を実行すると `dist/` が作り直される

## キャラを増やすとき
1. `characters/_template.md` をコピーして、`characters/（ローマ字の名前）.md` にする
2. 全部の項目を埋める
3. `python3 uranai/build.py` を実行する

## 用途を増やすとき（本鑑定、リプ返信、投稿など）
`modes/` にファイルを1つ足して、`python3 uranai/build.py` を実行する。全キャラ分が一度にできる。

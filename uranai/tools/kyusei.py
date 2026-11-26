#!/usr/bin/env python3
"""九星気学の計算（本命星・月命星・年の巡り）。

  python3 uranai/tools/kyusei.py 1967-09-13            # 本命星・月命星と、今年から3年分の巡り
  python3 uranai/tools/kyusei.py 1967-09-13 2026 2027  # 巡りを見る年を指定

・九星の1年は立春（2月4日ごろ）から始まる。立春より前の生まれは前年の星
・月は節入り（各月の6〜8日ごろ）で区切る
・節入りの日付は年によって1日ほど前後する。境目の日の生まれは「要確認」と出すので、
  暦で節入りの日時を確かめてから使う。確かめられないときは、その星を鑑定に書かない
"""
import sys
from datetime import date

STARS = {1: "一白水星", 2: "二黒土星", 3: "三碧木星", 4: "四緑木星", 5: "五黄土星",
         6: "六白金星", 7: "七赤金星", 8: "八白土星", 9: "九紫火星"}

# 五行と、伝統的な意味（象意）の要点。鑑定では、ここから言えることだけを使う
GOGYO = {1: "水", 2: "土", 3: "木", 4: "木", 5: "土", 6: "金", 7: "金", 8: "土", 9: "火"}
SHOI = {
    1: "水の星。柔らかく形を変えながら、人と人のあいだに入ってつなぐ。忍耐強く、内に深い思いを秘める",
    2: "大地の星。支える・育てる。地道な努力を重ね、人の役に立つことで力を発揮する",
    3: "雷・若木の星。動き出す力と発信力。新しいことを始めるときに強い",
    4: "風の星。信用と調和。人の縁を運び、物事をまとめて整える",
    5: "中央・帝王の星。強い意志と統率力。行き詰まりから立て直す力",
    6: "天の星。自分の力で立ち、責任を引き受け、人を支える側に立つ",
    7: "沢・喜びの星。お金と人の縁、言葉と楽しみに恵まれやすい",
    8: "山の星。積み上げて蓄える力。変化や受け継ぎの節目に強い",
    9: "火・太陽の星。直感と知性で物事を明らかにし、表に出て評価される",
}

# 節入りのおおよその日付（月, 日）。寅月（2月）から順に。
SETSU = [(2, 4), (3, 6), (4, 5), (5, 6), (6, 6), (7, 7), (8, 8), (9, 8), (10, 8), (11, 7), (12, 7), (1, 6)]

# 年盤で、中宮の星から1つずつ進む順番（飛泊順）
PALACES = [
    ("中宮", "転換期。動くより整える年"),
    ("乾宮（北西）", "充実。責任や大きな仕事が回ってくる年"),
    ("兌宮（西）", "実り。楽しみも出費も増える年"),
    ("艮宮（北東）", "変化。切り替えや転機の年"),
    ("離宮（南）", "頂点。努力が表に出て評価される年"),
    ("坎宮（北）", "冬の年。停滞しやすく、準備と内省の年"),
    ("坤宮（南西）", "土台づくり。地道な積み重ねの年"),
    ("震宮（東）", "動き出し。新しいことが始まる年"),
    ("巽宮（南東）", "整う。信用や縁がまとまる年"),
]


# 年盤の宮と方角（PALACES と同じ並び）
DIRS = ["中宮", "北西", "西", "北東", "南", "北", "南西", "東", "南東"]
OPPOSITE = {"北": "南", "南": "北", "東": "西", "西": "東",
            "北東": "南西", "南西": "北東", "南東": "北西", "北西": "南東"}
# 十二支の方角（子＝北 から）。艮・坤・巽・乾は2つの支を含むが、ここでは宮ごと凶方として扱う（安全側）
BRANCH_DIR = ["北", "北東", "北東", "東", "南東", "南東", "南", "南西", "南西", "西", "北西", "北西"]
GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}


def wrap9(n):
    n %= 9
    return 9 if n == 0 else n


def year_star(kyusei_year):
    """九星の年（立春〜翌立春）の星。"""
    s = sum(int(c) for c in str(kyusei_year))
    while s > 9:
        s = sum(int(c) for c in str(s))
    return wrap9(11 - s)


def kyusei_year_of(d):
    return d.year if (d.month, d.day) >= SETSU[0] else d.year - 1


def month_index(d):
    """寅月=0 ... 丑月=11"""
    for i in range(11, -1, -1):
        m, day = SETSU[i]
        if i == 11:  # 丑月は1月6日〜2月3日
            if (d.month == 1 and d.day >= day) or (d.month == 2 and (d.month, d.day) < SETSU[0]):
                return 11
            continue
        if (d.month, d.day) >= (m, day) and (i == 10 or (d.month, d.day) < SETSU[i + 1]):
            return i
    return 10  # 子月（12月7日〜1月5日）の1月部分


def near_boundary(d):
    for m, day in SETSU:
        if d.month == m and abs(d.day - day) <= 1:
            return True
    return False


def month_star(honmei, idx):
    start = {1: 8, 4: 8, 7: 8, 3: 5, 6: 5, 9: 5, 2: 2, 5: 2, 8: 2}[honmei]
    return wrap9(start - idx)


def palace_in_year(honmei, kyusei_year):
    center = year_star(kyusei_year)
    return PALACES[(honmei - center) % 9]


def year_board(kyusei_year):
    """方角 → その年にその方角へ回る星"""
    center = year_star(kyusei_year)
    return {DIRS[i]: wrap9(center + i) for i in range(9)}


def relation(honmei, star):
    a, b = GOGYO[honmei], GOGYO[star]
    if a == b:
        return "比和"
    if GENERATES[b] == a:
        return "生気"  # その星が本命星を生む
    if GENERATES[a] == b:
        return "退気"  # 本命星がその星を生む
    return None


def lucky_directions(honmei, kyusei_year):
    """その年の吉方位と、除いた凶方位（理由つき）。"""
    board = year_board(kyusei_year)
    where = {star: d for d, star in board.items()}
    bad = {}
    def mark(d, why):
        if d and d != "中宮":
            bad.setdefault(d, []).append(why)
    mark(where[5], "五黄殺")
    if where[5] != "中宮":
        mark(OPPOSITE[where[5]], "暗剣殺")
    mark(OPPOSITE[BRANCH_DIR[(kyusei_year - 4) % 12]], "歳破")
    if where[honmei] != "中宮":
        mark(where[honmei], "本命殺")
        mark(OPPOSITE[where[honmei]], "本命的殺")
    good = []
    for d in DIRS[1:]:
        if d in bad:
            continue
        rel = relation(honmei, board[d])
        if rel and board[d] != 5:
            good.append((d, board[d], rel))
    return good, bad


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    birth = date.fromisoformat(sys.argv[1])
    ky = kyusei_year_of(birth)
    honmei = year_star(ky)
    getsumei = month_star(honmei, month_index(birth))
    print(f"生年月日：{birth.isoformat()}")
    print(f"本命星：{STARS[honmei]}（九星の年は{ky}年）")
    print(f"  五行：{GOGYO[honmei]}／意味：{SHOI[honmei]}")
    print(f"月命星：{STARS[getsumei]}")
    print(f"  五行：{GOGYO[getsumei]}／意味：{SHOI[getsumei]}")
    if GOGYO[honmei] == GOGYO[getsumei]:
        print(f"※本命星と月命星が、同じ「{GOGYO[honmei]}」の星です（年と月の両方に{GOGYO[honmei]}の星を持つ生まれ）")
    if near_boundary(birth):
        print("※節入りの境目に近い生まれです。暦で節入りの日時を確かめてから使ってください（本命星・月命星が変わることがあります）")
    years = [int(y) for y in sys.argv[2:]] or [date.today().year + i for i in range(3)]
    print("年の巡り（九星の年は立春から始まる）：")
    for y in years:
        name, meaning = palace_in_year(honmei, y)
        print(f"  {y}年（年の星：{STARS[year_star(y)]}）→ 本命星は{name}：{meaning}")
        good, bad = lucky_directions(honmei, y)
        g = "、".join(f"{d}（{STARS[st]}・{rel}）" for d, st, rel in good) or "なし"
        b = "、".join(f"{d}（{'・'.join(w)}）" for d, w in bad.items())
        print(f"    吉方位：{g}")
        print(f"    除いた凶方位：{b}")
    print("※吉方位は年盤だけで見たもの（立春から翌立春まで）。流派で差があるので、鑑定では「方角としても力を向けやすい」程度に書き、引っ越しや契約など大きな決断を方角だけで勧めない")


if __name__ == "__main__":
    main()

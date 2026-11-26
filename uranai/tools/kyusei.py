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
    print(f"月命星：{STARS[getsumei]}")
    if near_boundary(birth):
        print("※節入りの境目に近い生まれです。暦で節入りの日時を確かめてから使ってください（本命星・月命星が変わることがあります）")
    years = [int(y) for y in sys.argv[2:]] or [date.today().year + i for i in range(3)]
    print("年の巡り（九星の年は立春から始まる）：")
    for y in years:
        name, meaning = palace_in_year(honmei, y)
        print(f"  {y}年（年の星：{STARS[year_star(y)]}）→ 本命星は{name}：{meaning}")


if __name__ == "__main__":
    main()

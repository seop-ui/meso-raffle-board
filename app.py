import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Raffle Prize Board", layout="wide")

# 10초마다 자동 새로고침
st_autorefresh(interval=10_000, key="raffle_refresh")

# -----------------------------
# Google Sheets CSV URL
# -----------------------------
sheet_url = "https://docs.google.com/spreadsheets/d/1oYJliCBrYC2qhAKNjGUbaTv4o6fxzpgGb8a-xSt1UOk/export?format=csv"

df = pd.read_csv(sheet_url)

# -----------------------------
# 시트 컬럼 정리
# 불필요한 Unnamed 컬럼 제거
# -----------------------------
df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

# -----------------------------
# 값 정리
# -----------------------------
for col in ["Qty", "Winners", "Available"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

df["Place"] = df["Place"].astype(str).str.strip()
df["Prize"] = df["Prize"].astype(str).str.strip()
df["Odds"] = df["Odds"].astype(str).str.strip()

# -----------------------------
# 시트에서 경품 데이터 찾기
# -----------------------------
def get_prize(place, prize):
    row = df[(df["Place"] == place) & (df["Prize"] == prize)]

    if row.empty:
        return {
            "qty": 0,
            "available": 0,
            "odds": "0%",
            "sold_out": True,
        }

    qty = int(row.iloc[0]["Qty"])
    available = int(row.iloc[0]["Available"])
    odds = str(row.iloc[0]["Odds"]).strip()

    return {
        "qty": qty,
        "available": available,
        "odds": odds,
        "sold_out": available <= 0,
    }

# -----------------------------
# 표시 문자열
# -----------------------------
def qty_html(item):
    if item["sold_out"]:
        return '<div class="qty soldout-text">SOLD OUT</div>'
    return f'<div class="qty">{item["available"]}/{item["qty"]}</div>'

def odds_html(item):
    if item["sold_out"]:
        return '<div class="odds soldout-sub">No chance left</div>'
    return f'<div class="odds">{item["odds"]}</div>'

def card_class(item, large=False):
    base = "big-card" if large else "card"
    if item["sold_out"]:
        return f"{base} soldout-card"
    if item["available"] <= 2:
        return f"{base} low-card"
    return base

# -----------------------------
# 각 경품 데이터 연결
# -----------------------------
hair = get_prize("Single", "Laser Hair Removal (1 Session)")
facial = get_prize("Single", "Custom Korean Facial (1 Session)")

off_bb = get_prize("80Off", "BB Laser")
off_sylfirm = get_prize("80Off", "SylfirmX RF Microneedling")
off_oligio = get_prize("80Off", "Oligio Lifting")
off_ultherapy = get_prize("80Off", "Ultherapy Prime")

free_bb = get_prize("Free", "BB Laser")
free_sylfirm = get_prize("Free", "SylfirmX RF Microneedling")
free_oligio = get_prize("Free", "Oligio Lifting")
free_ultherapy = get_prize("Free", "Ultherapy Prime")

# -----------------------------
# 스타일
# -----------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #f7f7f5;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1800px;
}

.main-title {
    text-align: center;
    font-size: 52px;
    font-weight: 800;
    margin-bottom: 38px;
    color: #1b2230;
}

.board {
    display: flex;
    gap: 24px;
    align-items: stretch;
}

.left {
    display: flex;
    gap: 20px;
    width: 25%;
}

.right {
    display: flex;
    gap: 20px;
    width: 75%;
}

.group {
    width: 50%;
}

.group-title {
    border: 3px solid #1f3341;
    text-align: center;
    padding: 10px;
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 10px;
    background: white;
    color: #1f3341;
}

.grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
}

.card, .big-card {
    border: 3px solid #1f3341;
    background: white;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #1f3341;
    box-sizing: border-box;
}

.card {
    min-height: 200px;
    padding: 14px 10px;
}

.big-card {
    min-height: 300px;
    width: 50%;
    padding: 20px 14px;
}

.prize {
    font-size: 18px;
    margin-bottom: 10px;
    text-align: center;
    padding: 0 8px;
    line-height: 1.25;
}

.qty {
    font-size: 40px;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 8px;
}

.odds-label {
    font-size: 16px;
    color: #536171;
    margin-bottom: 4px;
}

.odds {
    font-size: 26px;
    font-weight: 700;
    line-height: 1.1;
}

.low-card {
    background: #fff7df;
}

.soldout-card {
    background: #eceff3;
    border-color: #7f8a96;
    color: #5f6975;
}

.soldout-text {
    font-size: 28px;
    letter-spacing: 0.5px;
}

.soldout-sub {
    font-size: 18px;
    font-weight: 600;
}

.info-title {
    text-align: center;
    font-size: 30px;
    font-weight: 700;
    margin-top: 40px;
    color: #1b2230;
}

.info-box {
    border: 3px solid #1f3341;
    background: white;
    padding: 30px;
    font-size: 22px;
    margin-top: 10px;
    line-height: 1.8;
    color: #1f3341;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 제목
# -----------------------------
st.markdown('<div class="main-title">래플 이벤트 경품 현황판</div>', unsafe_allow_html=True)

# -----------------------------
# 왼쪽 큰 카드
# -----------------------------
left = f"""
<div class="left">

<div class="{card_class(hair, large=True)}">
<div class="prize">Hair Removal Prize</div>
{qty_html(hair)}
<div class="odds-label">Odds</div>
{odds_html(hair)}
</div>

<div class="{card_class(facial, large=True)}">
<div class="prize">Facial Prize</div>
{qty_html(facial)}
<div class="odds-label">Odds</div>
{odds_html(facial)}
</div>

</div>
"""

# -----------------------------
# 80% Off 그룹
# -----------------------------
group1 = f"""
<div class="group">
<div class="group-title">80% Off MeSO Signature Treatment</div>

<div class="grid">

<div class="{card_class(off_bb)}">
<div class="prize">BB Laser</div>
{qty_html(off_bb)}
<div class="odds-label">Odds</div>
{odds_html(off_bb)}
</div>

<div class="{card_class(off_sylfirm)}">
<div class="prize">SylfirmX RF Microneedling</div>
{qty_html(off_sylfirm)}
<div class="odds-label">Odds</div>
{odds_html(off_sylfirm)}
</div>

<div class="{card_class(off_oligio)}">
<div class="prize">Oligio Lifting</div>
{qty_html(off_oligio)}
<div class="odds-label">Odds</div>
{odds_html(off_oligio)}
</div>

<div class="{card_class(off_ultherapy)}">
<div class="prize">Ultherapy Prime</div>
{qty_html(off_ultherapy)}
<div class="odds-label">Odds</div>
{odds_html(off_ultherapy)}
</div>

</div>
</div>
"""

# -----------------------------
# Free 그룹
# -----------------------------
group2 = f"""
<div class="group">
<div class="group-title">Free MeSO Signature Treatment</div>

<div class="grid">

<div class="{card_class(free_bb)}">
<div class="prize">BB Laser</div>
{qty_html(free_bb)}
<div class="odds-label">Odds</div>
{odds_html(free_bb)}
</div>

<div class="{card_class(free_sylfirm)}">
<div class="prize">SylfirmX RF Microneedling</div>
{qty_html(free_sylfirm)}
<div class="odds-label">Odds</div>
{odds_html(free_sylfirm)}
</div>

<div class="{card_class(free_oligio)}">
<div class="prize">Oligio Lifting</div>
{qty_html(free_oligio)}
<div class="odds-label">Odds</div>
{odds_html(free_oligio)}
</div>

<div class="{card_class(free_ultherapy)}">
<div class="prize">Ultherapy Prime</div>
{qty_html(free_ultherapy)}
<div class="odds-label">Odds</div>
{odds_html(free_ultherapy)}
</div>

</div>
</div>
"""

# -----------------------------
# 보드 렌더링
# -----------------------------
st.markdown(f"""
<div class="board">
{left}
<div class="right">
{group1}
{group2}
</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# 참여방법
# -----------------------------
st.markdown('<div class="info-title">이벤트 참여방법</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
1. 이벤트 대상 시술 결제<br>
2. 응모권 수령<br>
3. 추첨기 참여<br>
4. 당첨 시 직원 안내 후 경품 수령
</div>
""", unsafe_allow_html=True)

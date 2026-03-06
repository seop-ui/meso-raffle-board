import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Raffle Prize Board",
    layout="wide",
)

# ---------------------------------
# 5초마다 자동 새로고침
# ---------------------------------
st_autorefresh(interval=5_000, key="raffle_refresh")

# ---------------------------------
# Google Sheets CSV URL
# ---------------------------------
sheet_url = "https://docs.google.com/spreadsheets/d/1oYJliCBrYC2qhAKNjGUbaTv4o6fxzpgGb8a-xSt1UOk/export?format=csv"

# 일반 표 형태로 읽기
df = pd.read_csv(sheet_url)

# K2 셀을 정확히 읽기 위해 raw 형태로 한 번 더 읽기
raw_df = pd.read_csv(sheet_url, header=None)

# ---------------------------------
# 불필요한 Unnamed 컬럼 제거
# ---------------------------------
df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]

# ---------------------------------
# 값 정리
# ---------------------------------
for col in ["Qty", "Winners", "Available"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

df["Place"] = df["Place"].astype(str).str.strip()
df["Prize"] = df["Prize"].astype(str).str.strip()
df["Odds"] = df["Odds"].astype(str).str.strip()

# ---------------------------------
# K2 셀 읽기
# K열 = 11번째 열 = index 10
# 2행 = index 1
# ---------------------------------
try:
    how_to_text = str(raw_df.iloc[1, 10]).strip()
    if how_to_text.lower() == "nan" or how_to_text == "":
        how_to_text = "1. 이벤트 대상 시술 결제\n2. 응모권 수령\n3. 추첨기 참여\n4. 당첨 시 직원 안내 후 경품 수령"
except Exception:
    how_to_text = "1. 이벤트 대상 시술 결제\n2. 응모권 수령\n3. 추첨기 참여\n4. 당첨 시 직원 안내 후 경품 수령"

how_to_html = how_to_text.replace("\n", "<br>")

# ---------------------------------
# 시트에서 경품 데이터 찾기
# ---------------------------------
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

# ---------------------------------
# 표시 문자열
# ---------------------------------
def qty_html(item):
    if item["sold_out"]:
        return '<div class="qty soldout-text">SOLD OUT</div>'
    return f'''
    <div class="qty-wrap">
        <div class="qty-main">{item["available"]}</div>
        <div class="qty-sub">of {item["qty"]}</div>
    </div>
    '''

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

# ---------------------------------
# 각 경품 데이터 연결
# ---------------------------------
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

# ---------------------------------
# 스타일
# ---------------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #f7f7f5;
    color: #1f3341;
}

.block-container {
    max-width: 1820px;
    padding-top: 1.4rem;
    padding-bottom: 2.2rem;
}

.main-title {
    text-align: center;
    font-size: 58px;
    font-weight: 800;
    margin: 8px 0 42px 0;
    color: #1b2230;
    letter-spacing: -0.5px;
}

.board {
    display: flex;
    gap: 28px;
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
    border: 3px solid #22384a;
    background: #ffffff;
    text-align: center;
    padding: 14px 12px;
    font-size: 24px;
    font-weight: 800;
    margin-bottom: 12px;
    color: #1f3341;
    border-radius: 12px;
    letter-spacing: -0.2px;
}

.grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
}

.card, .big-card {
    border: 3px solid #22384a;
    background: #ffffff;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #1f3341;
    box-sizing: border-box;
    border-radius: 16px;
    box-shadow: 0 4px 14px rgba(15, 30, 45, 0.05);
}

.card {
    min-height: 220px;
    padding: 16px 12px;
}

.big-card {
    min-height: 332px;
    width: 50%;
    padding: 22px 16px;
}

.prize {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 18px;
    text-align: center;
    padding: 0 8px;
    line-height: 1.3;
    min-height: 52px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.qty-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 10px;
}

.qty-main {
    font-size: 54px;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -1px;
}

.qty-sub {
    font-size: 18px;
    font-weight: 600;
    margin-top: 6px;
    color: #5b6b79;
}

.odds-label {
    font-size: 16px;
    color: #6b7a88;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 700;
}

.odds {
    font-size: 30px;
    font-weight: 800;
    line-height: 1.1;
}

.low-card {
    background: #fff6da;
    border-color: #c89000;
}

.soldout-card {
    background: #eceff3;
    border-color: #8a96a3;
    color: #5f6975;
    box-shadow: none;
}

.soldout-text {
    font-size: 30px;
    font-weight: 900;
    letter-spacing: 0.6px;
    line-height: 1.1;
    margin-bottom: 10px;
}

.soldout-sub {
    font-size: 18px;
    font-weight: 700;
}

.info-title {
    text-align: center;
    font-size: 34px;
    font-weight: 800;
    margin-top: 48px;
    margin-bottom: 16px;
    color: #1b2230;
    letter-spacing: -0.3px;
}

.info-box {
    border: 3px solid #22384a;
    background: #ffffff;
    padding: 30px 34px;
    font-size: 28px;
    margin-top: 8px;
    line-height: 1.9;
    color: #1f3341;
    border-radius: 18px;
    box-shadow: 0 4px 14px rgba(15, 30, 45, 0.05);
}

@media (max-width: 1400px) {
    .main-title {
        font-size: 46px;
    }
    .qty-main {
        font-size: 42px;
    }
    .prize {
        font-size: 18px;
    }
    .odds {
        font-size: 24px;
    }
    .info-box {
        font-size: 22px;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# 제목
# ---------------------------------
st.markdown('<div class="main-title">래플 이벤트 경품 현황판</div>', unsafe_allow_html=True)

# ---------------------------------
# 왼쪽 큰 카드
# ---------------------------------
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

# ---------------------------------
# 80% Off 그룹
# ---------------------------------
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

# ---------------------------------
# Free 그룹
# ---------------------------------
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

# ---------------------------------
# 보드 렌더링
# ---------------------------------
st.markdown(f"""
<div class="board">
{left}
<div class="right">
{group1}
{group2}
</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------
# 참여방법 (K2 셀 문구)
# ---------------------------------
st.markdown('<div class="info-title">이벤트 참여방법</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="info-box">
{how_to_html}
</div>
""", unsafe_allow_html=True)

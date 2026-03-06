import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Raffle Event Prize Board",
    layout="wide",
)

# 5초마다 자동 새로고침
st_autorefresh(interval=5_000, key="raffle_refresh")

# Google Sheets CSV URL
sheet_url = "https://docs.google.com/spreadsheets/d/1oYJliCBrYC2qhAKNjGUbaTv4o6fxzpgGb8a-xSt1UOk/export?format=csv"

# 시트 읽기
df = pd.read_csv(sheet_url)
raw_df = pd.read_csv(sheet_url, header=None)

# 불필요한 Unnamed 컬럼 제거
df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]

# 값 정리
for col in ["Qty", "Winners", "Available"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

df["Place"] = df["Place"].astype(str).str.strip()
df["Prize"] = df["Prize"].astype(str).str.strip()
df["Odds"] = df["Odds"].astype(str).str.strip()

# Ball Count 읽기 (I2 기준)
try:
    ball_count = int(pd.to_numeric(raw_df.iloc[1, 8], errors="coerce"))
    if ball_count <= 0:
        ball_count = 200
except Exception:
    ball_count = 200

# 경품 데이터 찾기
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

def get_card_class(item, large=False):
    base = "feature-card" if large else "prize-card"
    if item["sold_out"]:
        return f"{base} soldout-card"
    if item["available"] <= 2:
        return f"{base} low-card"
    return base

def render_card(title, item, large=False):
    card_class = get_card_class(item, large)

    if item["sold_out"]:
        main_value = '<div class="value soldout-main">SOLD OUT</div>'
        qty_line = '<div class="qty-line soldout-sub">No chance left</div>'
        odds_value = '<div class="odds-value soldout-sub">0%</div>'
    else:
        main_value = f'<div class="value">{item["available"]}</div>'
        qty_line = f'<div class="qty-line">/ {item["qty"]}</div>'
        odds_value = f'<div class="odds-value">{item["odds"]}</div>'

    return (
        f'<div class="{card_class}">'
        f'<div class="title">{title}</div>'
        f'<div class="value-row">{main_value}{qty_line}</div>'
        f'<div class="odds-label">ODDS</div>'
        f'<div class="odds-row">{odds_value}</div>'
        f'</div>'
    )

def summary_box(label, value):
    return (
        '<div class="summary-card">'
        f'<div class="summary-label">{label}</div>'
        f'<div class="summary-value">{value}</div>'
        '</div>'
    )

# 데이터 연결
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

# 요약 수치 계산
total_prizes_left = int(df["Available"].sum())
win_chance = round((total_prizes_left / ball_count) * 100, 2) if ball_count > 0 else 0
lose_count = max(ball_count - total_prizes_left, 0)
lose_chance = round((lose_count / ball_count) * 100, 2) if ball_count > 0 else 0

# 스타일
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #F7F7F5;
    color: #3B4F38;
}

.block-container {
    max-width: 1450px;
    padding-top: 0.2rem;
    padding-bottom: 0.4rem;
    padding-left: 0.4rem;
    padding-right: 0.4rem;
}

.main-title {
    text-align: center;
    font-size: 76px;
    font-weight: 900;
    margin: 6px 0 18px 0;
    color: #3B4F38;
    letter-spacing: -1.4px;
    line-height: 1.05;
}

.summary-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
    margin-bottom: 14px;
}

.summary-card {
    border: 3px solid #3B4F38;
    background: #FFFFFF;
    border-radius: 16px;
    min-height: 126px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 12px 10px;
    box-sizing: border-box;
}

.summary-label {
    font-size: 20px;
    font-weight: 900;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 10px;
    line-height: 1.1;
    text-align: center;
}

.summary-value {
    font-size: 52px;
    font-weight: 900;
    line-height: 1;
    text-align: center;
}

.board {
    display: grid;
    grid-template-columns: 320px minmax(0, 1fr);
    gap: 16px;
    align-items: start;
}

.left-column {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
}

.right-column {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
}

.group {
    min-width: 0;
}

.group-title {
    border: 3px solid #3B4F38;
    background: #CFD4C2;
    border-radius: 14px;
    min-height: 72px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 8px 12px;
    font-size: 22px;
    font-weight: 900;
    line-height: 1.15;
    margin-bottom: 10px;
    box-sizing: border-box;
}

.group-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
}

.feature-card, .prize-card {
    border: 3px solid #3B4F38;
    background: #FFFFFF;
    border-radius: 18px;
    width: 100%;
    box-sizing: border-box;
    color: #3B4F38;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
}

.feature-card {
    min-height: 534px;
    padding: 18px 10px 16px 10px;
}

.prize-card {
    min-height: 208px;
    padding: 12px 10px 12px 10px;
}

.title {
    width: 100%;
    min-height: 110px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 0 10px;
    font-size: 21px;
    font-weight: 900;
    line-height: 1.2;
    word-break: keep-all;
    overflow-wrap: anywhere;
    box-sizing: border-box;
}

.prize-card .title {
    min-height: 66px;
    font-size: 17px;
    line-height: 1.18;
}

.value-row {
    min-height: 116px;
    display: flex;
    align-items: baseline;
    justify-content: center;
    gap: 4px;
    margin-top: 2px;
    margin-bottom: 8px;
}

.feature-card .value {
    font-size: 64px;
    font-weight: 900;
    line-height: 1;
}

.prize-card .value {
    font-size: 54px;
    font-weight: 900;
    line-height: 1;
}

.qty-line {
    font-size: 26px;
    font-weight: 800;
    line-height: 1;
}

.feature-card .qty-line {
    font-size: 30px;
}

.odds-label {
    min-height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    font-weight: 900;
    letter-spacing: 1.2px;
    line-height: 1;
    margin-top: auto;
}

.odds-row {
    min-height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.odds-value {
    font-size: 34px;
    font-weight: 900;
    line-height: 1;
}

.prize-card .odds-value {
    font-size: 28px;
}

.low-card {
    background: #F8F5F2;
}

.soldout-card {
    background: #ECEEE8;
    border-color: #9AA694;
    color: #6B7566;
}

.soldout-main {
    font-size: 28px !important;
    line-height: 1.1;
    text-align: center;
}

.soldout-sub {
    font-size: 16px !important;
    font-weight: 800;
}

@media (max-width: 1180px) {
    .block-container {
        max-width: 1120px;
    }

    .main-title {
        font-size: 56px;
    }

    .summary-row {
        grid-template-columns: 1fr;
    }

    .board {
        grid-template-columns: 1fr;
    }

    .left-column {
        grid-template-columns: 1fr 1fr;
    }

    .right-column {
        grid-template-columns: 1fr;
    }

    .feature-card {
        min-height: 420px;
    }

    .summary-value {
        font-size: 42px;
    }
}
</style>
""", unsafe_allow_html=True)

# 제목
st.markdown('<div class="main-title">Raffle Event Prize Board</div>', unsafe_allow_html=True)

# 요약 카드
summary_html = (
    '<div class="summary-row">'
    + summary_box("Total Prizes Left", total_prizes_left)
    + summary_box("Win Chance", f"{win_chance:.1f}%")
    + summary_box("Lose Chance", f"{lose_chance:.1f}%")
    + '</div>'
)
st.markdown(summary_html, unsafe_allow_html=True)

# 왼쪽 카드
left_html = (
    '<div class="left-column">'
    + render_card("Hair Removal (1 session)", hair, large=True)
    + render_card("Korean Facial (1 session)", facial, large=True)
    + '</div>'
)

# 오른쪽 그룹
group1_html = (
    '<div class="group">'
    '<div class="group-title">80% Off MeSO Signature Treatment</div>'
    '<div class="group-grid">'
    + render_card("BB Laser", off_bb)
    + render_card("SylfirmX RF Microneedling", off_sylfirm)
    + render_card("Oligio Lifting", off_oligio)
    + render_card("Ultherapy Prime", off_ultherapy)
    + '</div></div>'
)

group2_html = (
    '<div class="group">'
    '<div class="group-title">Free MeSO Signature Treatment</div>'
    '<div class="group-grid">'
    + render_card("BB Laser", free_bb)
    + render_card("SylfirmX RF Microneedling", free_sylfirm)
    + render_card("Oligio Lifting", free_oligio)
    + render_card("Ultherapy Prime", free_ultherapy)
    + '</div></div>'
)

right_html = (
    '<div class="right-column">'
    + group1_html
    + group2_html
    + '</div>'
)

board_html = (
    '<div class="board">'
    + left_html
    + right_html
    + '</div>'
)

st.markdown(board_html, unsafe_allow_html=True)

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Raffle Prize Board",
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

# K2 셀 읽기
default_how_to = (
    "1. 이벤트 대상 시술 결제\n"
    "2. 응모권 수령\n"
    "3. 추첨기 참여\n"
    "4. 당첨 시 직원 안내 후 경품 수령"
)

try:
    how_to_text = str(raw_df.iloc[1, 10]).strip()
    if how_to_text.lower() == "nan" or how_to_text == "":
        how_to_text = default_how_to
except Exception:
    how_to_text = default_how_to

how_to_html = how_to_text.replace("\n", "<br>")

# Ball Count 읽기 (I2 기준: row index 1, col index 8)
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
    base = "big-card" if large else "card"
    if item["sold_out"]:
        return f"{base} soldout-card"
    if item["available"] <= 2:
        return f"{base} low-card"
    return base

def render_card(title, item, large=False):
    card_class = get_card_class(item, large)

    if item["sold_out"]:
        qty_block = '<div class="soldout-text">SOLD OUT</div>'
        odds_block = '<div class="soldout-sub">No chance left</div>'
    else:
        qty_block = (
            '<div class="qty-wrap">'
            f'<div class="qty-main">{item["available"]}</div>'
            f'<div class="qty-sub">of {item["qty"]}</div>'
            '</div>'
        )
        odds_block = f'<div class="odds">{item["odds"]}</div>'

    return (
        f'<div class="{card_class}">'
        f'<div class="prize">{title}</div>'
        f'{qty_block}'
        f'<div class="odds-label">Odds</div>'
        f'{odds_block}'
        f'</div>'
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

def summary_box(label, value, sub=""):
    sub_html = f'<div class="summary-sub">{sub}</div>' if sub else ""
    return (
        '<div class="summary-card">'
        f'<div class="summary-label">{label}</div>'
        f'<div class="summary-value">{value}</div>'
        f'{sub_html}'
        '</div>'
    )

# 스타일
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #F7F7F5;
    color: #3B4F38;
}

.block-container {
    max-width: 1360px;
    padding-top: 0.8rem;
    padding-bottom: 1.8rem;
}

.main-title {
    text-align: center;
    font-size: 52px;
    font-weight: 900;
    margin: 8px 0 26px 0;
    color: #3B4F38;
    letter-spacing: -0.8px;
}

.summary-row {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin-bottom: 24px;
}

.summary-card {
    border: 3px solid #3B4F38;
    background: #FFFFFF;
    border-radius: 18px;
    padding: 16px 14px;
    text-align: center;
    box-shadow: 0 4px 14px rgba(59, 79, 56, 0.06);
    min-height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-width: 0;
}

.summary-label {
    font-size: 16px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #6B7867;
    margin-bottom: 8px;
}

.summary-value {
    font-size: 38px;
    font-weight: 900;
    line-height: 1.05;
    color: #3B4F38;
}

.summary-sub {
    font-size: 15px;
    font-weight: 700;
    margin-top: 6px;
    color: #7A8675;
}

.board {
    display: grid;
    grid-template-columns: 280px minmax(0, 1fr);
    gap: 18px;
    align-items: start;
}

.left {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    min-width: 0;
}

.right {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 16px;
    min-width: 0;
}

.group {
    min-width: 0;
}

.group-title {
    border: 3px solid #3B4F38;
    background: #CFD4C2;
    text-align: center;
    padding: 12px 10px;
    font-size: 22px;
    font-weight: 900;
    margin-bottom: 10px;
    color: #3B4F38;
    border-radius: 14px;
    letter-spacing: -0.2px;
}

.grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
}

.card, .big-card {
    border: 3px solid #3B4F38;
    background: #FFFFFF;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #3B4F38;
    box-sizing: border-box;
    border-radius: 18px;
    box-shadow: 0 4px 14px rgba(59, 79, 56, 0.05);
    min-width: 0;
    width: 100%;
}

.card {
    min-height: 210px;
    padding: 14px 10px;
}

.big-card {
    min-height: 286px;
    width: 100%;
    padding: 18px 14px;
}

.prize {
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 16px;
    text-align: center;
    padding: 0 6px;
    line-height: 1.28;
    min-height: 52px;
    display: flex;
    align-items: center;
    justify-content: center;
    word-break: keep-all;
    overflow-wrap: anywhere;
}

.qty-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-bottom: 8px;
}

.qty-main {
    font-size: 50px;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -1px;
}

.qty-sub {
    font-size: 17px;
    font-weight: 700;
    margin-top: 6px;
    color: #6E7A69;
}

.odds-label {
    font-size: 14px;
    color: #70806B;
    margin-bottom: 5px;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 900;
}

.odds {
    font-size: 28px;
    font-weight: 900;
    line-height: 1.1;
}

.low-card {
    background: #F8F5F2;
    border-color: #3B4F38;
}

.soldout-card {
    background: #ECEEE8;
    border-color: #9AA694;
    color: #6B7566;
    box-shadow: none;
}

.soldout-text {
    font-size: 28px;
    font-weight: 900;
    letter-spacing: 0.6px;
    line-height: 1.1;
    margin-bottom: 10px;
}

.soldout-sub {
    font-size: 17px;
    font-weight: 700;
}

.info-title {
    text-align: center;
    font-size: 30px;
    font-weight: 900;
    margin-top: 34px;
    margin-bottom: 12px;
    color: #3B4F38;
    letter-spacing: -0.3px;
}

.info-box {
    border: 3px solid #3B4F38;
    background: #FFFFFF;
    padding: 26px 28px;
    font-size: 18px;
    margin-top: 8px;
    line-height: 1.95;
    color: #3B4F38;
    border-radius: 18px;
    box-shadow: 0 4px 14px rgba(59, 79, 56, 0.05);
}

@media (max-width: 1180px) {
    .block-container {
        max-width: 1100px;
    }

    .summary-row {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .main-title {
        font-size: 42px;
    }

    .board {
        grid-template-columns: 1fr;
    }

    .left {
        grid-template-columns: 1fr 1fr;
    }

    .right {
        grid-template-columns: 1fr;
    }

    .group {
        width: 100%;
    }

    .qty-main {
        font-size: 42px;
    }
}
</style>
""", unsafe_allow_html=True)

# 제목
st.markdown('<div class="main-title">래플 이벤트 경품 현황판</div>', unsafe_allow_html=True)

# 요약 카드
summary_html = (
    '<div class="summary-row">'
    + summary_box("Total Prizes Left", total_prizes_left, "remaining prizes")
    + summary_box("Win Chance", f"{win_chance:.2f}%", "current overall odds")
    + summary_box("Lose Chance", f"{lose_chance:.2f}%", "miss probability")
    + summary_box("Ball Count", ball_count, "fixed total balls")
    + '</div>'
)
st.markdown(summary_html, unsafe_allow_html=True)

# HTML 조각
left_html = (
    '<div class="left">'
    + render_card("Hair Removal Prize", hair, large=True)
    + render_card("Facial Prize", facial, large=True)
    + '</div>'
)

group1_html = (
    '<div class="group">'
    '<div class="group-title">80% Off MeSO Signature Treatment</div>'
    '<div class="grid">'
    + render_card("BB Laser", off_bb)
    + render_card("SylfirmX RF Microneedling", off_sylfirm)
    + render_card("Oligio Lifting", off_oligio)
    + render_card("Ultherapy Prime", off_ultherapy)
    + '</div></div>'
)

group2_html = (
    '<div class="group">'
    '<div class="group-title">Free MeSO Signature Treatment</div>'
    '<div class="grid">'
    + render_card("BB Laser", free_bb)
    + render_card("SylfirmX RF Microneedling", free_sylfirm)
    + render_card("Oligio Lifting", free_oligio)
    + render_card("Ultherapy Prime", free_ultherapy)
    + '</div></div>'
)

board_html = (
    '<div class="board">'
    + left_html
    + '<div class="right">'
    + group1_html
    + group2_html
    + '</div></div>'
)

st.markdown(board_html, unsafe_allow_html=True)

# 참여방법
st.markdown('<div class="info-title">이벤트 참여방법</div>', unsafe_allow_html=True)
st.markdown(f'<div class="info-box">{how_to_html}</div>', unsafe_allow_html=True)

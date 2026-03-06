import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Raffle Event Prize Board",
    layout="wide",
)

st_autorefresh(interval=5_000, key="raffle_refresh")

sheet_url = "https://docs.google.com/spreadsheets/d/1oYJliCBrYC2qhAKNjGUbaTv4o6fxzpgGb8a-xSt1UOk/export?format=csv"

df = pd.read_csv(sheet_url)
raw_df = pd.read_csv(sheet_url, header=None)

df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]

for col in ["Qty", "Winners", "Available"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

df["Place"] = df["Place"].astype(str).str.strip()
df["Prize"] = df["Prize"].astype(str).str.strip()
df["Odds"] = df["Odds"].astype(str).str.strip()

try:
    ball_count = int(pd.to_numeric(raw_df.iloc[1, 8], errors="coerce"))
    if ball_count <= 0:
        ball_count = 200
except Exception:
    ball_count = 200


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
        value_block = '<div class="value soldout-main">SOLD OUT</div>'
        odds_value = '<div class="odds-value soldout-sub">0%</div>'
    else:
        value_block = (
            '<div class="value-row">'
            f'<div class="value">{item["available"]}</div>'
            f'<div class="qty-line">/{item["qty"]}</div>'
            '</div>'
        )
        odds_value = f'<div class="odds-value">{item["odds"]}</div>'

    return (
        f'<div class="{card_class}">'
        f'<div class="title">{title}</div>'
        f'<div class="value-zone">{value_block}</div>'
        f'<div class="odds-zone">'
        f'<div class="odds-label">ODDS</div>'
        f'<div class="odds-row">{odds_value}</div>'
        f'</div>'
        f'</div>'
    )


def summary_box(label, value):
    return (
        '<div class="summary-card">'
        f'<div class="summary-label">{label}</div>'
        f'<div class="summary-value">{value}</div>'
        '</div>'
    )


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

total_prizes_left = int(df["Available"].sum())
win_chance = round((total_prizes_left / ball_count) * 100, 2) if ball_count > 0 else 0
lose_count = max(ball_count - total_prizes_left, 0)
lose_chance = round((lose_count / ball_count) * 100, 2) if ball_count > 0 else 0

st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #F7F7F5;
    color: #3B4F38;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.block-container {
    max-width: 1360px;
    padding-top: 1.6rem;
    padding-bottom: 1.6rem;
    padding-left: 1.6rem;
    padding-right: 1.6rem;
}

.main-title {
    text-align: center;
    font-size: 64px;
    font-weight: 900;
    letter-spacing: -1.4px;
    line-height: 1.02;
    margin: 0 0 24px 0;
    color: #3B4F38;
}

.summary-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 16px;
}

.summary-card {
    border: 2.5px solid #3B4F38;
    background: rgba(255,255,255,0.92);
    border-radius: 20px;
    min-height: 108px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 14px 10px;
    box-sizing: border-box;
}

.summary-label {
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 0.9px;
    text-transform: uppercase;
    margin-bottom: 8px;
    line-height: 1.1;
    text-align: center;
    color: #4C5E49;
}

.summary-value {
    font-size: 50px;
    font-weight: 900;
    line-height: 1;
    text-align: center;
    color: #2F422C;
}

.board {
    display: grid;
    grid-template-columns: 360px minmax(0, 1fr);
    gap: 16px;
    align-items: start;
}

.left-column {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    align-items: stretch;
}

.right-column {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    align-items: start;
}

.group {
    min-width: 0;
    display: flex;
    flex-direction: column;
}

.group-title {
    border: 2.5px solid #3B4F38;
    background: #CFD4C2;
    border-radius: 16px;
    height: 72px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 10px 14px;
    font-size: 20px;
    font-weight: 900;
    line-height: 1.15;
    margin-bottom: 10px;
    box-sizing: border-box;
    color: #32452F;
    flex: 0 0 72px;
}

.group-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    grid-auto-rows: 176px;
}

.feature-card, .prize-card {
    border: 2.5px solid #3B4F38;
    background: rgba(255,255,255,0.94);
    border-radius: 22px;
    width: 100%;
    box-sizing: border-box;
    color: #3B4F38;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    justify-content: flex-start;
    overflow: hidden;
}

.feature-card {
    height: 446px;
    padding: 12px 10px 14px 10px;
}

.prize-card {
    height: 176px;
    padding: 8px 8px 10px 8px;
}

.title {
    min-height: 96px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 0 10px;
    font-size: 20px;
    font-weight: 800;
    line-height: 1.16;
    word-break: keep-all;
    overflow-wrap: anywhere;
    box-sizing: border-box;
    color: #32452F;
}

.prize-card .title {
    min-height: 50px;
    font-size: 18px;
    line-height: 1.12;
}

.value-zone {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding-top: 2px;
    min-height: 0;
}

.value-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2px;
    min-width: 0;
}

.feature-card .value {
    font-size: 86px;
    font-weight: 900;
    line-height: 0.95;
    letter-spacing: -2px;
    color: #3B4F38;
}

.prize-card .value {
    font-size: 62px;
    font-weight: 900;
    line-height: 0.95;
    letter-spacing: -1.2px;
    color: #3B4F38;
}

.qty-line {
    font-size: 36px;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.6px;
    margin-top: 8px;
    color: #3B4F38;
}

.feature-card .qty-line {
    font-size: 38px;
    margin-top: 12px;
}

.prize-card .qty-line {
    font-size: 24px;
    margin-top: 6px;
}

.odds-zone {
    min-height: 76px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex: 0 0 76px;
}

.prize-card .odds-zone {
    min-height: 42px;
    flex: 0 0 42px;
}

.odds-label {
    font-size: 13px;
    font-weight: 900;
    letter-spacing: 1.2px;
    line-height: 1;
    text-transform: uppercase;
    margin-bottom: 6px;
    color: #5A6B57;
}

.prize-card .odds-label {
    font-size: 11px;
    margin-bottom: 4px;
}

.odds-row {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 0;
}

.odds-value {
    font-size: 34px;
    font-weight: 900;
    line-height: 1;
    color: #2F422C;
}

.prize-card .odds-value {
    font-size: 18px;
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
    font-weight: 900;
}

.soldout-sub {
    font-size: 14px !important;
    font-weight: 800;
}

@media (max-width: 1180px) {
    .block-container {
        max-width: 1120px;
        padding: 1.2rem;
    }

    .main-title {
        font-size: 54px;
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
        height: 410px;
    }

    .summary-value {
        font-size: 40px;
    }

    .feature-card .value {
        font-size: 76px;
    }

    .prize-card .value {
        font-size: 58px;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Raffle Event Prize Board</div>', unsafe_allow_html=True)

summary_html = (
    '<div class="summary-row">'
    + summary_box("Total Prizes Left", total_prizes_left)
    + summary_box("Win Chance", f"{win_chance:.1f}%")
    + summary_box("Lose Chance", f"{lose_chance:.1f}%")
    + '</div>'
)
st.markdown(summary_html, unsafe_allow_html=True)

left_html = (
    '<div class="left-column">'
    + render_card("Hair Removal (1 session)", hair, large=True)
    + render_card("Korean Facial (1 session)", facial, large=True)
    + '</div>'
)

group1_html = (
    '<div class="group">'
    '<div class="group-title">80% Off MeSO Signature Treatment</div>'
    '<div class="group-grid">'
    + render_card("BB Laser", off_bb)
    + render_card("SylfirmX RF", off_sylfirm)
    + render_card("Oligio Lifting", off_oligio)
    + render_card("Ultherapy Prime", off_ultherapy)
    + '</div></div>'
)

group2_html = (
    '<div class="group">'
    '<div class="group-title">Free MeSO Signature Treatment</div>'
    '<div class="group-grid">'
    + render_card("BB Laser", free_bb)
    + render_card("SylfirmX RF", free_sylfirm)
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

import base64

def get_base64_image(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

logo_base64 = get_base64_image("logo_grin_04.png")

st.markdown(
    f"""
    <div style="display:flex; justify-content:center; margin-top:90px; margin-bottom:10px;">
        <img src="data:image/png;base64,{logo_base64}" width="230" style="opacity:0.9;" />
    </div>
    """,
    unsafe_allow_html=True
)

import time
from urllib.parse import quote

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Raffle Event Prize Board",
    layout="wide",
)

# =========================================================
# 미리보기용 자동 전환
# =========================================================
st_autorefresh(interval=1000, key="raffle_refresh")

BOARD_SECONDS = 5
NUMBERS_1_SECONDS = 5
NUMBERS_2_SECONDS = 5
CYCLE_SECONDS = BOARD_SECONDS + NUMBERS_1_SECONDS + NUMBERS_2_SECONDS

t = int(time.time()) % CYCLE_SECONDS

if t < BOARD_SECONDS:
    page = "board"
elif t < BOARD_SECONDS + NUMBERS_1_SECONDS:
    page = "numbers_1"
else:
    page = "numbers_2"

# =========================================================
# Google Sheets 설정
# =========================================================
SPREADSHEET_ID = "1oYJliCBrYC2qhAKNjGUbaTv4o6fxzpgGb8a-xSt1UOk"
BOARD_SHEET_NAME = "Prize Board"
NUMBER_SHEET_NAME = "Prize Number"


def build_sheet_csv_url(spreadsheet_id: str, sheet_name: str) -> str:
    encoded_sheet = quote(sheet_name)
    return (
        f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq"
        f"?tqx=out:csv&sheet={encoded_sheet}"
    )


BOARD_URL = build_sheet_csv_url(SPREADSHEET_ID, BOARD_SHEET_NAME)
NUMBER_URL = build_sheet_csv_url(SPREADSHEET_ID, NUMBER_SHEET_NAME)

# =========================================================
# 데이터 로드
# =========================================================
@st.cache_data(ttl=2)
def load_board_data():
    board_df = pd.read_csv(BOARD_URL)
    raw_board_df = pd.read_csv(BOARD_URL, header=None)
    return board_df, raw_board_df


@st.cache_data(ttl=2)
def load_number_data():
    return pd.read_csv(NUMBER_URL)


try:
    df, raw_df = load_board_data()
except Exception as e:
    st.error(f"Prize Board 시트를 불러오지 못했습니다: {e}")
    st.stop()

df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed", regex=True)]

for col in ["Qty", "Winners", "Available"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

for col in ["Place", "Prize", "Odds"]:
    if col in df.columns:
        df[col] = df[col].astype(str).fillna("").str.strip()

try:
    ball_count = int(pd.to_numeric(raw_df.iloc[1, 8], errors="coerce"))
    if ball_count <= 0:
        ball_count = 200
except Exception:
    ball_count = 200


# =========================================================
# 공통 함수
# =========================================================
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
            "</div>"
        )
        odds_value = f'<div class="odds-value">{item["odds"]}</div>'

    return (
        f'<div class="{card_class}">'
        f'<div class="title">{title}</div>'
        f'<div class="value-zone">{value_block}</div>'
        f'<div class="odds-zone">'
        f'<div class="odds-label">ODDS</div>'
        f'<div class="odds-row">{odds_value}</div>'
        f"</div>"
        f"</div>"
    )


def summary_box(label, value):
    return (
        '<div class="summary-card">'
        f'<div class="summary-label">{label}</div>'
        f'<div class="summary-value">{value}</div>'
        "</div>"
    )


def normalize_status(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def safe_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


# =========================================================
# Prize Number 페이지
# =========================================================
def render_number_page(start_num: int, end_num: int, title_text: str):
    try:
        number_df = load_number_data()
    except Exception as e:
        st.markdown(
            f"""
            <div class="number-page">
                <div class="main-title number-title">{title_text}</div>
                <div class="load-error-box">
                    Prize Number 시트를 불러오지 못했습니다.<br>{str(e)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    number_df.columns = [str(c).strip() for c in number_df.columns]

    required_cols = ["Number", "Prize", "Winning Status"]
    missing = [c for c in required_cols if c not in number_df.columns]
    if missing:
        st.markdown(
            f"""
            <div class="number-page">
                <div class="main-title number-title">{title_text}</div>
                <div class="load-error-box">
                    Prize Number 시트 컬럼이 맞지 않습니다.<br>
                    누락 컬럼: {", ".join(missing)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    number_df = number_df[required_cols].copy()
    number_df["Number"] = pd.to_numeric(number_df["Number"], errors="coerce")
    number_df = number_df[number_df["Number"].notna()].copy()
    number_df["Number"] = number_df["Number"].astype(int)

    number_df["Prize"] = number_df["Prize"].apply(safe_text)
    number_df["Winning Status"] = number_df["Winning Status"].apply(safe_text)

    page_df = number_df[
        (number_df["Number"] >= start_num) & (number_df["Number"] <= end_num)
    ].sort_values("Number")

    rows_html = ""

    for row_start in range(start_num, end_num + 1, 10):
        row_html = '<div class="tv-grid-row">'

        for n in range(row_start, row_start + 10):
            matched = page_df[page_df["Number"] == n]

            if matched.empty:
                prize_text = ""
                status_text = ""
                status_norm = ""
            else:
                prize_text = safe_text(matched.iloc[0]["Prize"])
                status_text = safe_text(matched.iloc[0]["Winning Status"])
                status_norm = normalize_status(status_text)

            has_prize = prize_text != ""
            is_winner = status_norm == "winner"

            classes = ["tv-cell"]

            if has_prize and not is_winner:
                classes.append("prize-active-cell")

            if is_winner:
                classes.append("winner-done-cell")

            cell_html = (
                f'<div class="{" ".join(classes)}">'
                f'<div class="cell-shine"></div>'
                f'<div class="tv-number">{n}</div>'
                f'<div class="tv-prize">{prize_text}</div>'
                f'<div class="tv-status">{status_text}</div>'
                f'</div>'
            )
            row_html += cell_html

        row_html += "</div>"
        rows_html += row_html

    board_html = f"""
    <div class="number-page">
        <div class="main-title number-title">{title_text}</div>
        <div class="tv-grid-board">{rows_html}</div>
    </div>
    """
    st.markdown(board_html, unsafe_allow_html=True)


# =========================================================
# 보드 데이터 계산
# =========================================================
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

detail_df = df[
    df["Prize"].notna()
    & (df["Prize"].astype(str).str.strip() != "")
    & (df["Place"].astype(str).str.strip() != "합계")
]

total_prizes_left = int(detail_df["Available"].sum())
win_chance = round((total_prizes_left / ball_count) * 100, 2) if ball_count > 0 else 0
lose_count = max(ball_count - total_prizes_left, 0)
lose_chance = round((lose_count / ball_count) * 100, 2) if ball_count > 0 else 0

# =========================================================
# CSS
# =========================================================
st.markdown(
    """
<style>
html, body, [class*="css"] {
    background-color: #F7F7F5;
    color: #3B4F38;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Streamlit 상단 여백 축소 */
.block-container {
    max-width: 1360px;
    padding-top: 0.55rem;
    padding-bottom: 0.55rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

/* 불필요한 기본 여백 조금 더 축소 */
div[data-testid="stAppViewContainer"] > .main {
    padding-top: 0;
}

/* 공통 타이틀 */
.main-title {
    text-align: center;
    font-size: 64px;
    font-weight: 900;
    letter-spacing: -1.4px;
    line-height: 1.02;
    margin: 0 0 24px 0;
    color: #3B4F38;
}

/* Prize Number 전용 래퍼 */
.number-page {
    height: calc(100vh - 20px);
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}

/* Prize Number 전용 타이틀 축소 */
.number-title {
    font-size: 42px;
    margin: 0 0 10px 0;
    flex: 0 0 auto;
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

/* =========================================================
   Prize Number TV Layout (스크롤 방지용 최적화)
   ========================================================= */

.tv-grid-board {
    display: flex;
    flex-direction: column;
    border: 2.5px solid #3B4F38;
    border-radius: 18px;
    overflow: hidden;
    background: rgba(255,255,255,0.90);
    box-shadow: 0 12px 28px rgba(47, 66, 44, 0.08);
    flex: 1 1 auto;
    min-height: 0;
}

.tv-grid-row {
    display: grid;
    grid-template-columns: repeat(10, 1fr);
    flex: 1 1 0;
}

.tv-cell {
    position: relative;
    min-height: 0;
    height: 100%;
    padding: 6px 5px 5px 5px;
    box-sizing: border-box;
    border-right: 1.5px solid #A7B39E;
    border-bottom: 1.5px solid #A7B39E;
    background: linear-gradient(180deg, rgba(255,255,255,0.92) 0%, rgba(249,250,247,0.96) 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    overflow: hidden;
}

.tv-grid-row .tv-cell:last-child {
    border-right: none;
}

.tv-grid-row:last-child .tv-cell {
    border-bottom: none;
}

.cell-shine {
    position: absolute;
    top: -40%;
    left: -120%;
    width: 70%;
    height: 180%;
    background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.35) 50%, rgba(255,255,255,0) 100%);
    transform: rotate(18deg);
    pointer-events: none;
    opacity: 0;
}

.tv-number {
    position: relative;
    z-index: 2;
    font-size: 25px;
    font-weight: 900;
    line-height: 1;
    color: #2F422C;
    margin-bottom: 5px;
}

.tv-prize {
    position: relative;
    z-index: 2;
    font-size: 10px;
    font-weight: 800;
    line-height: 1.1;
    color: #32452F;
    text-align: center;
    margin-bottom: 4px;
    word-break: keep-all;
    overflow-wrap: anywhere;
    min-height: 24px;
}

.tv-status {
    position: relative;
    z-index: 2;
    margin-top: auto;
    font-size: 9px;
    font-weight: 900;
    line-height: 1.05;
    letter-spacing: 0.2px;
    color: #6A7B66;
    text-align: center;
    min-height: 11px;
}

/* 경품이 남아 있는 칸 */
.prize-active-cell {
    border: 3px solid #2F422C !important;
    z-index: 3;
    transform: scale(1.015);
    box-shadow: 0 0 0 3px rgba(207, 220, 194, 0.82), 0 0 20px rgba(101, 142, 90, 0.35);
    animation: activePrizePop 1.6s ease-in-out infinite;
    background:
        radial-gradient(circle at top, rgba(255,255,255,0.92), rgba(255,255,255,0) 35%),
        linear-gradient(180deg, #E6F1DE 0%, #D9EAD0 100%);
}

.prize-active-cell .cell-shine {
    opacity: 1;
    animation: sweepShine 1.8s linear infinite;
}

.prize-active-cell .tv-number {
    font-size: 29px;
    color: #1F351D;
}

.prize-active-cell .tv-status {
    color: #234720;
}

.prize-active-cell::after {
    content: "★";
    position: absolute;
    top: 4px;
    right: 6px;
    font-size: 14px;
    font-weight: 900;
    color: #2F422C;
    animation: twinkle 1.1s ease-in-out infinite;
}

/* 이미 당첨된 번호 */
.winner-done-cell {
    background: linear-gradient(180deg, #E3E5E0 0%, #D6D9D2 100%);
    border-color: #B3BBB0 !important;
    box-shadow: none !important;
    transform: none !important;
    animation: none !important;
}

.winner-done-cell .cell-shine {
    opacity: 0 !important;
    animation: none !important;
}

.winner-done-cell .tv-number {
    color: #5F695C;
    font-size: 27px;
}

.winner-done-cell .tv-prize {
    color: #667063;
}

.winner-done-cell .tv-status {
    color: #7A8477;
}

/* TV 송출용이므로 하단 로고 숨김 */
.logo-wrap {
    display: none;
}

.load-error-box {
    text-align: center;
    font-size: 20px;
    color: #8B0000;
    margin-top: 24px;
    padding: 24px;
    border: 2px solid #C7B0B0;
    border-radius: 16px;
    background: #FFF7F7;
}

@keyframes sweepShine {
    0% { left: -120%; }
    100% { left: 155%; }
}

@keyframes activePrizePop {
    0%, 100% { transform: scale(1.015); }
    50% { transform: scale(1.03); }
}

@keyframes twinkle {
    0%, 100% { transform: scale(0.9); opacity: 0.7; }
    50% { transform: scale(1.12); opacity: 1; }
}

@media (max-width: 1180px) {
    .block-container {
        max-width: 1120px;
        padding: 0.7rem;
    }

    .main-title {
        font-size: 52px;
    }

    .number-title {
        font-size: 38px;
        margin-bottom: 8px;
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

    .tv-grid-row {
        grid-template-columns: repeat(10, 1fr);
    }

    .tv-number {
        font-size: 23px;
    }

    .tv-prize {
        font-size: 10px;
    }

    .tv-status {
        font-size: 9px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# 페이지 렌더링
# =========================================================
if page == "board":
    st.markdown('<div class="main-title">Raffle Event Prize Board</div>', unsafe_allow_html=True)

    summary_html = (
        '<div class="summary-row">'
        + summary_box("Total Prizes Left", total_prizes_left)
        + summary_box("Win Chance", f"{win_chance:.1f}%")
        + summary_box("Lose Chance", f"{lose_chance:.1f}%")
        + "</div>"
    )
    st.markdown(summary_html, unsafe_allow_html=True)

    left_html = (
        '<div class="left-column">'
        + render_card("Hair Removal (1 session)", hair, large=True)
        + render_card("Korean Facial (1 session)", facial, large=True)
        + "</div>"
    )

    group1_html = (
        '<div class="group">'
        '<div class="group-title">80% Off MeSO Signature Treatment</div>'
        '<div class="group-grid">'
        + render_card("BB Laser", off_bb)
        + render_card("SylfirmX RF", off_sylfirm)
        + render_card("Oligio Lifting", off_oligio)
        + render_card("Ultherapy Prime", off_ultherapy)
        + "</div></div>"
    )

    group2_html = (
        '<div class="group">'
        '<div class="group-title">Free MeSO Signature Treatment</div>'
        '<div class="group-grid">'
        + render_card("BB Laser", free_bb)
        + render_card("SylfirmX RF", free_sylfirm)
        + render_card("Oligio Lifting", free_oligio)
        + render_card("Ultherapy Prime", free_ultherapy)
        + "</div></div>"
    )

    right_html = (
        '<div class="right-column">'
        + group1_html
        + group2_html
        + "</div>"
    )

    board_html = (
        '<div class="board">'
        + left_html
        + right_html
        + "</div>"
    )

    st.markdown(board_html, unsafe_allow_html=True)

elif page == "numbers_1":
    render_number_page(1, 100, "Prize Number 1 - 100")

elif page == "numbers_2":
    render_number_page(101, 200, "Prize Number 101 - 200")

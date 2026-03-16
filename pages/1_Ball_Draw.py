import random
import time
from urllib.parse import quote

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Raffle Ball Draw",
    layout="wide",
)

# =========================================================
# 기본 설정
# =========================================================
SPREADSHEET_ID = "1oYJliCBrYC2qhAKNjGUbaTv4o6fxzpgGb8a-xSt1UOk"
NUMBER_SHEET_NAME = "Prize Number"

ROLL_REFRESH_MS = 120   # 번호 바뀌는 속도(ms)
APP_TITLE = "Raffle Ball Draw"

# =========================================================
# Google Sheets CSV URL
# =========================================================
def build_sheet_csv_url(spreadsheet_id: str, sheet_name: str) -> str:
    encoded_sheet = quote(sheet_name)
    return (
        f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq"
        f"?tqx=out:csv&sheet={encoded_sheet}"
    )


NUMBER_URL = build_sheet_csv_url(SPREADSHEET_ID, NUMBER_SHEET_NAME)

# =========================================================
# 데이터 로드
# =========================================================
@st.cache_data(ttl=2)
def load_number_data():
    df = pd.read_csv(NUMBER_URL)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def safe_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def normalize_status(value) -> str:
    return safe_text(value).lower()


# =========================================================
# 세션 상태 초기화
# =========================================================
if "rolling" not in st.session_state:
    st.session_state.rolling = False

if "display_number" not in st.session_state:
    st.session_state.display_number = None

if "display_prize" not in st.session_state:
    st.session_state.display_prize = ""

if "last_winner_number" not in st.session_state:
    st.session_state.last_winner_number = None

if "last_winner_prize" not in st.session_state:
    st.session_state.last_winner_prize = ""

if "session_drawn_numbers" not in st.session_state:
    st.session_state.session_drawn_numbers = []

if "history" not in st.session_state:
    st.session_state.history = []

# rolling 중일 때만 자동 새로고침
if st.session_state.rolling:
    st_autorefresh(interval=ROLL_REFRESH_MS, key="raffle_ball_refresh")

# =========================================================
# 데이터 준비
# =========================================================
try:
    number_df = load_number_data()
except Exception as e:
    st.error(f"Prize Number 시트를 불러오지 못했습니다: {e}")
    st.stop()

required_cols = ["Number", "Prize", "Winning Status"]
missing = [c for c in required_cols if c not in number_df.columns]
if missing:
    st.error(f"필수 컬럼이 없습니다: {', '.join(missing)}")
    st.stop()

number_df = number_df[required_cols].copy()
number_df["Number"] = pd.to_numeric(number_df["Number"], errors="coerce")
number_df = number_df[number_df["Number"].notna()].copy()
number_df["Number"] = number_df["Number"].astype(int)
number_df["Prize"] = number_df["Prize"].apply(safe_text)
number_df["Winning Status"] = number_df["Winning Status"].apply(safe_text)

# 시트에서 이미 Winner 처리된 번호 제외
base_pool_df = number_df[
    ~number_df["Winning Status"].apply(normalize_status).eq("winner")
].copy()

# 현재 앱 세션에서 이미 뽑은 번호도 제외
remaining_df = base_pool_df[
    ~base_pool_df["Number"].isin(st.session_state.session_drawn_numbers)
].copy()

remaining_df = remaining_df.sort_values("Number")

# rolling 중이면 화면 번호를 계속 랜덤하게 갱신
if st.session_state.rolling and not remaining_df.empty:
    preview_row = remaining_df.sample(1).iloc[0]
    st.session_state.display_number = int(preview_row["Number"])
    st.session_state.display_prize = safe_text(preview_row["Prize"])

# =========================================================
# 액션 함수
# =========================================================
def start_roll():
    if remaining_df.empty:
        return

    st.session_state.rolling = True
    preview_row = remaining_df.sample(1).iloc[0]
    st.session_state.display_number = int(preview_row["Number"])
    st.session_state.display_prize = safe_text(preview_row["Prize"])


def stop_and_draw():
    if remaining_df.empty:
        st.session_state.rolling = False
        return

    winner_row = remaining_df.sample(1).iloc[0]
    winner_number = int(winner_row["Number"])
    winner_prize = safe_text(winner_row["Prize"])

    st.session_state.rolling = False
    st.session_state.display_number = winner_number
    st.session_state.display_prize = winner_prize
    st.session_state.last_winner_number = winner_number
    st.session_state.last_winner_prize = winner_prize

    if winner_number not in st.session_state.session_drawn_numbers:
        st.session_state.session_drawn_numbers.append(winner_number)

    st.session_state.history.insert(
        0,
        {
            "Number": winner_number,
            "Prize": winner_prize,
            "Draw Time": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
    )


def undo_last_draw():
    if not st.session_state.history:
        return

    last = st.session_state.history.pop(0)
    last_number = int(last["Number"])

    if last_number in st.session_state.session_drawn_numbers:
        st.session_state.session_drawn_numbers.remove(last_number)

    st.session_state.last_winner_number = None
    st.session_state.last_winner_prize = ""
    st.session_state.display_number = None
    st.session_state.display_prize = ""


def reset_session_draws():
    st.session_state.rolling = False
    st.session_state.display_number = None
    st.session_state.display_prize = ""
    st.session_state.last_winner_number = None
    st.session_state.last_winner_prize = ""
    st.session_state.session_drawn_numbers = []
    st.session_state.history = []


# =========================================================
# CSS
# =========================================================
st.markdown(
    """
    <style>
    html, body {
        background: #F7F7F5;
        color: #2F422C;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 0.6rem;
        padding-bottom: 0.8rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .main-title {
        text-align: center;
        font-size: 54px;
        font-weight: 900;
        line-height: 1.05;
        letter-spacing: -1.2px;
        margin-bottom: 18px;
        color: #2F422C;
    }

    .top-stats {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-bottom: 18px;
    }

    .stat-card {
        background: rgba(255,255,255,0.95);
        border: 2.5px solid #3B4F38;
        border-radius: 18px;
        padding: 16px 10px;
        text-align: center;
    }

    .stat-label {
        font-size: 15px;
        font-weight: 800;
        text-transform: uppercase;
        color: #52634F;
        margin-bottom: 8px;
    }

    .stat-value {
        font-size: 42px;
        font-weight: 900;
        line-height: 1;
        color: #2F422C;
    }

    .draw-layout {
        display: grid;
        grid-template-columns: 1.35fr 0.65fr;
        gap: 16px;
        align-items: stretch;
    }

    .draw-panel, .side-panel {
        background: rgba(255,255,255,0.95);
        border: 2.5px solid #3B4F38;
        border-radius: 24px;
        box-sizing: border-box;
    }

    .draw-panel {
        min-height: 680px;
        padding: 24px 24px 22px 24px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .side-panel {
        min-height: 680px;
        padding: 18px 18px 16px 18px;
        overflow: hidden;
    }

    .ball-stage {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 12px 0 8px 0;
    }

    .ball-wrap {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 18px;
        width: 100%;
    }

    .ball {
        width: 360px;
        height: 360px;
        border-radius: 50%;
        border: 8px solid #2F422C;
        background:
            radial-gradient(circle at 30% 28%, #FFFFFF 0%, #F5FAF1 30%, #DDEAD5 68%, #C5D8BB 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow:
            inset 0 12px 22px rgba(255,255,255,0.75),
            inset 0 -14px 24px rgba(47,66,44,0.10),
            0 18px 40px rgba(47,66,44,0.12);
        position: relative;
    }

    .ball::before {
        content: "";
        position: absolute;
        top: 42px;
        left: 70px;
        width: 120px;
        height: 62px;
        border-radius: 50%;
        background: rgba(255,255,255,0.65);
        transform: rotate(-18deg);
    }

    .ball-number {
        font-size: 120px;
        font-weight: 900;
        line-height: 1;
        color: #21351F;
        letter-spacing: -4px;
    }

    .rolling .ball {
        animation: pulseBall 0.55s ease-in-out infinite;
    }

    .rolling .ball-number {
        animation: flickerNum 0.18s linear infinite;
    }

    .prize-box {
        width: 100%;
        min-height: 110px;
        border: 2px solid #B6C3AE;
        border-radius: 18px;
        background: #FAFCF8;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 14px 16px;
        text-align: center;
    }

    .prize-label {
        font-size: 16px;
        font-weight: 800;
        color: #596956;
        margin-bottom: 8px;
        text-transform: uppercase;
    }

    .prize-value {
        font-size: 34px;
        font-weight: 900;
        line-height: 1.12;
        color: #2F422C;
        word-break: keep-all;
        overflow-wrap: anywhere;
    }

    .winner-banner {
        margin-top: 14px;
        width: 100%;
        border: 2.5px solid #2F422C;
        border-radius: 18px;
        background: linear-gradient(180deg, #EAF5E3 0%, #DCEBD3 100%);
        padding: 16px 16px;
        text-align: center;
    }

    .winner-banner-label {
        font-size: 15px;
        font-weight: 800;
        color: #4F624B;
        margin-bottom: 8px;
        text-transform: uppercase;
    }

    .winner-banner-value {
        font-size: 30px;
        font-weight: 900;
        color: #1F351D;
        line-height: 1.1;
    }

    .history-title {
        font-size: 24px;
        font-weight: 900;
        line-height: 1.1;
        margin-bottom: 12px;
        text-align: center;
        color: #2F422C;
    }

    .history-wrap {
        height: 600px;
        overflow-y: auto;
        padding-right: 4px;
    }

    .history-card {
        border: 2px solid #C8D1C2;
        border-radius: 16px;
        background: #FBFCFA;
        padding: 12px 12px;
        margin-bottom: 10px;
    }

    .history-number {
        font-size: 28px;
        font-weight: 900;
        color: #21351F;
        margin-bottom: 4px;
    }

    .history-prize {
        font-size: 16px;
        font-weight: 800;
        color: #3E533B;
        line-height: 1.15;
        margin-bottom: 6px;
        word-break: keep-all;
        overflow-wrap: anywhere;
    }

    .history-time {
        font-size: 12px;
        color: #6D7B69;
        font-weight: 700;
    }

    @keyframes pulseBall {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.03); }
    }

    @keyframes flickerNum {
        0% { opacity: 1; }
        50% { opacity: 0.82; }
        100% { opacity: 1; }
    }

    @media (max-width: 1200px) {
        .top-stats {
            grid-template-columns: 1fr;
        }

        .draw-layout {
            grid-template-columns: 1fr;
        }

        .draw-panel, .side-panel {
            min-height: auto;
        }

        .ball {
            width: 280px;
            height: 280px;
        }

        .ball-number {
            font-size: 94px;
        }

        .prize-value {
            font-size: 28px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# 상단 타이틀
# =========================================================
st.markdown(f'<div class="main-title">{APP_TITLE}</div>', unsafe_allow_html=True)

total_count = len(number_df)
already_winner_count = len(
    number_df[number_df["Winning Status"].apply(normalize_status) == "winner"]
)
remaining_count = len(remaining_df)

stats_html = f"""
<div class="top-stats">
    <div class="stat-card">
        <div class="stat-label">Total Numbers</div>
        <div class="stat-value">{total_count}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Already Winner in Sheet</div>
        <div class="stat-value">{already_winner_count}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Remaining in This Draw</div>
        <div class="stat-value">{remaining_count}</div>
    </div>
</div>
"""
st.markdown(stats_html, unsafe_allow_html=True)

# =========================================================
# 버튼
# =========================================================
btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 1])

with btn_col1:
    if st.button("START ROLLING", use_container_width=True, disabled=remaining_df.empty):
        start_roll()
        st.rerun()

with btn_col2:
    if st.button(
        "STOP & DRAW",
        use_container_width=True,
        disabled=(not st.session_state.rolling and remaining_df.empty),
    ):
        stop_and_draw()
        st.rerun()

with btn_col3:
    if st.button(
        "UNDO LAST DRAW",
        use_container_width=True,
        disabled=(len(st.session_state.history) == 0),
    ):
        undo_last_draw()
        st.rerun()

with btn_col4:
    if st.button("RESET SESSION", use_container_width=True):
        reset_session_draws()
        st.rerun()

# =========================================================
# 메인 화면
# =========================================================
ball_number = st.session_state.display_number
ball_prize = st.session_state.display_prize
rolling_class = "rolling" if st.session_state.rolling else ""

display_number = "?" if ball_number is None else str(ball_number)
display_prize = "Ready to draw" if ball_prize == "" else ball_prize

history_html = ""
for item in st.session_state.history:
    history_html += f"""
    <div class="history-card">
        <div class="history-number">No. {item['Number']}</div>
        <div class="history-prize">{item['Prize']}</div>
        <div class="history-time">{item['Draw Time']}</div>
    </div>
    """

latest_winner_number = (
    f"No. {st.session_state.last_winner_number}"
    if st.session_state.last_winner_number is not None
    else "-"
)
latest_winner_prize = st.session_state.last_winner_prize if st.session_state.last_winner_prize else ""

main_html = f"""
<div class="draw-layout">
    <div class="draw-panel {rolling_class}">
        <div class="ball-stage">
            <div class="ball-wrap">
                <div class="ball">
                    <div class="ball-number">{display_number}</div>
                </div>

                <div class="prize-box">
                    <div class="prize-label">Prize</div>
                    <div class="prize-value">{display_prize}</div>
                </div>

                <div class="winner-banner">
                    <div class="winner-banner-label">Latest Winner</div>
                    <div class="winner-banner-value">
                        {latest_winner_number}
                        <br>
                        {latest_winner_prize}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="side-panel">
        <div class="history-title">Draw History</div>
        <div class="history-wrap">
            {history_html if history_html else '<div style="text-align:center; color:#6D7B69; font-weight:700; padding-top:24px;">No draw history yet</div>'}
        </div>
    </div>
</div>
"""
st.markdown(main_html, unsafe_allow_html=True)

# =========================================================
# 세션 추첨 결과 다운로드
# =========================================================
if st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history)
    st.download_button(
        label="Download Session Result CSV",
        data=history_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="raffle_draw_history.csv",
        mime="text/csv",
        use_container_width=True,
    )

# =========================================================
# 안내
# =========================================================
st.info(
    "이 버전은 Google Sheet를 읽어와서 추첨만 진행합니다. "
    "즉, 화면에서 뽑힌 결과를 Google Sheet의 Winning Status에 자동 반영하지는 않습니다."
)

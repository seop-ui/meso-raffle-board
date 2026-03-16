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

ROLL_REFRESH_MS = 120
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

if "last_winner_ball_color" not in st.session_state:
    st.session_state.last_winner_ball_color = "green"

if "session_drawn_numbers" not in st.session_state:
    st.session_state.session_drawn_numbers = []

if "history" not in st.session_state:
    st.session_state.history = []

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


def get_ball_color(prize_text: str, winning_status_text: str) -> str:
    status_norm = normalize_status(winning_status_text)
    has_prize = safe_text(prize_text) != ""

    if has_prize and status_norm == "not a winner":
        return "green"
    return "gray"


# 전체 개수
total_count = len(number_df)

# 현재 시트 기준 winner 개수
already_winner_count = len(
    number_df[number_df["Winning Status"].apply(normalize_status) == "winner"]
)

# 현재 앱 세션에서 이미 뽑은 번호 제외
remaining_df = number_df[
    ~number_df["Number"].isin(st.session_state.session_drawn_numbers)
].copy()

remaining_df = remaining_df.sort_values("Number")

remaining_count = len(remaining_df)

# rolling 중이면 화면 번호를 계속 랜덤하게 갱신
if st.session_state.rolling and not remaining_df.empty:
    preview_row = remaining_df.sample(1).iloc[0]
    st.session_state.display_number = int(preview_row["Number"])
    st.session_state.display_prize = safe_text(preview_row["Prize"])
    st.session_state.last_winner_ball_color = get_ball_color(
        preview_row["Prize"],
        preview_row["Winning Status"],
    )

# =========================================================
# 액션 함수
# =========================================================
def start_roll():
    if remaining_df.empty:
        return

    preview_row = remaining_df.sample(1).iloc[0]
    st.session_state.rolling = True
    st.session_state.display_number = int(preview_row["Number"])
    st.session_state.display_prize = safe_text(preview_row["Prize"])
    st.session_state.last_winner_ball_color = get_ball_color(
        preview_row["Prize"],
        preview_row["Winning Status"],
    )


def stop_and_draw():
    if remaining_df.empty:
        st.session_state.rolling = False
        return

    winner_row = remaining_df.sample(1).iloc[0]
    winner_number = int(winner_row["Number"])
    winner_prize = safe_text(winner_row["Prize"])
    winner_status = safe_text(winner_row["Winning Status"])
    winner_ball_color = get_ball_color(winner_prize, winner_status)

    st.session_state.rolling = False
    st.session_state.display_number = winner_number
    st.session_state.display_prize = winner_prize if winner_prize else "No Prize"
    st.session_state.last_winner_number = winner_number
    st.session_state.last_winner_prize = winner_prize if winner_prize else "No Prize"
    st.session_state.last_winner_ball_color = winner_ball_color

    if winner_number not in st.session_state.session_drawn_numbers:
        st.session_state.session_drawn_numbers.append(winner_number)

    st.session_state.history.insert(
        0,
        {
            "Number": winner_number,
            "Prize": winner_prize if winner_prize else "No Prize",
            "Winning Status": winner_status,
            "Ball Color": winner_ball_color,
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
    st.session_state.last_winner_ball_color = "green"


def reset_session_draws():
    st.session_state.rolling = False
    st.session_state.display_number = None
    st.session_state.display_prize = ""
    st.session_state.last_winner_number = None
    st.session_state.last_winner_prize = ""
    st.session_state.last_winner_ball_color = "green"
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
        max-width: 1420px;
        padding-top: 0.4rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .main-title {
        text-align: center;
        font-size: 54px;
        font-weight: 900;
        line-height: 1.05;
        letter-spacing: -1.2px;
        margin-bottom: 16px;
        color: #2F422C;
    }

    .stat-card {
        background: rgba(255,255,255,0.96);
        border: 2.5px solid #3B4F38;
        border-radius: 20px;
        padding: 14px 10px;
        text-align: center;
        min-height: 95px;
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

    .panel-box {
        background: rgba(255,255,255,0.96);
        border: 2.5px solid #3B4F38;
        border-radius: 24px;
        padding: 24px 20px 20px 20px;
        min-height: 760px;
    }

    .ball-wrap {
        display: flex;
        justify-content: center;
        margin-top: 10px;
        margin-bottom: 18px;
    }

    .ball-green, .ball-gray {
        width: 320px;
        height: 320px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        box-shadow:
            inset 0 12px 22px rgba(255,255,255,0.75),
            inset 0 -14px 24px rgba(47,66,44,0.10),
            0 18px 40px rgba(47,66,44,0.12);
    }

    .ball-green {
        border: 8px solid #2F422C;
        background:
            radial-gradient(circle at 30% 28%, #FFFFFF 0%, #F5FAF1 30%, #DDEAD5 68%, #C5D8BB 100%);
    }

    .ball-gray {
        border: 8px solid #6F776E;
        background:
            radial-gradient(circle at 30% 28%, #FFFFFF 0%, #F1F2F1 28%, #DDDFDD 68%, #C9CDCA 100%);
    }

    .ball-green::before, .ball-gray::before {
        content: "";
        position: absolute;
        top: 40px;
        left: 68px;
        width: 118px;
        height: 60px;
        border-radius: 50%;
        background: rgba(255,255,255,0.62);
        transform: rotate(-18deg);
    }

    .ball-number {
        font-size: 112px;
        font-weight: 900;
        line-height: 1;
        letter-spacing: -4px;
    }

    .ball-green .ball-number {
        color: #21351F;
    }

    .ball-gray .ball-number {
        color: #5E655D;
    }

    .rolling .ball-green,
    .rolling .ball-gray {
        animation: pulseBall 0.55s ease-in-out infinite;
    }

    .rolling .ball-number {
        animation: flickerNum 0.18s linear infinite;
    }

    .info-card {
        background: #FAFCF8;
        border: 2px solid #B6C3AE;
        border-radius: 18px;
        padding: 16px 14px;
        text-align: center;
        margin-top: 12px;
    }

    .info-label {
        font-size: 15px;
        font-weight: 800;
        color: #596956;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .info-value {
        font-size: 30px;
        font-weight: 900;
        line-height: 1.15;
        color: #2F422C;
        word-break: keep-all;
        overflow-wrap: anywhere;
    }

    .history-title {
        font-size: 26px;
        font-weight: 900;
        line-height: 1.1;
        margin-bottom: 14px;
        text-align: center;
        color: #2F422C;
    }

    .history-card {
        border: 2px solid #C8D1C2;
        border-radius: 16px;
        background: #FBFCFA;
        padding: 12px;
        margin-bottom: 10px;
    }

    .history-number {
        font-size: 26px;
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
    }

    .history-meta {
        font-size: 12px;
        color: #6D7B69;
        font-weight: 700;
    }

    .empty-history {
        text-align: center;
        color: #6D7B69;
        font-weight: 700;
        padding-top: 24px;
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
        .ball-green, .ball-gray {
            width: 260px;
            height: 260px;
        }

        .ball-number {
            font-size: 90px;
        }

        .info-value {
            font-size: 24px;
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

# =========================================================
# 상단 통계
# =========================================================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">Total Numbers</div>
            <div class="stat-value">{total_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">Already Winner in Sheet</div>
            <div class="stat-value">{already_winner_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">Remaining in This Draw</div>
            <div class="stat-value">{remaining_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# =========================================================
# 버튼
# =========================================================
btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 1])

with btn_col1:
    if st.button("START ROLLING", use_container_width=True, disabled=remaining_df.empty):
        start_roll()
        st.rerun()

with btn_col2:
    if st.button("STOP & DRAW", use_container_width=True, disabled=(not st.session_state.rolling and remaining_df.empty)):
        stop_and_draw()
        st.rerun()

with btn_col3:
    if st.button("UNDO LAST DRAW", use_container_width=True, disabled=(len(st.session_state.history) == 0)):
        undo_last_draw()
        st.rerun()

with btn_col4:
    if st.button("RESET SESSION", use_container_width=True):
        reset_session_draws()
        st.rerun()

st.write("")

# =========================================================
# 메인 화면
# =========================================================
left_col, right_col = st.columns([1.35, 0.65])

ball_number = st.session_state.display_number
ball_prize = st.session_state.display_prize
display_number = "?" if ball_number is None else str(ball_number)
display_prize = "Ready to draw" if ball_prize == "" else ball_prize

if ball_number is None:
    current_ball_color = "green"
else:
    current_ball_color = st.session_state.last_winner_ball_color

rolling_class = "rolling" if st.session_state.rolling else ""
ball_class = "ball-green" if current_ball_color == "green" else "ball-gray"

with left_col:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="ball-wrap {rolling_class}">
            <div class="{ball_class}">
                <div class="ball-number">{display_number}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-label">Prize</div>
            <div class="info-value">{display_prize}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    latest_winner_number = (
        f"No. {st.session_state.last_winner_number}"
        if st.session_state.last_winner_number is not None
        else "-"
    )
    latest_winner_prize = (
        st.session_state.last_winner_prize
        if st.session_state.last_winner_prize
        else ""
    )

    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-label">Latest Winner</div>
            <div class="info-value">{latest_winner_number}<br>{latest_winner_prize}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown('<div class="history-title">Draw History</div>', unsafe_allow_html=True)

    if st.session_state.history:
        for item in st.session_state.history:
            color_text = "Green Ball" if item["Ball Color"] == "green" else "Gray Ball"
            st.markdown(
                f"""
                <div class="history-card">
                    <div class="history-number">No. {item["Number"]}</div>
                    <div class="history-prize">{item["Prize"]}</div>
                    <div class="history-meta">{item["Winning Status"]} · {color_text}</div>
                    <div class="history-meta">{item["Draw Time"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<div class="empty-history">No draw history yet</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

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

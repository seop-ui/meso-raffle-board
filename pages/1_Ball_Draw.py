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
PRIZEBOARD_SHEET_NAME = "Prize Board"

# STOP 버튼 반응이 너무 안 좋으면 350 -> 500으로 올려도 됨
ROLL_REFRESH_MS = 350

# 하단 안내 문구 폰트 크기
NOTICE_FONT_SIZE_PX = 22

APP_TITLE = "Raffle Ball Draw"

NOTICE_TEXT = (
    "The rolling ball animation is for visual effect only. "
    "The actual number is randomly selected when the draw stops."
)

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
PRIZEBOARD_URL = build_sheet_csv_url(SPREADSHEET_ID, PRIZEBOARD_SHEET_NAME)

# =========================================================
# 데이터 로드
# =========================================================
@st.cache_data(ttl=2)
def load_number_data():
    df = pd.read_csv(NUMBER_URL)
    df.columns = [str(c).strip() for c in df.columns]
    return df


@st.cache_data(ttl=2)
def load_prizeboard_raw():
    return pd.read_csv(PRIZEBOARD_URL, header=None)


def safe_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def normalize_status(value) -> str:
    return safe_text(value).lower()


def format_metric(value) -> str:
    text = safe_text(value)
    return text if text != "" else "-"


def get_ball_color(prize_text: str, winning_status_text: str) -> str:
    status_norm = normalize_status(winning_status_text)
    has_prize = safe_text(prize_text) != ""

    # 상품 있음 + Not a Winner = 초록공
    if has_prize and status_norm == "not a winner":
        return "green"

    # 상품 없거나 winner = 회색공
    return "gray"


# =========================================================
# 세션 상태 초기화
# =========================================================
if "rolling" not in st.session_state:
    st.session_state.rolling = False

if "display_number" not in st.session_state:
    st.session_state.display_number = None

if "display_prize" not in st.session_state:
    st.session_state.display_prize = ""

if "display_ball_color" not in st.session_state:
    st.session_state.display_ball_color = "green"

if "session_drawn_numbers" not in st.session_state:
    st.session_state.session_drawn_numbers = []

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

total_count = len(number_df)

# 이미 이번 세션에서 뽑힌 번호는 제외
remaining_df = number_df[
    ~number_df["Number"].isin(st.session_state.session_drawn_numbers)
].copy()

remaining_df = remaining_df.sort_values("Number")

# Prize Board!E14, F14 읽기
try:
    prizeboard_raw = load_prizeboard_raw()
    remaining_prizes = format_metric(prizeboard_raw.iloc[13, 4])      # E14
    winning_probability = format_metric(prizeboard_raw.iloc[13, 5])   # F14
except Exception:
    remaining_prizes = "-"
    winning_probability = "-"

# rolling 중이면 화면 번호만 계속 바뀜 (시각 효과)
if st.session_state.rolling and not remaining_df.empty:
    preview_row = remaining_df.sample(1).iloc[0]
    st.session_state.display_number = int(preview_row["Number"])
    st.session_state.display_prize = safe_text(preview_row["Prize"])
    st.session_state.display_ball_color = get_ball_color(
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
    st.session_state.display_ball_color = get_ball_color(
        preview_row["Prize"],
        preview_row["Winning Status"],
    )


def stop_and_draw():
    if remaining_df.empty:
        st.session_state.rolling = False
        return

    # 실제 당첨 번호는 STOP 누르는 순간 랜덤 추첨
    winner_row = remaining_df.sample(1).iloc[0]
    winner_number = int(winner_row["Number"])
    winner_prize = safe_text(winner_row["Prize"])
    winner_status = safe_text(winner_row["Winning Status"])
    winner_ball_color = get_ball_color(winner_prize, winner_status)

    st.session_state.rolling = False
    st.session_state.display_number = winner_number
    st.session_state.display_prize = winner_prize if winner_prize else "No Prize"
    st.session_state.display_ball_color = winner_ball_color

    if winner_number not in st.session_state.session_drawn_numbers:
        st.session_state.session_drawn_numbers.append(winner_number)


def reset_session_draws():
    st.session_state.rolling = False
    st.session_state.display_number = None
    st.session_state.display_prize = ""
    st.session_state.display_ball_color = "green"
    st.session_state.session_drawn_numbers = []


# =========================================================
# CSS
# =========================================================
st.markdown(
    f"""
    <style>
    html, body {{
        background: #F7F7F5;
        color: #2F422C;
    }}

    .block-container {{
        max-width: 1500px;
        padding-top: 0.35rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }}

    .main-title {{
        text-align: center;
        font-size: 54px;
        font-weight: 900;
        line-height: 1.05;
        letter-spacing: -1.2px;
        margin-top: 30px;
        margin-bottom: 16px;
        color: #2F422C;
    }}

    .stat-card {{
        background: rgba(255,255,255,0.96);
        border: 2.5px solid #3B4F38;
        border-radius: 20px;
        padding: 14px 10px;
        text-align: center;
        min-height: 95px;
    }}

    .stat-label {{
        font-size: 15px;
        font-weight: 800;
        text-transform: uppercase;
        color: #52634F;
        margin-bottom: 8px;
    }}

    .stat-value {{
        font-size: 42px;
        font-weight: 900;
        line-height: 1;
        color: #2F422C;
    }}

    .main-panel {{
        background: transparent;
        border: none;
        border-radius: 0;
        padding: 8px 0 0 0;
        min-height: 0;
    }}

    .ball-wrap {{
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 10px;
        margin-bottom: 22px;
    }}

    .ball-green, .ball-gray {{
        width: 420px;
        height: 420px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        box-shadow:
            inset 0 14px 24px rgba(255,255,255,0.75),
            inset 0 -16px 28px rgba(47,66,44,0.10),
            0 20px 42px rgba(47,66,44,0.12);
    }}

    .ball-green {{
        border: 10px solid #2F422C;
        background:
            radial-gradient(circle at 30% 28%, #FFFFFF 0%, #F5FAF1 30%, #DDEAD5 68%, #C5D8BB 100%);
    }}

    .ball-gray {{
        border: 10px solid #6F776E;
        background:
            radial-gradient(circle at 30% 28%, #FFFFFF 0%, #F1F2F1 28%, #DDDFDD 68%, #C9CDCA 100%);
    }}

    .ball-green::before, .ball-gray::before {{
        content: "";
        position: absolute;
        top: 52px;
        left: 92px;
        width: 150px;
        height: 76px;
        border-radius: 50%;
        background: rgba(255,255,255,0.62);
        transform: rotate(-18deg);
    }}

    .ball-number {{
        font-size: 150px;
        font-weight: 900;
        line-height: 1;
        letter-spacing: -5px;
    }}

    .ball-green .ball-number {{
        color: #21351F;
    }}

    .ball-gray .ball-number {{
        color: #5E655D;
    }}

    .rolling .ball-green,
    .rolling .ball-gray {{
        animation: pulseBall 0.55s ease-in-out infinite;
    }}

    .rolling .ball-number {{
        animation: flickerNum 0.18s linear infinite;
    }}

    .bottom-card {{
        background: #FAFCF8;
        border: 2px solid #B6C3AE;
        border-radius: 20px;
        padding: 18px 16px;
        text-align: center;
        margin-top: 14px;
    }}

    .bottom-label {{
        font-size: 16px;
        font-weight: 800;
        color: #596956;
        text-transform: uppercase;
        margin-bottom: 10px;
    }}

    .bottom-value {{
        font-size: 34px;
        font-weight: 900;
        line-height: 1.15;
        color: #2F422C;
        word-break: keep-all;
        overflow-wrap: anywhere;
    }}

    .notice-text {{
        text-align: center;
        margin-top: 30px;
        font-size: {NOTICE_FONT_SIZE_PX}px;
        font-weight: 600;
        line-height: 1.35;
        color: #6B7468;
    }}

    @keyframes pulseBall {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.03); }}
    }}

    @keyframes flickerNum {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.82; }}
        100% {{ opacity: 1; }}
    }}

    @media (max-width: 1200px) {{
        .ball-green, .ball-gray {{
            width: 300px;
            height: 300px;
        }}

        .ball-number {{
            font-size: 104px;
        }}

        .bottom-value {{
            font-size: 28px;
        }}

        .notice-text {{
            font-size: 22px;
        }}
    }}
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
            <div class="stat-label">Remaining Prizes</div>
            <div class="stat-value">{remaining_prizes}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">Winning Probability</div>
            <div class="stat-value">{winning_probability}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# =========================================================
# 버튼
# =========================================================
btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])

with btn_col1:
    if st.button("START", use_container_width=True, disabled=remaining_df.empty):
        start_roll()
        st.rerun()

with btn_col2:
    if st.button("DRAW", use_container_width=True):
        stop_and_draw()
        st.rerun()

with btn_col3:
    if st.button("RESET", use_container_width=True):
        reset_session_draws()
        st.rerun()

st.write("")

# =========================================================
# 메인 뽑기 화면
# =========================================================
ball_number = st.session_state.display_number
ball_prize = st.session_state.display_prize

display_number = "?" if ball_number is None else str(ball_number)
display_prize = "Ready to draw" if ball_prize == "" else ball_prize

current_ball_color = st.session_state.display_ball_color
rolling_class = "rolling" if st.session_state.rolling else ""
ball_class = "ball-green" if current_ball_color == "green" else "ball-gray"

st.markdown('<div class="main-panel">', unsafe_allow_html=True)

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
    <div class="bottom-card">
        <div class="bottom-label">Prize</div>
        <div class="bottom-value">{display_prize}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 안내 문구
# =========================================================
st.markdown(
    f"""
    <div class="notice-text">
        {NOTICE_TEXT}
    </div>
    """,
    unsafe_allow_html=True,
)

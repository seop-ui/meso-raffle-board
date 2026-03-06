import pandas as pd
import streamlit as st

st.set_page_config(page_title="Raffle Prize Board", layout="wide")

# -----------------------------
# Google Sheets CSV URL
# -----------------------------
sheet_url = "https://docs.google.com/spreadsheets/d/1oYJliCBrYC2qhAKNjGUbaTv4o6fxzpgGb8a-xSt1UOk/export?format=csv"

df = pd.read_csv(sheet_url)

# -----------------------------
# 테스트용 데이터 표 확인
# 나중에 연결 확인 끝나면 지워도 됨
# -----------------------------
st.dataframe(df)

# -----------------------------
# 시트에서 경품 데이터 찾기
# -----------------------------
def get_prize(place, prize):
    row = df[(df["Place"] == place) & (df["Prize"] == prize)]

    if row.empty:
        return {
            "qty": 0,
            "available": 0,
            "odds": "0%"
        }

    return {
        "qty": int(row.iloc[0]["Qty"]),
        "available": int(row.iloc[0]["Available"]),
        "odds": str(row.iloc[0]["Odds"])
    }

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

.main-title {
    text-align: center;
    font-size: 52px;
    font-weight: 800;
    margin-bottom: 40px;
}

.board {
    display: flex;
    gap: 24px;
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
}

.grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
}

.card {
    border: 3px solid #1f3341;
    background: white;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.big-card {
    border: 3px solid #1f3341;
    background: white;
    min-height: 300px;
    width: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.prize {
    font-size: 18px;
    margin-bottom: 10px;
    text-align: center;
    padding: 0 8px;
}

.qty {
    font-size: 40px;
    font-weight: 800;
}

.odds {
    font-size: 26px;
    font-weight: 700;
}

.info-title {
    text-align: center;
    font-size: 30px;
    font-weight: 700;
    margin-top: 40px;
}

.info-box {
    border: 3px solid #1f3341;
    background: white;
    padding: 30px;
    font-size: 22px;
    margin-top: 10px;
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

<div class="big-card">
<div class="prize">Hair Removal Prize</div>
<div class="qty">{hair['available']}/{hair['qty']}</div>
<div>Odds</div>
<div class="odds">{hair['odds']}</div>
</div>

<div class="big-card">
<div class="prize">Facial Prize</div>
<div class="qty">{facial['available']}/{facial['qty']}</div>
<div>Odds</div>
<div class="odds">{facial['odds']}</div>
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

<div class="card">
<div class="prize">BB Laser</div>
<div class="qty">{off_bb['available']}/{off_bb['qty']}</div>
<div>Odds</div>
<div class="odds">{off_bb['odds']}</div>
</div>

<div class="card">
<div class="prize">SylfirmX RF Microneedling</div>
<div class="qty">{off_sylfirm['available']}/{off_sylfirm['qty']}</div>
<div>Odds</div>
<div class="odds">{off_sylfirm['odds']}</div>
</div>

<div class="card">
<div class="prize">Oligio Lifting</div>
<div class="qty">{off_oligio['available']}/{off_oligio['qty']}</div>
<div>Odds</div>
<div class="odds">{off_oligio['odds']}</div>
</div>

<div class="card">
<div class="prize">Ultherapy Prime</div>
<div class="qty">{off_ultherapy['available']}/{off_ultherapy['qty']}</div>
<div>Odds</div>
<div class="odds">{off_ultherapy['odds']}</div>
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

<div class="card">
<div class="prize">BB Laser</div>
<div class="qty">{free_bb['available']}/{free_bb['qty']}</div>
<div>Odds</div>
<div class="odds">{free_bb['odds']}</div>
</div>

<div class="card">
<div class="prize">SylfirmX RF Microneedling</div>
<div class="qty">{free_sylfirm['available']}/{free_sylfirm['qty']}</div>
<div>Odds</div>
<div class="odds">{free_sylfirm['odds']}</div>
</div>

<div class="card">
<div class="prize">Oligio Lifting</div>
<div class="qty">{free_oligio['available']}/{free_oligio['qty']}</div>
<div>Odds</div>
<div class="odds">{free_oligio['odds']}</div>
</div>

<div class="card">
<div class="prize">Ultherapy Prime</div>
<div class="qty">{free_ultherapy['available']}/{free_ultherapy['qty']}</div>
<div>Odds</div>
<div class="odds">{free_ultherapy['odds']}</div>
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

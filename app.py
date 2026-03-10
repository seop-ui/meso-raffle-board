import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
import base64

st.set_page_config(
    page_title="Raffle Event Prize Board",
    layout="wide",
)

# refresh every second
st_autorefresh(interval=1000, key="raffle_refresh")

# ===============================
# 페이지 자동 전환 로직
# ===============================

cycle = 50
t = int(time.time()) % cycle

if t < 30:
    page = "board"
elif t < 40:
    page = "numbers1"
else:
    page = "numbers2"

# ===============================
# 데이터 불러오기
# ===============================

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
except:
    ball_count = 200


# ===============================
# Prize 정보 함수
# ===============================

def get_prize(place, prize):

    row = df[(df["Place"] == place) & (df["Prize"] == prize)]

    if row.empty:
        return {"qty":0,"available":0,"odds":"0%","sold_out":True}

    qty = int(row.iloc[0]["Qty"])
    available = int(row.iloc[0]["Available"])
    odds = str(row.iloc[0]["Odds"])

    return {
        "qty": qty,
        "available": available,
        "odds": odds,
        "sold_out": available <= 0
    }


# ===============================
# 카드 렌더링
# ===============================

def render_card(title,item,large=False):

    if item["sold_out"]:
        value = "SOLD OUT"
        odds = "0%"
    else:
        value = f'{item["available"]}/{item["qty"]}'
        odds = item["odds"]

    size = "feature-card" if large else "prize-card"

    html=f"""
    <div class="{size}">
        <div class="title">{title}</div>
        <div class="value">{value}</div>
        <div class="odds">{odds}</div>
    </div>
    """

    return html


# ===============================
# Prize Number 화면
# ===============================

def render_numbers(start,end):

    number_url="https://docs.google.com/spreadsheets/d/1oYJliCBrYC2qhAKNjGUbaTv4o6fxzpgGb8a-xSt1UOk/export?format=csv&gid=0"

    num_df=pd.read_csv(number_url)

    num_df=num_df.iloc[start-1:end]

    html='<div class="number-grid">'

    for _,row in num_df.iterrows():

        number=row["Number"]
        prize=row["Prize"]
        status=row["Winning Status"]

        if status=="Winner":
            color="#CFE8CF"
        else:
            color="#EFEFEF"

        html+=f"""
        <div class="ball" style="background:{color}">
            <div class="num">{number}</div>
            <div class="prize">{prize}</div>
            <div class="status">{status}</div>
        </div>
        """

    html+='</div>'

    st.markdown(html,unsafe_allow_html=True)


# ===============================
# 통계 계산
# ===============================

detail_df=df[
    df["Prize"].notna() &
    (df["Prize"]!="") &
    (df["Place"]!="합계")
]

total_prizes_left=int(detail_df["Available"].sum())

win_chance=round((total_prizes_left/ball_count)*100,2)
lose_chance=round((1-win_chance/100)*100,2)


# ===============================
# CSS
# ===============================

st.markdown("""
<style>

body{
background:#F7F7F5;
color:#3B4F38;
}

.main-title{
text-align:center;
font-size:60px;
font-weight:900;
margin-bottom:20px;
}

.summary{
display:flex;
justify-content:center;
gap:20px;
margin-bottom:20px;
}

.summary-box{
border:2px solid #3B4F38;
padding:15px 30px;
border-radius:15px;
text-align:center;
}

.feature-card{
height:350px;
border:2px solid #3B4F38;
border-radius:20px;
padding:10px;
text-align:center;
}

.prize-card{
height:150px;
border:2px solid #3B4F38;
border-radius:20px;
padding:10px;
text-align:center;
}

.title{
font-size:18px;
font-weight:700;
}

.value{
font-size:40px;
font-weight:900;
margin-top:20px;
}

.odds{
font-size:20px;
margin-top:10px;
}

.number-grid{
display:grid;
grid-template-columns:repeat(10,1fr);
gap:8px;
padding:20px;
}

.ball{
border:2px solid #3B4F38;
border-radius:10px;
padding:8px;
text-align:center;
height:80px;
}

.num{
font-size:18px;
font-weight:900;
}

.prize{
font-size:11px;
}

.status{
font-size:10px;
}

</style>
""",unsafe_allow_html=True)

# ===============================
# 페이지 렌더링
# ===============================

if page=="board":

    st.markdown('<div class="main-title">Raffle Event Prize Board</div>',unsafe_allow_html=True)

    st.markdown(f"""
    <div class="summary">
        <div class="summary-box">
            <div>Total Prizes Left</div>
            <div style="font-size:40px;font-weight:900;">{total_prizes_left}</div>
        </div>

        <div class="summary-box">
            <div>Win Chance</div>
            <div style="font-size:40px;font-weight:900;">{win_chance:.1f}%</div>
        </div>

        <div class="summary-box">
            <div>Lose Chance</div>
            <div style="font-size:40px;font-weight:900;">{lose_chance:.1f}%</div>
        </div>
    </div>
    """,unsafe_allow_html=True)

    hair=get_prize("Single","Laser Hair Removal (1 Session)")
    facial=get_prize("Single","Custom Korean Facial (1 Session)")

    st.markdown(render_card("Hair Removal",hair,True),unsafe_allow_html=True)
    st.markdown(render_card("Korean Facial",facial,True),unsafe_allow_html=True)

elif page=="numbers1":

    st.markdown('<div class="main-title">Prize Numbers 1 - 100</div>',unsafe_allow_html=True)

    render_numbers(1,100)

elif page=="numbers2":

    st.markdown('<div class="main-title">Prize Numbers 101 - 200</div>',unsafe_allow_html=True)

    render_numbers(101,200)


# ===============================
# 로고
# ===============================

def get_base64_image(path):
    with open(path,"rb") as f:
        return base64.b64encode(f.read()).decode()

logo_base64=get_base64_image("logo_grin_04.png")

st.markdown(f"""
<div style="display:flex;justify-content:center;margin-top:80px;">
<img src="data:image/png;base64,{logo_base64}" width="200">
</div>
""",unsafe_allow_html=True)

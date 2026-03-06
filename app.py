import pandas as pd
import streamlit as st
sheet_url = "https://docs.google.com/spreadsheets/d/1oYJliCBrYC2qhAKNjGUbaTv4o6fxzpgGb8a-xSt1UOk/export?format=csv"

df = pd.read_csv(sheet_url)
st.dataframe(df)



st.set_page_config(page_title="Raffle Prize Board", layout="wide")

st.markdown("""
<style>

html, body, [class*="css"] {
    background-color:#f7f7f5;
}

.main-title{
    text-align:center;
    font-size:52px;
    font-weight:800;
    margin-bottom:40px;
}

.board{
    display:flex;
    gap:24px;
}

.left{
    display:flex;
    gap:20px;
    width:25%;
}

.right{
    display:flex;
    gap:20px;
    width:75%;
}

.group{
    width:50%;
}

.group-title{
    border:3px solid #1f3341;
    text-align:center;
    padding:10px;
    font-size:22px;
    font-weight:700;
    margin-bottom:10px;
    background:white;
}

.grid{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:12px;
}

.card{
    border:3px solid #1f3341;
    background:white;
    min-height:200px;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
}

.big-card{
    border:3px solid #1f3341;
    background:white;
    min-height:300px;
    width:50%;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
}

.prize{
    font-size:18px;
    margin-bottom:10px;
}

.qty{
    font-size:40px;
    font-weight:800;
}

.odds{
    font-size:26px;
    font-weight:700;
}

.info-title{
    text-align:center;
    font-size:30px;
    font-weight:700;
    margin-top:40px;
}

.info-box{
    border:3px solid #1f3341;
    background:white;
    padding:30px;
    font-size:22px;
    margin-top:10px;
}

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">래플 이벤트 경품 현황판</div>', unsafe_allow_html=True)

left = """
<div class="left">

<div class="big-card">
<div class="prize">Hair Removal Prize</div>
<div class="qty">11/20</div>
<div>Odds</div>
<div class="odds">20%</div>
</div>

<div class="big-card">
<div class="prize">Facial Prize</div>
<div class="qty">11/20</div>
<div>Odds</div>
<div class="odds">20%</div>
</div>

</div>
"""

group1 = """
<div class="group">
<div class="group-title">80% Off MeSO Signature Treatment</div>

<div class="grid">

<div class="card">
<div class="prize">BB Laser</div>
<div class="qty">11/20</div>
<div>Odds</div>
<div class="odds">20%</div>
</div>

<div class="card">
<div class="prize">SylfirmX RF Microneedling</div>
<div class="qty">5/5</div>
<div>Odds</div>
<div class="odds">2.5%</div>
</div>

<div class="card">
<div class="prize">Oligio Lifting</div>
<div class="qty">5/5</div>
<div>Odds</div>
<div class="odds">2.5%</div>
</div>

<div class="card">
<div class="prize">Ultherapy Prime</div>
<div class="qty">2/2</div>
<div>Odds</div>
<div class="odds">1%</div>
</div>

</div>
</div>
"""

group2 = """
<div class="group">
<div class="group-title">Free MeSO Signature Treatment</div>

<div class="grid">

<div class="card">
<div class="prize">BB Laser</div>
<div class="qty">4/4</div>
<div>Odds</div>
<div class="odds">2%</div>
</div>

<div class="card">
<div class="prize">SylfirmX RF Microneedling</div>
<div class="qty">2/2</div>
<div>Odds</div>
<div class="odds">1%</div>
</div>

<div class="card">
<div class="prize">Oligio Lifting</div>
<div class="qty">2/2</div>
<div>Odds</div>
<div class="odds">1%</div>
</div>

<div class="card">
<div class="prize">Ultherapy Prime</div>
<div class="qty">1/1</div>
<div>Odds</div>
<div class="odds">0.5%</div>
</div>

</div>
</div>
"""

st.markdown(f"""
<div class="board">
{left}
<div class="right">
{group1}
{group2}
</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="info-title">이벤트 참여방법</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">

1. 이벤트 대상 시술 결제<br>
2. 응모권 수령<br>
3. 추첨기 참여<br>
4. 당첨 시 직원 안내 후 경품 수령

</div>
""", unsafe_allow_html=True)

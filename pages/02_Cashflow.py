import streamlit as st
from utils.financials import build_cashflow

df = build_cashflow(
    120000,
    0.02,
    0.05,
    0.20,
    20
)

st.header("Cash Flow")

st.dataframe(df, use_container_width=True)

st.line_chart(
    df.set_index("Année")[["NOI","AFFO"]]
)

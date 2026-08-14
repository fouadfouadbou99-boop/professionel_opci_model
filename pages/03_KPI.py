import streamlit as st

st.header("Indicateurs KPI")

c1, c2, c3, c4 = st.columns(4)

c1.metric("VAN Projet", "1 035 413")
c2.metric("VAN Equity", "983 642")
c3.metric("MOIC", "5.26x")
c4.metric("LTV", "60%")

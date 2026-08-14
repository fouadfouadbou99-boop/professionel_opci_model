import streamlit as st

st.header("Dashboard Exécutif")

a,b,c,d = st.columns(4)

a.metric("VAN Projet", "1 035 413")
b.metric("VAN Equity", "983 642")
c.metric("MOIC", "5.26x")
d.metric("DSCR", "1.50")

import pandas as pd
import streamlit as st

df = pd.DataFrame({
    "Scénario":[
        "Loyers -10%",
        "Loyers -5%",
        "Base",
        "Loyers +5%",
        "Loyers +10%"
    ],
    "TRI":[9,11,13,15,17]
})

st.header("Analyse de sensibilité")

st.bar_chart(
    df.set_index("Scénario")
)

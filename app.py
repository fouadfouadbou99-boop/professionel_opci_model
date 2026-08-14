import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf

st.set_page_config(
    page_title="Modèle Immobilier OPCI",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Modèle Immobilier OPCI")

st.markdown("""
Simulation simplifiée d'investissement immobilier OPCI.
""")

st.sidebar.header("Hypothèses")

prix_acquisition = st.sidebar.number_input(
    "Prix d'acquisition (MAD)",
    value=10000000.0,
    step=100000.0
)

loyer_annuel = st.sidebar.number_input(
    "Loyer annuel initial (MAD)",
    value=800000.0,
    step=10000.0
)

croissance = st.sidebar.slider(
    "Croissance annuelle des loyers (%)",
    0.0,
    10.0,
    2.0
) / 100

vacance = st.sidebar.slider(
    "Vacance (%)",
    0.0,
    20.0,
    5.0
) / 100

opex = st.sidebar.slider(
    "Charges d'exploitation (%)",
    0.0,
    50.0,
    20.0
) / 100

taux_actualisation = st.sidebar.slider(
    "Taux d'actualisation (%)",
    0.0,
    20.0,
    8.0
) / 100

horizon = st.sidebar.slider(
    "Horizon (années)",
    5,
    30,
    20
)

cashflows = [-prix_acquisition]

data = []

for annee in range(1, horizon + 1):

    revenu_brut = loyer_annuel * ((1 + croissance) ** (annee - 1))
    revenu_net = revenu_brut * (1 - vacance)
    noi = revenu_net * (1 - opex)

    cashflows.append(noi)

    data.append(
        {
            "Année": annee,
            "Revenu Brut": round(revenu_brut, 0),
            "Revenu Net": round(revenu_net, 0),
            "NOI": round(noi, 0)
        }
    )

df = pd.DataFrame(data)

van = npf.npv(taux_actualisation, cashflows)
tri = npf.irr(cashflows)

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "VAN (MAD)",
        f"{van:,.0f}"
    )

with col2:
    st.metric(
        "TRI",
        f"{tri:.2%}"
    )

st.subheader("Cash-Flows")

st.dataframe(
    df,
    use_container_width=True
)

st.subheader("Evolution du NOI")

st.line_chart(
    df.set_index("Année")["NOI"]
)

st.success("Application opérationnelle")

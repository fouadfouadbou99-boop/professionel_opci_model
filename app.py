import streamlit as st
import pandas as pd
import numpy_financial as npf
from io import BytesIO

st.set_page_config(
    page_title="Modèle Immobilier OPCI",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Modèle Immobilier OPCI")

# =========================
# HYPOTHESES
# =========================

st.sidebar.header("Hypothèses")

prix_acquisition = st.sidebar.number_input(
    "Prix Acquisition (MAD)",
    value=10000000.0,
    step=100000.0
)

ltv = st.sidebar.slider(
    "LTV (%)",
    0,
    80,
    60
) / 100

taux_dette = st.sidebar.slider(
    "Taux Dette (%)",
    0.0,
    10.0,
    5.0
) / 100

rendement_initial = st.sidebar.slider(
    "Rendement locatif initial (%)",
    1.0,
    15.0,
    8.0
) / 100

croissance = st.sidebar.slider(
    "Croissance loyers (%)",
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
    "Charges exploitation (%)",
    0.0,
    50.0,
    20.0
) / 100

taux_actualisation = st.sidebar.slider(
    "Taux actualisation (%)",
    1.0,
    20.0,
    8.0
) / 100

exit_yield = st.sidebar.slider(
    "Exit Yield (%)",
    4.0,
    12.0,
    7.0
) / 100

horizon = st.sidebar.slider(
    "Horizon (années)",
    5,
    30,
    20
)

# =========================
# FINANCEMENT
# =========================

montant_dette = prix_acquisition * ltv
fonds_propres = prix_acquisition - montant_dette

# Dette in fine simplifiée

interet_annuel = montant_dette * taux_dette

# =========================
# CASH FLOWS
# =========================

loyer_initial = prix_acquisition * rendement_initial

cashflows_projet = [-prix_acquisition]
cashflows_equity = [-fonds_propres]

data = []

for annee in range(1, horizon + 1):

    loyer_brut = loyer_initial * ((1 + croissance) ** (annee - 1))

    loyer_net = loyer_brut * (1 - vacance)

    noi = loyer_net * (1 - opex)

    cashflow_projet = noi

    cashflow_equity = noi - interet_annuel

    dscr = (
        noi / interet_annuel
        if interet_annuel > 0
        else 0
    )

    cashflows_projet.append(cashflow_projet)

    cashflows_equity.append(cashflow_equity)

    data.append({
        "Année": annee,
        "Loyer Brut": round(loyer_brut, 0),
        "Loyer Net": round(loyer_net, 0),
        "NOI": round(noi, 0),
        "Intérêts": round(interet_annuel, 0),
        "Cash Flow Equity": round(cashflow_equity, 0),
        "DSCR": round(dscr, 2)
    })

# =========================
# VALEUR TERMINALE
# =========================

valeur_terminale = noi / exit_yield

cashflows_projet[-1] += valeur_terminale

cashflows_equity[-1] += (
    valeur_terminale - montant_dette
)

# =========================
# KPI
# =========================

van_projet = npf.npv(
    taux_actualisation,
    cashflows_projet
)

tri_projet = npf.irr(
    cashflows_projet
)

van_equity = npf.npv(
    taux_actualisation,
    cashflows_equity
)

tri_equity = npf.irr(
    cashflows_equity
)

moic_equity = (
    sum(cashflows_equity[1:])
    / fonds_propres
)

debt_yield = (
    (data[0]["NOI"] / montant_dette)
    if montant_dette > 0
    else 0
)

# =========================
# DATAFRAMES
# =========================

df_cashflow = pd.DataFrame(data)

df_kpi = pd.DataFrame({
    "Indicateur": [
        "VAN Projet",
        "TRI Projet",
        "VAN Equity",
        "TRI Equity",
        "MOIC Equity",
        "LTV",
        "Debt Yield"
    ],
    "Valeur": [
        round(van_projet, 0),
        round(tri_projet * 100, 2),
        round(van_equity, 0),
        round(tri_equity * 100, 2),
        round(moic_equity, 2),
        round(ltv * 100, 2),
        round(debt_yield * 100, 2)
    ]
})

# =========================
# DASHBOARD
# =========================

st.subheader("KPI Projet")

c1, c2 = st.columns(2)

c1.metric(
    "VAN Projet",
    f"{van_projet:,.0f} MAD"
)

c2.metric(
    "TRI Projet",
    f"{tri_projet:.2%}"
)

st.subheader("KPI Equity")

c3, c4, c5 = st.columns(3)

c3.metric(
    "VAN Equity",
    f"{van_equity:,.0f} MAD"
)

c4.metric(
    "TRI Equity",
    f"{tri_equity:.2%}"
)

c5.metric(
    "MOIC Equity",
    f"{moic_equity:.2f}x"
)

st.subheader("Financement")

c6, c7, c8 = st.columns(3)

c6.metric(
    "Dette",
    f"{montant_dette:,.0f}"
)

c7.metric(
    "Fonds Propres",
    f"{fonds_propres:,.0f}"
)

c8.metric(
    "Debt Yield",
    f"{debt_yield:.2%}"
)

st.subheader("Cash Flows")

st.dataframe(
    df_cashflow,
    use_container_width=True
)

st.line_chart(
    df_cashflow.set_index("Année")[
        ["NOI", "Cash Flow Equity"]
    ]
)

# =========================
# EXPORT EXCEL
# =========================

buffer = BytesIO()

with pd.ExcelWriter(
    buffer,
    engine="xlsxwriter"
) as writer:

    df_cashflow.to_excel(
        writer,
        sheet_name="Cashflows",
        index=False
    )

    df_kpi.to_excel(
        writer,
        sheet_name="KPI",
        index=False
    )

buffer.seek(0)

st.download_button(
    "📥 Télécharger Excel",
    data=buffer,
    file_name="Modele_OPCI_Dette.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

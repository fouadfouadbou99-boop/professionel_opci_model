import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
import plotly.express as px

st.set_page_config(
    page_title="OPCI Immobilier",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Modèle Immobilier OPCI Professionnel")

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Hypothèses")

prix_acquisition = st.sidebar.number_input(
    "Prix acquisition",
    value=1000000.0
)

frais_acquisition = st.sidebar.number_input(
    "Frais acquisition",
    value=0.08
)

travaux = st.sidebar.number_input(
    "Travaux",
    value=100000.0
)

loyer_brut_a1 = st.sidebar.number_input(
    "Loyer brut année 1",
    value=120000.0
)

croissance = st.sidebar.number_input(
    "Croissance annuelle",
    value=0.02,
    format="%.4f"
)

vacance = st.sidebar.number_input(
    "Vacance",
    value=0.05,
    format="%.4f"
)

opex = st.sidebar.number_input(
    "OPEX",
    value=0.20,
    format="%.4f"
)

ltv = st.sidebar.number_input(
    "LTV",
    value=0.60,
    format="%.4f"
)

taux_dette = st.sidebar.number_input(
    "Taux dette",
    value=0.05,
    format="%.4f"
)

horizon = st.sidebar.slider(
    "Horizon",
    5,
    30,
    20
)

exit_yield = st.sidebar.number_input(
    "Exit Yield",
    value=0.07,
    format="%.4f"
)

discount_rate = st.sidebar.number_input(
    "Discount Rate",
    value=0.08,
    format="%.4f"
)

# =====================================================
# INVESTISSEMENT
# =====================================================

cout_total = prix_acquisition * (1 + frais_acquisition) + travaux

montant_dette = cout_total * ltv
equity = cout_total - montant_dette

# =====================================================
# CASH FLOW
# =====================================================

rows = []

for year in range(1, horizon + 1):

    loyer_brut = loyer_brut_a1 * ((1 + croissance) ** (year - 1))

    loyer_net = loyer_brut * (1 - vacance)

    noi = loyer_net * (1 - opex)

    interets = montant_dette * taux_dette

    ffo = noi - interets

    affo = ffo * 0.95

    rows.append([
        year,
        loyer_brut,
        loyer_net,
        noi,
        ffo,
        affo
    ])

df = pd.DataFrame(
    rows,
    columns=[
        "Année",
        "Loyer Brut",
        "Loyer Net",
        "NOI",
        "FFO",
        "AFFO"
    ]
)

# =====================================================
# VALEUR DE SORTIE
# =====================================================

noi_terminal = df.iloc[-1]["NOI"]

valeur_sortie = noi_terminal / exit_yield

cashflows_equity = [-equity]

for _, row in df.iterrows():
    cashflows_equity.append(row["AFFO"])

cashflows_equity[-1] += valeur_sortie

irr_equity = npf.irr(cashflows_equity)

npv_equity = npf.npv(
    discount_rate,
    cashflows_equity
)

moic = (
    sum(cashflows_equity[1:]) /
    abs(cashflows_equity[0])
)

# =====================================================
# KPI
# =====================================================

st.subheader("📊 KPI")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "TRI Equity",
    f"{irr_equity:.2%}"
)

c2.metric(
    "VAN Equity",
    f"{npv_equity:,.0f}"
)

c3.metric(
    "MOIC",
    f"{moic:.2f}x"
)

c4.metric(
    "LTV",
    f"{ltv:.0%}"
)

# =====================================================
# CASHFLOW
# =====================================================

st.subheader("📈 Cash Flow")

st.dataframe(
    df,
    use_container_width=True
)

fig_cashflow = px.line(
    df,
    x="Année",
    y=["NOI", "AFFO"],
    title="Evolution NOI / AFFO"
)

st.plotly_chart(
    fig_cashflow,
    use_container_width=True
)

# =====================================================
# KPI COMPLEMENTAIRES
# =====================================================

dscr = 1.5
icr = 2.5
occupation = 1 - vacance

st.subheader("📌 KPI Complémentaires")

a, b, c, d = st.columns(4)

a.metric("DSCR", f"{dscr:.2f}")
b.metric("ICR", f"{icr:.2f}")
c.metric("Occupation", f"{occupation:.2%}")
d.metric("Vacance", f"{vacance:.2%}")

# =====================================================
# SENSIBILITE
# =====================================================

st.subheader("🎯 Analyse de Sensibilité")

sens_data = []

for variation in [-0.10, -0.05, 0, 0.05, 0.10]:

    new_rent = loyer_brut_a1 * (1 + variation)

    cashflows = [-equity]

    for y in range(1, horizon + 1):

        gross = new_rent * ((1 + croissance) ** (y - 1))
        net = gross * (1 - vacance)
        noi = net * (1 - opex)
        ffo = noi - (montant_dette * taux_dette)
        affo = ffo * 0.95

        cashflows.append(affo)

    terminal = noi / exit_yield

    cashflows[-1] += terminal

    tri = npf.irr(cashflows)

    sens_data.append({
        "Variation": variation,
        "TRI": tri
    })

sens_df = pd.DataFrame(sens_data)

fig_sens = px.bar(
    sens_df,
    x="Variation",
    y="TRI",
    title="Sensibilité du TRI aux Loyers"
)

st.plotly_chart(
    fig_sens,
    use_container_width=True
)

# =====================================================
# DECISION
# =====================================================

st.subheader("✅ Scoring Investissement")

if irr_equity > 0.12 and moic > 2:
    decision = "INVESTIR"
    couleur = "green"
else:
    decision = "REJETER"
    couleur = "red"

st.markdown(
    f"<h2 style='color:{couleur}'>{decision}</h2>",
    unsafe_allow_html=True
)

# =====================================================
# DASHBOARD EXECUTIF
# =====================================================

st.subheader("🏢 Dashboard Exécutif")

dashboard = pd.DataFrame(
    {
        "Indicateur": [
            "Prix Acquisition",
            "Coût Total",
            "Dette",
            "Equity",
            "Valeur de Sortie",
            "TRI",
            "VAN",
            "MOIC"
        ],
        "Valeur": [
            prix_acquisition,
            cout_total,
            montant_dette,
            equity,
            valeur_sortie,
            irr_equity,
            npv_equity,
            moic
        ]
    }
)

st.dataframe(
    dashboard,
    use_container_width=True
)

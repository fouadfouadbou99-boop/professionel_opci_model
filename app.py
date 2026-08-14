import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
import plotly.express as px

# ==========================================================
# CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Modèle Immobilier OPCI",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Modèle Immobilier OPCI Professionnel")
st.markdown("Simulation financière immobilière OPCI")

# ==========================================================
# SIDEBAR - HYPOTHESES
# ==========================================================

st.sidebar.header("Hypothèses")

prix_acquisition = st.sidebar.number_input(
    "Prix acquisition",
    value=1000000.0,
    step=10000.0
)

frais_acquisition = st.sidebar.number_input(
    "Frais acquisition (%)",
    value=0.08,
    step=0.01
)

travaux = st.sidebar.number_input(
    "Travaux",
    value=100000.0,
    step=10000.0
)

loyer_brut_a1 = st.sidebar.number_input(
    "Loyer Brut année 1",
    value=120000.0,
    step=5000.0
)

croissance = st.sidebar.number_input(
    "Croissance annuelle (%)",
    value=0.02,
    step=0.01
)

vacance = st.sidebar.number_input(
    "Vacance (%)",
    value=0.05,
    step=0.01
)

opex = st.sidebar.number_input(
    "OPEX (%)",
    value=0.20,
    step=0.01
)

ltv = st.sidebar.number_input(
    "LTV (%)",
    value=0.60,
    step=0.05
)

taux_dette = st.sidebar.number_input(
    "Taux dette (%)",
    value=0.05,
    step=0.01
)

horizon = st.sidebar.slider(
    "Horizon (années)",
    min_value=5,
    max_value=30,
    value=20
)

exit_yield = st.sidebar.number_input(
    "Exit Yield (%)",
    value=0.07,
    step=0.005
)

discount_rate = st.sidebar.number_input(
    "Discount Rate (%)",
    value=0.08,
    step=0.01
)

# ==========================================================
# CALCUL INVESTISSEMENT
# ==========================================================

cout_total = prix_acquisition * (1 + frais_acquisition) + travaux

montant_dette = cout_total * ltv

equity = cout_total - montant_dette

# ==========================================================
# GENERATION CASH FLOWS
# ==========================================================

cashflows = []

for annee in range(1, horizon + 1):

    loyer_brut = loyer_brut_a1 * ((1 + croissance) ** (annee - 1))

    loyer_net = loyer_brut * (1 - vacance)

    noi = loyer_net * (1 - opex)

    charge_interet = montant_dette * taux_dette

    ffo = noi - charge_interet

    affo = ffo * 0.95

    cashflows.append([
        annee,
        loyer_brut,
        loyer_net,
        noi,
        ffo,
        affo
    ])

df = pd.DataFrame(
    cashflows,
    columns=[
        "Année",
        "Loyer Brut",
        "Loyer Net",
        "NOI",
        "FFO",
        "AFFO"
    ]
)

# ==========================================================
# VALEUR TERMINALE
# ==========================================================

dernier_noi = df["NOI"].iloc[-1]

valeur_sortie = dernier_noi / exit_yield

# ==========================================================
# CASH FLOWS INVESTISSEUR
# ==========================================================

cashflows_equity = [-equity]

for valeur in df["AFFO"]:
    cashflows_equity.append(valeur)

cashflows_equity[-1] += valeur_sortie

# ==========================================================
# KPI
# ==========================================================

tri_equity = npf.irr(cashflows_equity)

van_equity = npf.npv(
    discount_rate,
    cashflows_equity
)

moic = (
    sum(cashflows_equity[1:]) /
    abs(cashflows_equity[0])
)

occupation = 1 - vacance

dscr = 1.50

icr = 2.50

# ==========================================================
# KPI VISUELS
# ==========================================================

st.subheader("📊 KPI Principaux")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "TRI Equity",
    f"{tri_equity:.2%}"
)

col2.metric(
    "VAN Equity",
    f"{van_equity:,.0f} MAD"
)

col3.metric(
    "MOIC",
    f"{moic:.2f}x"
)

col4.metric(
    "Occupation",
    f"{occupation:.2%}"
)

# ==========================================================
# TABLEAU CASH FLOW
# ==========================================================

st.subheader("📋 Cash Flow")

st.dataframe(
    df.style.format({
        "Loyer Brut": "{:,.0f}",
        "Loyer Net": "{:,.0f}",
        "NOI": "{:,.0f}",
        "FFO": "{:,.0f}",
        "AFFO": "{:,.0f}"
    }),
    use_container_width=True
)

# ==========================================================
# GRAPHIQUE NOI / AFFO
# ==========================================================

st.subheader("📈 Evolution NOI / AFFO")

fig1 = px.line(
    df,
    x="Année",
    y=["NOI", "AFFO"],
    markers=True
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# ==========================================================
# SENSIBILITE TRI
# ==========================================================

st.subheader("🎯 Analyse de Sensibilité")

sensibilite = []

for var in [-0.10, -0.05, 0, 0.05, 0.10]:

    nouveau_loyer = loyer_brut_a1 * (1 + var)

    cfs = [-equity]

    for annee in range(1, horizon + 1):

        gross = nouveau_loyer * ((1 + croissance) ** (annee - 1))

        net = gross * (1 - vacance)

        noi = net * (1 - opex)

        ffo = noi - (montant_dette * taux_dette)

        affo = ffo * 0.95

        cfs.append(affo)

    valeur_terminale = noi / exit_yield

    cfs[-1] += valeur_terminale

    tri = npf.irr(cfs)

    sensibilite.append({
        "Scénario": f"{int(var*100)} %",
        "TRI": tri
    })

sens_df = pd.DataFrame(sensibilite)

fig2 = px.bar(
    sens_df,
    x="Scénario",
    y="TRI",
    text="TRI",
    color="TRI"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# ==========================================================
# SCORING
# ==========================================================

st.subheader("✅ Décision Investissement")

if tri_equity >= 0.12 and moic >= 2:

    st.success("INVESTIR")

else:

    st.error("REJETER")

# ==========================================================
# DASHBOARD EXECUTIF
# ==========================================================

st.subheader("🏢 Dashboard Exécutif")

dashboard = pd.DataFrame({
    "Indicateur": [
        "Prix Acquisition",
        "Coût Total",
        "Dette",
        "Equity",
        "Valeur de Sortie",
        "TRI Equity",
        "VAN Equity",
        "MOIC",
        "DSCR",
        "ICR"
    ],
    "Valeur": [
        prix_acquisition,
        cout_total,
        montant_dette,
        equity,
        valeur_sortie,
        tri_equity,
        van_equity,
        moic,
        dscr,
        icr
    ]
})

st.dataframe(
    dashboard,
    use_container_width=True
)

# ==========================================================
# EXPORT CSV
# ==========================================================

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Télécharger Cash Flow CSV",
    data=csv,
    file_name="cashflow_opci.csv",
    mime="text/csv"
)

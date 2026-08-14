import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
import plotly.express as px
from io import BytesIO

# ==========================================================
# CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Modèle Immobilier OPCI",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Modèle Immobilier OPCI Professionnel")
st.markdown("Analyse financière immobilière OPCI")

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.header("Hypothèses")

prix_acquisition = st.sidebar.number_input(
    "Prix acquisition (MAD)",
    value=1000000.0,
    step=50000.0
)

frais_acquisition = st.sidebar.number_input(
    "Frais acquisition (%)",
    value=0.08,
    step=0.01,
    format="%.2f"
)

travaux = st.sidebar.number_input(
    "Travaux (MAD)",
    value=100000.0,
    step=10000.0
)

loyer_brut_a1 = st.sidebar.number_input(
    "Loyer brut année 1",
    value=120000.0,
    step=5000.0
)

croissance = st.sidebar.number_input(
    "Croissance annuelle (%)",
    value=0.02,
    step=0.01,
    format="%.2f"
)

vacance = st.sidebar.number_input(
    "Vacance (%)",
    value=0.05,
    step=0.01,
    format="%.2f"
)

opex = st.sidebar.number_input(
    "OPEX (%)",
    value=0.20,
    step=0.01,
    format="%.2f"
)

ltv = st.sidebar.number_input(
    "LTV (%)",
    value=0.60,
    step=0.05,
    format="%.2f"
)

taux_dette = st.sidebar.number_input(
    "Taux dette (%)",
    value=0.05,
    step=0.01,
    format="%.2f"
)

horizon = st.sidebar.slider(
    "Horizon (années)",
    5,
    40,
    20
)

exit_yield = st.sidebar.number_input(
    "Exit Yield (%)",
    value=0.07,
    step=0.005,
    format="%.3f"
)

discount_rate = st.sidebar.number_input(
    "Discount Rate (%)",
    value=0.08,
    step=0.01,
    format="%.2f"
)

# ==========================================================
# INVESTISSEMENT
# ==========================================================

cout_total = prix_acquisition * (1 + frais_acquisition) + travaux

montant_dette = cout_total * ltv

equity = cout_total - montant_dette

# ==========================================================
# CASH FLOW
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
# SORTIE
# ==========================================================

dernier_noi = df["NOI"].iloc[-1]

if exit_yield > 0:
    valeur_sortie = dernier_noi / exit_yield
else:
    valeur_sortie = 0

# ==========================================================
# FLUX EQUITY
# ==========================================================

cashflows_equity = [-equity]

for valeur in df["AFFO"]:
    cashflows_equity.append(valeur)

cashflows_equity[-1] += valeur_sortie

# ==========================================================
# KPI
# ==========================================================

try:
    tri_equity = npf.irr(cashflows_equity)
except:
    tri_equity = np.nan

van_equity = (
    -equity +
    npf.npv(
        discount_rate,
        cashflows_equity[1:]
    )
)

moic = (
    sum(cashflows_equity[1:]) /
    abs(cashflows_equity[0])
)

occupation = 1 - vacance

service_dette = montant_dette * taux_dette

if service_dette > 0:
    dscr = df["NOI"].mean() / service_dette
else:
    dscr = np.nan

if service_dette > 0:
    icr = df["FFO"].mean() / service_dette
else:
    icr = np.nan

cap_rate = df["NOI"].iloc[0] / prix_acquisition

# ==========================================================
# KPI VISUELS
# ==========================================================

st.subheader("📊 KPI Principaux")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("TRI Equity", f"{tri_equity:.2%}")
c2.metric("VAN Equity", f"{van_equity:,.0f} MAD")
c3.metric("MOIC", f"{moic:.2f} x")
c4.metric("DSCR", f"{dscr:.2f}")
c5.metric("Cap Rate", f"{cap_rate:.2%}")

# ==========================================================
# CASH FLOW
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
# EVOLUTION NOI / AFFO
# ==========================================================

st.subheader("📈 Evolution NOI / AFFO")

fig1 = px.line(
    df,
    x="Année",
    y=["NOI", "AFFO"],
    markers=True
)

fig1.update_layout(
    yaxis_title="MAD",
    legend_title=""
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# ==========================================================
# SENSIBILITE
# ==========================================================

st.subheader("🎯 Analyse de sensibilité")

sensibilite = []

scenarios = [
    (-0.10, "Loyers -10%"),
    (-0.05, "Loyers -5%"),
    (0.00, "Base"),
    (0.05, "Loyers +5%"),
    (0.10, "Loyers +10%")
]

for var, nom in scenarios:

    nouveau_loyer = loyer_brut_a1 * (1 + var)

    cfs = [-equity]

    for annee in range(1, horizon + 1):

        gross = nouveau_loyer * ((1 + croissance) ** (annee - 1))

        net = gross * (1 - vacance)

        noi = net * (1 - opex)

        ffo = noi - service_dette

        affo = ffo * 0.95

        cfs.append(affo)

    valeur_terminale = noi / exit_yield

    cfs[-1] += valeur_terminale

    try:
        tri = npf.irr(cfs) * 100
    except:
        tri = np.nan

    sensibilite.append({
        "Scénario": nom,
        "TRI": tri
    })

sens_df = pd.DataFrame(sensibilite)

fig2 = px.bar(
    sens_df,
    x="Scénario",
    y="TRI",
    text="TRI",
    color="TRI",
    color_continuous_scale=[
        "#d73027",
        "#fc8d59",
        "#fee090",
        "#91bfdb",
        "#4575b4"
    ]
)

fig2.update_traces(
    texttemplate="%{y:.1f}%",
    textposition="outside"
)

fig2.update_layout(
    showlegend=False,
    yaxis_title="TRI (%)",
    xaxis_title=""
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# ==========================================================
# DECISION
# ==========================================================

st.subheader("✅ Décision d'investissement")

if (
    tri_equity >= 0.12
    and moic >= 2
    and dscr >= 1.20
):
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
        "Cap Rate",
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
        cap_rate,
        dscr,
        icr
    ]
})

st.dataframe(
    dashboard.style.format({
        "Valeur": "{:,.2f}"
    }),
    use_container_width=True
)

# ==========================================================
# EXPORT CSV
# ==========================================================

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Télécharger CSV",
    data=csv,
    file_name="cashflow_opci.csv",
    mime="text/csv"
)

# ==========================================================
# EXPORT EXCEL
# ==========================================================

buffer = BytesIO()

with pd.ExcelWriter(
    buffer,
    engine="openpyxl"
) as writer:

    df.to_excel(
        writer,
        index=False,
        sheet_name="CashFlow"
    )

st.download_button(
    label="📊 Télécharger Excel",
    data=buffer.getvalue(),
    file_name="modele_opci.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

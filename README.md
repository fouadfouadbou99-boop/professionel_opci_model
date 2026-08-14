# 🏢 OPCI Real Estate Financial Model

Application Streamlit de modélisation financière immobilière destinée aux OPCI, foncières, investisseurs institutionnels et caisses de retraite.

L'application permet :

- Simulation des cash-flows immobiliers
- Calcul automatique des KPI financiers
- Analyse de rentabilité
- Analyse de sensibilité
- Tableau de bord décisionnel
- Génération des indicateurs d'investissement

---

# Fonctionnalités

## 1. Paramétrage des hypothèses

L'utilisateur peut définir :

- Prix d'acquisition
- Frais d'acquisition
- Budget CAPEX
- Loyer annuel initial
- Taux de croissance des loyers
- Taux de vacance
- Charges d'exploitation
- Horizon d'investissement
- Taux de financement
- LTV
- Exit Yield
- Inflation

---

## 2. Modélisation des Cash-Flows

Calcul annuel de :

- Revenus locatifs bruts
- Revenus locatifs nets
- NOI (Net Operating Income)
- Dette
- Service de la dette
- Free Cash Flow
- AFFO
- Distribution aux investisseurs

---

## 3. Calcul des KPI

### Rentabilité

- TRI Projet
- TRI Equity
- VAN Projet
- VAN Equity
- MOIC

### Dette

- DSCR
- ICR
- Debt Yield
- LTV

### Valorisation

- Valeur terminale
- Exit Value
- Multiple de sortie

---

## 4. Analyse de sensibilité

Simulation automatique sur :

- Loyers
- Taux de vacance
- Exit Yield
- Taux d'actualisation

Affichage sous forme de :

- Heatmap
- Graphiques
- Tableau dynamique

---

## 5. Dashboard Exécutif

Vue synthétique destinée aux :

- Comité d'investissement
- Direction financière
- Direction générale
- Conseil d'administration

---

# Structure du projet

```text
opci-streamlit/
│
├── app.py
├── requirements.txt
├── README.md
│
├── pages/
│   ├── 01_Hypotheses.py
│   ├── 02_Cashflow.py
│   ├── 03_KPI.py
│   ├── 04_Sensibilite.py
│   └── 05_Dashboard.py
│
├── utils/
│   ├── financials.py
│   ├── debt.py
│   ├── valuation.py
│   └── metrics.py
│
├── data/
│   └── model.xlsx
│
└── assets/
    └── logo.png

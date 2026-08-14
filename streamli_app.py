import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import numpy_financial as npf

# Titre de l'application Streamlit
st.set_page_config(layout="wide")
st.title("Modèle Financier Immobilier")
st.write("Visualisation des projections financières annuelles et calculs de rentabilité")

# --- 1. Charger les données et les Hypothèses ---
excel_file_path = '/content/Real_estate_app_project.xlsx'

try:
    excel_file = pd.ExcelFile(excel_file_path)
    hypotheses_df = pd.read_excel(excel_file, sheet_name='Hypothèses')
    # Clean up the hypotheses_df
    hypotheses_df.columns = ['Parameter', 'Value']
    hypotheses_df = hypotheses_df.drop(0).set_index('Parameter')
    st.success(f"Fichier '{excel_file_path}' chargé avec succès!")
except FileNotFoundError:
    st.error(f"Erreur: Le fichier '{excel_file_path}' n'a pas été trouvé. Assurez-vous qu'il existe.")
    st.stop()

# Function to get value safely from hypotheses
def get_hypothesis(param_name):
    # Ensure the value is numeric, handling potential string formats if any
    value = hypotheses_df.loc[param_name, 'Value']
    return pd.to_numeric(value, errors='coerce')

# --- 2. Récupérer les paramètres et effectuer les calculs ---

# Acquisition
prix_acquisition = get_hypothesis('Prix acquisition')
frais_acquisition_percent = get_hypothesis('Frais acquisition %')
travaux = get_hypothesis('Travaux')
budget_acquisition = prix_acquisition * (1 + frais_acquisition_percent) + travaux

# Financement
dette_percent = get_hypothesis('Dette %')
montant_dette = budget_acquisition * dette_percent
montant_equity = budget_acquisition - montant_dette

# Dette (Amortization Schedule)
interest_rate_annual = get_hypothesis('Taux dette %')
loan_duration_years = int(get_hypothesis('Duree dette'))

interest_rate_monthly = interest_rate_annual / 12
num_payments_months = loan_duration_years * 12

monthly_payment = 0
if interest_rate_monthly > 0:
    # Using numpy_financial.pmt for more robust monthly payment calculation
    monthly_payment = npf.pmt(interest_rate_monthly, num_payments_months, -montant_dette)
else:
    monthly_payment = montant_dette / num_payments_months # Simple division if interest rate is 0

amortization_schedule_data = []
remaining_balance = montant_dette

for year in range(1, loan_duration_years + 1):
    annual_interest_payment = 0
    annual_principal_payment = 0
    start_balance_year = remaining_balance # Store starting balance for the year

    # Calculate annual payments using numpy_financial
    # Total interest for the year
    # npf.ipmt calculates the interest payment for a given period
    # npf.ppmt calculates the principal payment for a given period
    for month in range(1, 13):
        if remaining_balance <= 0: # Stop if loan is fully paid off mid-year
            break

        period = (year - 1) * 12 + month
        if period <= num_payments_months:
            interest_this_month = npf.ipmt(interest_rate_monthly, period, num_payments_months, -montant_dette)
            principal_this_month = npf.ppmt(interest_rate_monthly, period, num_payments_months, -montant_dette)
        else:
            interest_this_month = 0
            principal_this_month = 0

        annual_interest_payment += interest_this_month
        annual_principal_payment += principal_this_month
        # Update remaining balance for accurate monthly calculations within the year
        # This is more accurate than simple sum for remaining balance. Recalculate using npf.fv or track manually.
        # For annual schedule, npf functions are better used to get aggregate sums for the year

    # Recalculate remaining balance at year end
    # Use a loop to update remaining_balance for next year's start_balance
    current_year_start_balance = montant_dette
    if year > 1:
        current_year_start_balance = amortization_schedule_data[year - 2][5]

    temp_balance = current_year_start_balance
    total_interest_year = 0
    total_principal_year = 0
    for _ in range(12):
        if temp_balance <= 0:
            break
        interest_pmt = temp_balance * interest_rate_monthly
        principal_pmt = monthly_payment - interest_pmt
        if principal_pmt > temp_balance:
            principal_pmt = temp_balance
            interest_pmt = monthly_payment - principal_pmt

        total_interest_year += interest_pmt
        total_principal_year += principal_pmt
        temp_balance -= principal_pmt
        if abs(temp_balance) < 0.01: # handle floating point inaccuracies
            temp_balance = 0

    remaining_balance_eoy = temp_balance

    amortization_schedule_data.append([
        year,
        current_year_start_balance,
        total_interest_year,
        total_principal_year,
        total_interest_year + total_principal_year, # Annual Annuity
        remaining_balance_eoy
    ])
amortization_schedule_df = pd.DataFrame(amortization_schedule_data, columns=[
    'Année', 'Solde début période', 'Intérêts annuels', 'Amortissement annuel', 'Annuité annuelle', 'Solde fin période'
])


# Projection Annuelle
loyer_brut_an1 = get_hypothesis('Loyer brut An1')
croissance_loyers_percent = get_hypothesis('Croissance loyers %')
vacance_percent = get_hypothesis('Vacance %')
charges_percent = get_hypothesis('Charges %')
horizon_years = int(get_hypothesis('Horizon'))

projection_data = []
current_gross_rent = loyer_brut_an1

for year in range(1, horizon_years + 1):
    revenus_bruts = current_gross_rent
    vacance = revenus_bruts * vacance_percent
    revenus_nets = revenus_bruts - vacance
    charges_exploitation = revenus_nets * charges_percent
    noi = revenus_nets - charges_exploitation

    interets_dette = 0
    amortissement_capital = 0
    if year <= loan_duration_years:
        # Ensure 'Année' in amortization_schedule_df is treated as numeric for lookup
        amort_year_data = amortization_schedule_df[amortization_schedule_df['Année'] == year]
        if not amort_year_data.empty:
            interets_dette = amort_year_data['Intérêts annuels'].iloc[0]
            amortissement_capital = amort_year_data['Amortissement annuel'].iloc[0]

    projection_data.append([
        year, revenus_bruts, vacance, revenus_nets, charges_exploitation, noi, interets_dette, amortissement_capital
    ])
projection_numeric_df = pd.DataFrame(projection_data, columns=[
    'Année', 'Revenus Bruts', 'Vacance', 'Revenus Nets', 'Charges d\'exploitation', 'NOI', 'Intérêts de la dette', 'Amortissement du capital'
])

# Cash Flows
projection_numeric_df['Cash-flow avant dette'] = projection_numeric_df['NOI']
projection_numeric_df['Cash-flow après dette'] = projection_numeric_df['NOI'] - \
                                               projection_numeric_df['Intérêts de la dette'] - \
                                               projection_numeric_df['Amortissement du capital']

# Valeur Terminale et Produit Net de Cession
noi_last_year = projection_numeric_df.loc[projection_numeric_df['Année'] == horizon_years, 'NOI'].iloc[0]
exit_cap_rate = get_hypothesis('Exit Cap Rate %')
frais_cession_percent = get_hypothesis('Frais cession %')

valeur_terminale = noi_last_year / exit_cap_rate if exit_cap_rate > 0 else 0
produit_net_cession = valeur_terminale * (1 - frais_cession_percent)

# KPIs
project_cash_flows = [-budget_acquisition] + projection_numeric_df['NOI'].tolist()
if horizon_years < len(project_cash_flows): # Ensure index exists
    project_cash_flows[horizon_years] += produit_net_cession # Add terminal value to last year NOI

equity_cash_flows = [-montant_equity] + projection_numeric_df['Cash-flow après dette'].tolist()
if horizon_years < len(equity_cash_flows): # Ensure index exists
    equity_cash_flows[horizon_years] += produit_net_cession # Add terminal value to last year Equity CF

tri_projet = npf.irr(project_cash_flows) if project_cash_flows else 0 # Handle empty list
tri_equity = npf.irr(equity_cash_flows) if equity_cash_flows else 0

taux_actualisation = get_hypothesis('Taux actualisation %')
van = npf.npv(taux_actualisation, project_cash_flows[1:]) + project_cash_flows[0] # NPV function usually expects future CFs, so we add initial CF separately

moic_equity_multiple = sum(cf for cf in equity_cash_flows if cf > 0) / abs(equity_cash_flows[0]) if abs(equity_cash_flows[0]) > 0 else np.inf


# Ratios Financiers Annuels (DSCR et LTV)
projection_numeric_df['Debt Service'] = projection_numeric_df['Intérêts de la dette'] + \
                                       projection_numeric_df['Amortissement du capital']
projection_numeric_df['DSCR'] = projection_numeric_df.apply(
    lambda row: row['NOI'] / row['Debt Service'] if row['Debt Service'] != 0 else np.inf, axis=1)

if exit_cap_rate == 0:
    projection_numeric_df['Asset Value'] = np.inf
else:
    projection_numeric_df['Asset Value'] = projection_numeric_df['NOI'] / exit_cap_rate

# Map remaining loan balance for LTV calculation
# Ensure 'Année' column in both DFs are comparable for mapping
projection_numeric_df['Solde fin période'] = projection_numeric_df['Année'].map(
    amortization_schedule_df.set_index('Année')['Solde fin période'])
projection_numeric_df['Solde fin période'] = projection_numeric_df['Solde fin période'].fillna(0)

projection_numeric_df['LTV'] = projection_numeric_df.apply(
    lambda row: (row['Solde fin période'] / row['Asset Value']) if row['Asset Value'] != 0 and not pd.isna(row['Asset Value']) else np.nan, axis=1)

# Prepare DataFrame for display (formatting)
projection_df_display = projection_numeric_df.copy()
for col in ['Revenus Bruts', 'Vacance', 'Revenus Nets', 'Charges d\'exploitation', 'NOI',
            'Intérêts de la dette', 'Amortissement du capital', 'Cash-flow avant dette',
            'Cash-flow après dette', 'Debt Service', 'Asset Value', 'Solde fin période']:
    projection_df_display[col] = projection_df_display[col].apply(lambda x: f'{x:,.2f}' if pd.notna(x) and np.isfinite(x) else 'N/A')

projection_df_display['DSCR'] = projection_df_display['DSCR'].apply(lambda x: f'{x:,.2f}' if pd.notna(x) and np.isfinite(x) else 'N/A')
projection_df_display['LTV'] = projection_df_display['LTV'].apply(lambda x: f'{x:,.2%}' if pd.notna(x) and np.isfinite(x) else 'N/A')

# --- 3. Affichage Streamlit ---

st.header("Paramètres d'entrée")
st.dataframe(hypotheses_df.astype(str))

st.header("Indicateurs Clés de Performance (KPIs)")
col1, col2, col3, col4 = st.columns(4)
col1.metric("TRI Projet", f"{tri_projet:.2%}")
col2.metric("TRI Equity", f"{tri_equity:.2%}")
col3.metric("VAN", f"{van:,.2f} €")
col4.metric("MOIC / Equity Multiple", f"{moic_equity_multiple:.2f}x")

st.header("Tableau de Projection Annuel")
st.dataframe(projection_df_display)

st.header("Visualisation des Flux de Trésorerie")
fig_cashflows = px.line(
    projection_numeric_df,
    x='Année',
    y=['NOI', 'Cash-flow avant dette', 'Cash-flow après dette'],
    title='NOI et Flux de Trésorerie Annuels',
    labels={'value': 'Montant (€)', 'Année': 'Année'},
    hover_name='Année',
    height=500
)
fig_cashflows.update_layout(hovermode="x unified")
st.plotly_chart(fig_cashflows, use_container_width=True)

st.header("Visualisation des Ratios DSCR et LTV")
fig_ratios = px.line(
    projection_numeric_df,
    x='Année',
    y=['DSCR', 'LTV'],
    title='Ratios DSCR et LTV Annuels',
    labels={'value': 'Ratio', 'Année': 'Année'},
    hover_name='Année',
    height=500
)
fig_ratios.update_layout(hovermode="x unified")
st.plotly_chart(fig_ratios, use_container_width=True)

# Export to Excel
output_excel_path = '/content/annual_projection_with_ratios.xlsx'
projection_df_display.to_excel(output_excel_path, index=False)
st.success(f"Le tableau de projection complet a été exporté vers '{output_excel_path}'")

st.markdown("--- ")
st.markdown("Ce modèle a été généré pour automatiser les calculs financiers et visualiser les projections immobilières.")

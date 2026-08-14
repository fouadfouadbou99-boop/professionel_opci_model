# 🏢 Modèle Immobilier OPCI

Application Streamlit de modélisation financière immobilière destinée aux OPCI, investisseurs institutionnels, caisses de retraite et sociétés de gestion.

## Fonctionnalités

- Simulation de cash-flows immobiliers
- Calcul de la VAN (Valeur Actuelle Nette)
- Calcul du TRI (Taux de Rendement Interne)
- Analyse des revenus locatifs
- Tableau de bord exécutif
- Visualisation graphique des performances

## Structure du projet

```text
professionelopcimodel/
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

Cloner le dépôt :

```bash
git clone https://github.com/votre_compte/professionelopcimodel.git
cd professionelopcimodel
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

## Exécution locale

Lancer l'application :

```bash
streamlit run app.py
```

L'application sera accessible à l'adresse :

```text
http://localhost:8501
```

## Déploiement Streamlit Cloud

Paramètres de déploiement :

```text
Repository : professionelopcimodel
Branch : main
Main file path : app.py
```

## Dépendances

```text
streamlit
pandas
numpy
numpy-financial
```

## KPI suivis

- VAN Projet
- VAN Equity
- TRI
- MOIC
- DSCR
- Cash-Flows
- Revenus locatifs

## Auteur

Fouad Boukhnif

Chef de Division

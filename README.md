# Modèle Financier Immobilier avec Streamlit

Ce projet fournit un modèle financier interactif pour l'évaluation de projets immobiliers, implémenté en Python et visualisé via une application Streamlit. Il permet de simuler des projections financières annuelles, de calculer des indicateurs clés de performance (KPIs) et de visualiser les flux de trésorerie ainsi que les ratios financiers.

## Fonctionnalités

*   **Chargement des Hypothèses :** Lit les paramètres d'entrée (prix d'acquisition, frais, loyers, taux d'intérêt, etc.) à partir d'un fichier Excel (`Real_estate_app_project.xlsx`).
*   **Calcul de Financement :** Détermine le budget d'acquisition, le montant de la dette et l'apport en fonds propres (equity).
*   **Tableau d'Amortissement :** Génère un tableau d'amortissement annuel pour le prêt immobilier.
*   **Projection Annuelle :** Calcule les revenus bruts, la vacance, les charges d'exploitation, le NOI (Net Operating Income) et les flux de trésorerie avant et après dette sur un horizon défini.
*   **Valeur Terminale et Produit Net de Cession :** Estime la valeur de revente de l'actif à la fin de l'horizon de projection.
*   **Calcul des KPIs :** Calcule le TRI (Taux de Rentabilité Interne) projet, le TRI equity, la VAN (Valeur Actuelle Nette) et le MOIC (Multiple on Invested Capital).
*   **Ratios Financiers :** Calcule annuellement le DSCR (Debt Service Coverage Ratio) et le LTV (Loan-to-Value).
*   **Visualisations Interactives :** Utilise Plotly pour des graphiques dynamiques des flux de trésorerie et des ratios financiers.
*   **Exportation :** Exporte le tableau de projection complet (incluant les ratios) dans un fichier Excel.

## Fichiers

*   `streamlit_app.py` : Le script principal de l'application Streamlit contenant toute la logique de calcul et l'interface utilisateur.
*   `Real_estate_app_project.xlsx` : Le fichier Excel contenant les hypothèses d'entrée pour le modèle financier. Il doit inclure une feuille nommée `Hypothèses` avec les paramètres requis.
*   `annual_projection_with_ratios.xlsx` : Le fichier Excel de sortie généré par l'application, contenant le tableau de projection annuel détaillé avec les KPIs et les ratios.

## Installation et Utilisation

1.  **Cloner le dépôt GitHub :**
    ```bash
    git clone <URL_DU_DEPOT>
    cd <NOM_DU_DEPOT>
    ```

2.  **Installer les dépendances :**
    Assurez-vous d'avoir Python 3.7+ installé. Créez un environnement virtuel (recommandé) :
    ```bash
    python -m venv venv
    source venv/bin/activate  # Sur Windows: .\venv\Scripts\activate
    pip install -r requirements.txt
    ```
    (Le fichier `requirements.txt` devrait contenir `streamlit`, `pandas`, `plotly`, `numpy`, `numpy_financial`)

3.  **Préparer le fichier d'hypothèses :**
    Placez votre fichier `Real_estate_app_project.xlsx` dans le même répertoire que `streamlit_app.py`. Ce fichier doit contenir la feuille `Hypothèses` avec les données d'entrée structurées comme suit (colonne A pour le paramètre, colonne B pour la valeur) :

    | Parameter            | Value      |
    | :------------------- | :--------- |
    | Prix acquisition     | 1000000.00 |
    | Frais acquisition %  | 0.08       |
    | Travaux              | 100000.00  |
    | Loyer brut An1       | 120000.00  |
    | ...                  | ...        |

4.  **Lancer l'application Streamlit :**
    ```bash
    streamlit run streamlit_app.py
    ```

    L'application s'ouvrira automatiquement dans votre navigateur web.

## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à soumettre des issues ou des pull requests pour améliorer le modèle ou l'application.

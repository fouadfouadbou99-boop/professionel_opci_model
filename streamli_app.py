# --------------------------------------------------
# AMORTISSEMENT DETTE
# --------------------------------------------------

monthly_rate = taux_dette / 12
nper = duree_dette * 12

if monthly_rate > 0:

    mensualite = npf.pmt(
        monthly_rate,
        nper,
        -montant_dette
    )

else:

    mensualite = montant_dette / nper

solde = montant_dette

schedule = []

for annee in range(1, duree_dette + 1):

    debut = solde

    interets_annuels = 0
    principal_annuel = 0

    for mois in range(12):

        if solde <= 0:
            break

        interet = solde * monthly_rate

        principal = mensualite - interet

        principal = min(principal, solde)

        # Correction de l'erreur
        solde -= principal

        interets_annuels += interet
        principal_annuel += principal

    service_dette = (
        interets_annuels +
        principal_annuel
    )

    schedule.append(
        {
            "Année": annee,
            "Dette début": debut,
            "Intérêts": interets_annuels,
            "Principal": principal_annuel,
            "Service dette": service_dette,
            "Dette fin": solde
        }
    )

debt_df = pd.DataFrame(schedule)


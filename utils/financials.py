import pandas as pd
import numpy as np

def build_cashflow(
    rent_a1,
    growth,
    vacancy,
    opex,
    horizon
):

    rows = []

    for year in range(1, horizon + 1):

        gross_rent = rent_a1 * ((1 + growth) ** (year - 1))

        net_rent = gross_rent * (1 - vacancy)

        noi = net_rent * (1 - opex)

        ffo = noi

        affo = ffo * 0.95

        rows.append([
            year,
            gross_rent,
            net_rent,
            noi,
            ffo,
            affo
        ])

    return pd.DataFrame(
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

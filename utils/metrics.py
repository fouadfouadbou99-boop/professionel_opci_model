import numpy as np
import numpy_financial as npf

def calc_npv(rate, cashflows):
    return npf.npv(rate, cashflows)

def calc_irr(cashflows):
    return npf.irr(cashflows)

def calc_moic(total_distributions, equity):
    return total_distributions / equity

import math


def valor_futuro_continuo(tasa_continua,
                          dias_anio,
                          dias_inversion,
                          valor_presente):
    factor_incremento = math.exp(tasa_continua*dias_inversion/dias_anio)
    return valor_presente*factor_incremento
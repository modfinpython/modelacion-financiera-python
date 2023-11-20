import math


def valor_presente_continuo(tasa_continua,
                            dias_anio,
                            dias_inversion,
                            valor_futuro):
    factor_decremento_continuo = math.exp(-tasa_continua * dias_inversion/dias_anio)
    return valor_futuro*factor_decremento_continuo
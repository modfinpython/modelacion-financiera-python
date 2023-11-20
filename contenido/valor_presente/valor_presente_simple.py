def valor_presente(tasa_interes, dias_anio, dias_flujo, valor_futuro):
    factor_descuento = 1/(1 + tasa_interes * dias_flujo / dias_anio)
    return valor_futuro*factor_descuento

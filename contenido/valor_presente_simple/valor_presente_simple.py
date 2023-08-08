def valor_presente(tasa_interes, dias_anio, dias_flujo, flujo_futuro):
    factor_descuento = 1/(1 + tasa_interes * dias_flujo / dias_anio) ** (dias_flujo / dias_anio)
    valor_presente = flujo_futuro * factor_descuento
    return valor_presente

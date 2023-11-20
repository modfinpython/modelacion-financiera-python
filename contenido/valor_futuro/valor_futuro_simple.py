def obtener_valor_futuro_simple(tasa_interes,
                                dias_flujo,
                                dias_anio,
                                valor_presente):
    factor_incremento = (1+tasa_interes*dias_flujo/dias_anio)
    return valor_presente*factor_incremento

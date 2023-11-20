def valor_futuro_compuesto(tasa_interes,
                           dias_anio,
                           dias_inversion,
                           dias_capitalizacion,
                           valor_presente):
    factor_interes_compuesto = (1 + tasa_interes * (dias_capitalizacion / dias_anio)) ** (dias_inversion / dias_capitalizacion)
    return valor_presente * factor_interes_compuesto

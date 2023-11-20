def valor_futuro_anualidad_ordinaria(pago, 
                                     frecuencia,
                                     tasa_nominal,
                                     anios_inversion):
    tasa_ajustada = tasa_nominal/frecuencia
    periodos = anios_inversion*frecuencia
    valor_futuro = pago*((1+tasa_ajustada)**(periodos)-1)/tasa_ajustada
    return valor_futuro

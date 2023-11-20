def valor_presente_anualidad_ordinaria(pago,
                                       frecuencia,
                                       tasa_nominal,
                                       anios_inversion):
    tasa_ajustada = tasa_nominal / frecuencia
    periodos = anios_inversion * frecuencia
    valor_presente = pago * ((1 - (1 + tasa_ajustada) ** (-periodos)) / tasa_ajustada)
    return valor_presente
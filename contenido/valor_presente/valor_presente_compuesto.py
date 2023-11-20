def valor_presente_compuesto(tasa_interes,
                             dias_anio,
                             dias_inversion,
                             dias_capitalizacion,
                             valor_futuro):
    factor_decremento_compuesto = 1/((1+tasa_interes*dias_capitalizacion/dias_anio)**(dias_inversion/dias_capitalizacion))
    return valor_futuro*factor_decremento_compuesto

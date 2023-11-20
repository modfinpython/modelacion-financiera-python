import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def calendario_pagos(pago, frecuencia, tasa_interes, anios):
    tasa_ajust = tasa_interes/frecuencia
    periodos_indice = anios*frecuencia+1
    anualidad = np.zeros(periodos_indice)
    capital_inicial = np.zeros(periodos_indice)
    interes = np.zeros(periodos_indice)
    capital_final = np.zeros(periodos_indice)
    periodos = np.arange(periodos_indice)

    for i in range(periodos_indice):
        if i == 0:
            anualidad[i] = 0
            capital_inicial[i] = 0
            capital_final[i] = 0
        else:
            anualidad[i] = pago
            capital_inicial[i] = capital_final[i-1]
            interes[i] = capital_inicial[i]*tasa_ajust
            capital_final[i] = capital_inicial[i]+interes[i]+anualidad[i]

    df = {'Periodo': periodos,
          'Pago': anualidad,
          'Capital Inicial': capital_inicial,
          'Interes': interes,
          'Capital Final': capital_final}
    calendario_pagos = pd.DataFrame(df)

    return calendario_pagos


def plot_calendario_pagos(tabla: pd.DataFrame):
    periodos = tabla['Periodo']
    ancho_barras = 0.5
    indices = np.arange(len(periodos))

    fig, ax = plt.subplots()

    ax.bar(indices, tabla['Pago'], width=ancho_barras, label='Pago')
    ax.bar(indices, tabla['Interes'], width=ancho_barras, bottom=tabla['Pago'], label='Interés')
    ax.bar(indices, tabla['Capital Inicial'], width=ancho_barras, bottom=tabla['Pago'] + tabla['Interes'], label='Capital Inicial')

    ax.bar(indices, tabla['Capital Final'], width=ancho_barras, bottom=tabla['Pago'] + tabla['Capital Inicial'] + tabla['Interes'] , label='Capital Final')

    ax.set_xlabel('Periodo')
    ax.set_ylabel('Valor')
    ax.set_xticks(indices)
    ax.set_xticklabels(periodos)
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    plt.show()

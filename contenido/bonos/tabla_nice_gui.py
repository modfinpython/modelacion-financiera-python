# Importamos Librerías
from abc import abstractmethod
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from nicegui import ui

import plotly.graph_objects as go

class Bono:
    def __init__(
        self,
        valor_nominal,
        tasa_cupon,
        tasa_rendimiento,
        sobre_tasa,
        periodo_cupon,
        dias_vencimiento,
        dias_por_año,
    ):
        self.valor_nominal = valor_nominal  # Valor nominal
        self.tasa_cupon = tasa_cupon  # Tasa del cupón
        self.tasa_rendimiento = tasa_rendimiento  # Tasa de interés
        self.sobre_tasa = sobre_tasa  # Sobretasa
        self.periodo_cupon = periodo_cupon if periodo_cupon != 0 else dias_vencimiento  # Periodo de cada cupón
        self.dias_vencimiento = dias_vencimiento  # Días hasta el vencimiento
        self.dias_por_año = dias_por_año  # Días por año (360, 365, etc.)
        self.flujos = None  # Se definirá en subclases

    def obtener_cupones(self):
        # Calcular el número total de cupones (puede incluir decimales)
        total_cupones = self.dias_vencimiento / self.periodo_cupon
        cupones_completos = int(total_cupones)
        
        es_fraccionado = total_cupones > cupones_completos
        fraccion_cupon = total_cupones - cupones_completos if es_fraccionado else 0

        return cupones_completos, es_fraccionado, fraccion_cupon

    def obtener_intereses_devengados(self):
        cupones_completos, es_fraccionado, fraccion_cupon = self.obtener_cupones()
        longitud = cupones_completos + 1 if es_fraccionado else cupones_completos
        intereses_devengados = np.zeros(longitud)
        if es_fraccionado:
            intereses_devengados[0] = (
                (1 - fraccion_cupon)
                * (self.periodo_cupon)
                * self.valor_nominal
                * self.tasa_cupon
                / self.dias_por_año
            )

        return intereses_devengados

    def obtener_factores(self):
        cupones_completos, es_fraccionado, fraccion_cupon = self.obtener_cupones()
        longitud = cupones_completos + (1 if es_fraccionado else 0)
        factores = np.zeros(longitud)

        if es_fraccionado:
            factores = np.arange(start=fraccion_cupon, stop=fraccion_cupon + longitud)
        else:
            factores = np.arange(start=1, stop=longitud + 1)
        
        return factores

    def obtener_valores_presentes(self, tasa_rendimiento=None):
        if tasa_rendimiento is None:
            tasa_rendimiento = self.tasa_rendimiento
        if self.flujos is None:
            self.definir_flujos()  # Asegura que self.flujos esté definido

        factores = self.obtener_factores()
        descuento = (
            1
            + (tasa_rendimiento + self.sobre_tasa)
            * self.periodo_cupon
            / self.dias_por_año
        ) ** -factores

        valores_presentes = self.flujos * descuento

        return valores_presentes

    def obtener_calendario_pagos(self):
        factores = self.obtener_factores()
        dias_flujo = factores * self.periodo_cupon
        flujo_efectivo = self.definir_flujos()
        valor_presente_bruto = self.obtener_valores_presentes()
        interes_devengado = self.obtener_intereses_devengados()
        valor_presente_neto = valor_presente_bruto - interes_devengado

        df = {
            "Días Flujo": dias_flujo,
            "Flujo": flujo_efectivo,
            "Valor Presente Bruto": valor_presente_bruto,
            "Interés Devengado": interes_devengado,
            "Valor Presente Neto": valor_presente_neto,
        }

        # Convertimos al formato DataFrame con pandas

        calendario_pagos = pd.DataFrame(df)
        calendario_pagos.loc["Total"] = [
            dias_flujo[-1],
            flujo_efectivo.sum(),
            valor_presente_bruto.sum(),
            interes_devengado.sum(),
            valor_presente_neto.sum(),
        ]
        return calendario_pagos

    def obtener_medidas(self):
        precio_sucio = self.precio_sucio
        interes_devengado = self.interes_devengado
        precio_limpio = self.precio_limpio
        duracion_macaulay = self.duracion_macaulay
        duracion_modificada = self.duracion_modificada
        convexidad = self.convexidad

        datos = {
            "Concepto": [
                "Precio Sucio",
                "Interés Devengado",
                "Precio Limpio",
                "Duración Macaulay",
                "Duración Modificada",
                "Convexidad",
            ],
            "Dato": [
                precio_sucio,
                interes_devengado,
                precio_limpio,
                duracion_macaulay,
                duracion_modificada,
                convexidad,
            ],
        }

        medidas = pd.DataFrame(datos)
        medidas.set_index("Concepto", inplace=True)

        return medidas

    def calcular_precio_sucio_cambio(self, tasa_rendimiento=None):
        if tasa_rendimiento is None:
            tasa_rendimiento = self.tasa_rendimiento
        valor_presente_bruto = self.obtener_valores_presentes(
            tasa_rendimiento=tasa_rendimiento
        )
        precio_sucio = valor_presente_bruto.sum()

        return precio_sucio

    def obtener_grafico_precio_ytm(self, max, min, escenarios):
        tasa_interes_potencial = np.linspace(min, max, escenarios)
        precio_sucio = np.zeros(escenarios)

        for idx, tasa in enumerate(tasa_interes_potencial):
            precio_sucio[idx] = self.calcular_precio_sucio_cambio(tasa_rendimiento=tasa)

        datos = pd.DataFrame({'Precio': precio_sucio, 'Tasa': tasa_interes_potencial})


        return datos


    @property
    def precio_sucio(self):
        valor_presente_bruto = self.obtener_valores_presentes()
        precio_sucio = valor_presente_bruto.sum()

        return precio_sucio

    @property
    def interes_devengado(self):
        intereses_devengados = self.obtener_intereses_devengados()
        interes_devengado = intereses_devengados.sum()

        return interes_devengado

    @property
    def precio_limpio(self):
        precio_sucio = self.precio_sucio
        interes_devengado = self.interes_devengado
        precio_limpio = precio_sucio - interes_devengado

        return precio_limpio

    @property
    def duracion_macaulay(self):
        valor_presente_bruto = self.obtener_valores_presentes()
        factores = self.obtener_factores()
        proporcion = valor_presente_bruto / self.precio_sucio
        tiempo_proporcion = proporcion * factores
        duracion_macaulay = (
            tiempo_proporcion.sum() * self.periodo_cupon / self.dias_por_año
        )

        return duracion_macaulay

    @property
    def duracion_modificada(self):
        duracion_macaulay = self.duracion_macaulay
        duración_modificada = duracion_macaulay / (
            1
            + (self.tasa_rendimiento + self.sobre_tasa)
            * self.periodo_cupon
            / self.dias_por_año
        )
        return duración_modificada

    @property
    def convexidad(self):
        tasa_original = self.tasa_rendimiento
        precio_mas = self.calcular_precio_sucio_cambio(tasa_rendimiento=tasa_original + 0.0001)
        precio_menos = self.calcular_precio_sucio_cambio(tasa_rendimiento=tasa_original - 0.0001)
        precio_base = self.precio_sucio
        
        convexidad = (precio_menos + precio_mas - (2 * precio_base)) / (
            (0.0001**2) * precio_base
        )

        return convexidad

    @abstractmethod
    def definir_flujos(self):
        pass

class CuponCero(Bono):
    def definir_flujos(self):
        factores = self.obtener_factores()
        self.flujos = np.zeros(len(factores))
        self.flujos[-1] = (
            self.valor_nominal
        )  # Solo hay un flujo, el valor nominal al final

        return self.flujos

class CuponFijo(Bono):
    def definir_flujos(self):
        factores = self.obtener_factores()
        
        cupon = self.valor_nominal * self.tasa_cupon * self.periodo_cupon / self.dias_por_año
        
        if len(factores) > 1:
            cupones = np.full(len(factores), cupon)
            valor_nominal =  np.full(len(factores), 0)
            valor_nominal[-1] = self.valor_nominal
            self.flujos = cupones + valor_nominal

        else:
            self.flujos = np.array([cupon + self.valor_nominal])

        return self.flujos

class CuponVariable(Bono):
    def definir_flujos(self):
        factores = self.obtener_factores()

        cupon_0 = self.valor_nominal * self.tasa_cupon * self.periodo_cupon / self.dias_por_año
        cupon_n = self.valor_nominal * self.tasa_rendimiento * self.periodo_cupon / self.dias_por_año

        if len(factores) > 1:
            cupones = np.full(len(factores), cupon_n)
            cupones[0] = cupon_0
            valor_nominal =  np.full(len(factores), 0)
            valor_nominal[-1] = self.valor_nominal
            
            self.flujos = cupones + valor_nominal
        else:
            self.flujos = np.array([cupon_0 + self.valor_nominal])

        return self.flujos

#Parte Visual

calendario = pd.DataFrame()
datos_grafica = pd.DataFrame()
figura = go.Figure()
medidas = pd.DataFrame()

# Función para actualizar el ag-Grid con el DataFrame
def actualizar():
    valor_nominal = valor_nominal_input.value
    tasa_cupon = tasa_cupon_input.value
    tasa_rendimiento = tasa_rendimiento_input.value
    sobre_tasa = sobre_tasa_input.value
    periodo_cupon = periodo_cupon_input.value
    dias_vencimiento = dias_vencimiento_input.value
    dias_por_año = dias_por_año_input.value
    
    valor_seleccionado = opciones_radio.value

    if valor_seleccionado == 'Cero':
        bono = CuponCero(valor_nominal, tasa_cupon, tasa_rendimiento, sobre_tasa, periodo_cupon, dias_vencimiento, dias_por_año)
    elif valor_seleccionado == 'Fijo':
        bono = CuponFijo(valor_nominal, tasa_cupon, tasa_rendimiento, sobre_tasa, periodo_cupon, dias_vencimiento, dias_por_año)
    elif valor_seleccionado == 'Variable':
        bono = CuponVariable(valor_nominal, tasa_cupon, tasa_rendimiento, sobre_tasa, periodo_cupon, dias_vencimiento, dias_por_año)


    calendario = bono.obtener_calendario_pagos()
    datos_grafica = bono.obtener_grafico_precio_ytm(0.25,0.001,60)
    medidas = bono.obtener_medidas()

    
    medidas_reset = medidas.reset_index()

    medidas_tabla.columns = [{'name': col, 'label': col, 'field': col} for col in medidas_reset.columns]
    medidas_tabla.rows = medidas_reset.to_dict('records')

    calendario_reset = calendario.reset_index()
    calendario_tabla.columns = [{'name': col, 'label': col, 'field': col} for col in calendario_reset.columns]
    calendario_tabla.rows = calendario_reset.to_dict('records')
    
    figura.update_traces(overwrite=True, x=datos_grafica['Tasa'], y=datos_grafica['Precio'])
    #figura.add_trace(go.Scatter(x=[tasa_rendimiento], y=[bono.precio_sucio], mode='markers', name='Punto Específico'))
    plot.update()


with ui.row():
    ui.label('Modelo Bono').style('color: #6E93D6; font-size: 250%; font-weight: 400')
with ui.row():
    with ui.card():
        ui.label('Variables de Entrada').style('color: #6E93D6; font-size: 100%; font-weight: 400')
        # Creación de la interfaz de usuario con entradas
        valor_nominal_input = ui.number(label='Valor Nominal', value=100).props('clearable')
        tasa_cupon_input = ui.number(label='Tasa Cupón', value=0.05).props('clearable')
        tasa_rendimiento_input = ui.number(label='Tasa Rendimiento', value=0.1007).props('clearable')
        sobre_tasa_input = ui.number(label='Sobre Tasa', value=0).props('clearable')
        periodo_cupon_input = ui.number(label='Periodo', value=182).props('clearable')
        dias_vencimiento_input = ui.number(label='Plazo', value=366).props('clearable')
        dias_por_año_input = ui.number(label='Días Año', value=360).props('clearable')

        bono = CuponFijo(valor_nominal_input.value,tasa_cupon_input.value, tasa_rendimiento_input.value, sobre_tasa_input.value, periodo_cupon_input.value,dias_vencimiento_input.value,dias_por_año_input.value )
        calendario = bono.obtener_calendario_pagos()
        medidas = bono.obtener_medidas()


        datos_grafica = bono.obtener_grafico_precio_ytm(0.25,0.001,60)
        figura.add_trace(go.Scatter(x=datos_grafica['Tasa'], y=datos_grafica['Precio']))
        figura.update_layout(margin=dict(l=0, r=0, t=0, b=0))

        opciones_radio = ui.radio(['Cero', 'Fijo', 'Variable'], value='Cero').props('inline')


       # Botón para actualizar el ag-Grid con nuevos datos
        ui.button('Actualizar', on_click=actualizar)

    with ui.card().style('width: 600px; height: 660px;'):
        ui.label('Gráfica Precio vs Tasa').style('color: #6E93D6; font-size: 100%; font-weight: 400')
        plot = ui.plotly(figura).classes('w-full')

    with ui.card().style('width: 360px; height: 660px;'):
        ui.label('Medidas').style('color: #6E93D6; font-size: 100%; font-weight: 400')
        medidas_reset = medidas.reset_index()
        medidas_tabla = ui.table.from_pandas(medidas).style("width:100%;height:100%;")
        medidas_tabla.columns = [{'name': col, 'label': col, 'field': col} for col in medidas_reset.columns]
        medidas_tabla.rows = medidas_reset.to_dict('records')

with ui.row():
    with ui.card().style('width: 1260px; height: 800px;'):
        ui.label('Calendario de Pagos').style('color: #6E93D6; font-size: 100%; font-weight: 400')
        calendario_reset = calendario.reset_index()
        calendario_tabla = ui.table.from_pandas(calendario).style("width:100%;height:100%;")
        calendario_tabla.columns = [{'name': col, 'label': col, 'field': col} for col in calendario_reset.columns]
        calendario_tabla.rows = calendario_reset.to_dict('records')


ui.run()

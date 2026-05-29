'''
Archivo con las funciones para realizar cálculos de distintos tipos
'''
import numpy as np
import pandas as pd


def redondearDecimalMedio(valor: float) -> float:
    '''Redondea un número al múltiplo de 0.5 más cercano'''
    return round(valor * 2) / 2


def mediaSegura(agentes, atributo):
    '''Función auxiliar para poder hacer medias sin errores'''

    #Si no hay agentes de este tipo, se devuelve una media de 0
    if len(agentes) == 0:
        return 0.0 
    
    #Si hay agentes sobre los que calcular la media, simplemente se calcula
    return agentes.agg(atributo, np.mean)


def calcularIndiceGini(valores):
    '''Calcula el coeficiente de Gini para una lista de valores'''

    #Convertimos a array de numpy y forzamos el tipo float para evitar errores
    valores = np.array(valores).flatten().astype(float)
    
    #Si el array está vacío, devolvemos 0.0
    if len(valores) == 0:
        return 0.0


    #Si hay valores negativos, desplazamos toda la distribución hacia arriba
    if np.amin(valores) < 0:
        valores -= np.amin(valores)
    
    #Para evitar una posible división entre 0
    valores += 0.0000001

    #Ordenamos los valores porque así lo requiere el Gini
    valores = np.sort(valores)


    idx = np.arange(1, valores.shape[0] + 1)
    n = valores.shape[0]

    #Aplicamos la fórmula de Gini = [Sumatorio((2 * i - n - 1) * x_i)] / [n * Sumatorio(x_i)]
    gini = ((np.sum((2 * idx - n - 1) * valores)) / (n * np.sum(valores)))

    return gini


def calcularCorrFelicidadDinero(df_agentes):
    '''Método que calcula la correlación de Pearson entre la Felicidad y el Dinero, siendo el rango de valores posibles:
       1  = Correlación positiva perfecta
       0  = No hay relación
      -1 = Correlación negativa perfecta'''
    
    if df_agentes.empty:
        return 0.0
    
    #Usamos directamente el método de Pandas que calcula la correlación de Pearson
    return df_agentes['Felicidad'].corr(df_agentes['Dinero'])


def obtenerResumenEstadistico(df_agentes):
    '''Genera un diccionario con las métricas importantes del estado actual. Recibe como parametro una fila por cada agente en cada instante de tiempo'''

    resumen = {
        "Gini_Dinero": calcularIndiceGini(df_agentes['Dinero']),                    #Calculamos el índice de Gini
        "Correlacion_Felicidad_Dinero": calcularCorrFelicidadDinero(df_agentes),    #Calculamos la correlación entre la felicidad y el dinero
        "Felicidad_Max": df_agentes['Felicidad'].max(),                             #Coje la felicidad máxima
        "Dinero_Total_Sistema": df_agentes['Dinero'].sum()                          #Coje el dinero total
    }
    return resumen
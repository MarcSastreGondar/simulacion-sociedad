#Documento con las funciones para realizar cálculos y calcular métricas a enseñar en cualquier momento
'''

'''
import numpy as np
import pandas as pd


def redondearDecimalMedio(valor: float) -> float:
        '''Redondea un número al múltiplo de 0.5 más cercano'''
        return round(valor * 2) / 2


def calcular_indice_gini(valores):
    '''
    Calcula el coeficiente de Gini para una lista de valores.
    '''
    # Convertimos a array de numpy y forzamos el tipo float para evitar errores de casteo
    array = np.array(valores).flatten().astype(float)
    
    if len(array) == 0:
        return 0.0

    if np.amin(array) < 0:
        array -= np.amin(array)
    
    array += 0.0000001
    array = np.sort(array)
    index = np.arange(1, array.shape[0] + 1)
    n = array.shape[0]
    return ((np.sum((2 * index - n - 1) * array)) / (n * np.sum(array)))


def calcular_correlacion_felicidad_dinero(df_agentes):
    '''
    Calcula la correlación de Pearson entre Felicidad y Dinero.
    1  = Correlación positiva perfecta.
    0  = No hay relación.
    -1 = Correlación negativa (más dinero, menos felicidad).
    '''
    if df_agentes.empty:
        return 0.0
    return df_agentes['Felicidad'].corr(df_agentes['Dinero'])


def obtener_resumen_estadistico(df_agentes):
    '''
    Genera un diccionario con las métricas clave del estado actual.
    '''
    resumen = {
        "Gini_Dinero": calcular_indice_gini(df_agentes['Dinero']),
        "Correlacion_Felicidad_Dinero": calcular_correlacion_felicidad_dinero(df_agentes),
        "Felicidad_Max": df_agentes['Felicidad'].max(),
        "Dinero_Total_Sistema": df_agentes['Dinero'].sum()
    }
    return resumen
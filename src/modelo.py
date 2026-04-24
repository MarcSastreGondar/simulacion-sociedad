#safr342? =?¿=?=?=! ?¿=·$"·$$?="=$~$!-.   Documento para la lógica principal de la simulación. Incluye todos los 
# parámetros configurables y la instanciación de prácticamente todo lo que se tenga que usar y
# y los métodos que calculen y modifiquen cosas generales del programa. Básicamente el documento main.
'''
gashfd
'''

import mesa

######asfasf 3325235 q35??      CREO que esto va en el simulacionSociedad.ipynb
import pandas as pd
import numpy as np  #Para el data collector

# Imports de los agentes
from .agentes.trabajador import Trabajador
from .agentes.empresario import Empresario
from .agentes.antisistema import Antisistema



"""Modelo principal de la simulación"""
class ModeloSociedad(mesa.Model):    
    
    def __init__(self, n_trabajadores=100, n_empresarios=20, n_rebeldes=10, anchuraGrid=20, alturaGrid=20, seed=150,                        #Parámetros del modelo
                 tiempoMaxPosible=24, tiempoVital=3, energia=100, porcentajeAleatorio=0.2,     #Parámetros de los agentes en general
                 dineroInicialT=500, insatisfaccionInicialT=15, tiempoTrabajo=8, maxTiempoAlTrabajo=1.5,                                                                                    #Parámetros de los Trabajadores
                 dineroInicialE=15000, insatisfaccionInicialE=0,
                 dineroInicialA=50, insatisfaccionInicialA=50):

        super().__init__(rng=seed)
        
        # Creamos las casillas en las que pueden moverse los agentes
        self.grid = mesa.discrete_space.OrthogonalMooreGrid((anchuraGrid, alturaGrid), torus=True, random=self.random)  #torus = True para que los bordes del mapa están conectados entre sí


        # Creamos los agentes de cada tipo
        self.trabajadores = Trabajador.create_agents(self, n_trabajadores, 
                                                     tiempoMaxPosible, tiempoVital, energia, porcentajeAleatorio,
                                                     dineroInicialT, insatisfaccionInicialT, tiempoTrabajo, maxTiempoAlTrabajo)
        
        self.empresarios = Empresario.create_agents(self, n_empresarios,
                                                    tiempoMaxPosible, tiempoVital, energia, porcentajeAleatorio,
                                                    dineroInicialE, insatisfaccionInicialE)
        
        self.antisistemas = Antisistema.create_agents(self, n_rebeldes,
                                                      tiempoMaxPosible, tiempoVital, energia, porcentajeAleatorio,
                                                      dineroInicialA, insatisfaccionInicialA)        


        # Recorremos cada agente de la lista de agentes y le asignamos una casilla aleatoria
        for agente in self.agents:                
            agente.cell = self.grid.all_cells.select_random_cell()            
        
        print(f"Agentes correctamente instanciados. Se han creado {len(self.agents)} agentes, siendo {len(self.trabajadores)} trabajadores, {len(self.empresarios)} empresarios y {len(self.antisistemas)} antisistema.")   
        #self.agents.do("printCaracteristicas")
        

        #Inicializamos el data collector para que recoja los datos durante la ejecución
        self.datacollector = mesa.DataCollector(
            #Datos recojidos del modelo en general
            model_reporters={
                "Insatisfaccion_Media": lambda m: m.agents.agg("insatisfaccion", np.mean)
                },
            
            #Datos recogidos de cada agente
            agent_reporters={
                "Insatisfaccion": "insatisfaccion"
                }
        )


    """Paso de tiempo de toda la simulación"""
    def step(self):        

        # Ejecutamos el step() de todos los agentes en orden aleatorio.
        self.agents.shuffle_do("step")

        #Recojemos los datos de todo el modelo una vez hayan actuado los agentes
        self.datacollector.collect(self)
        
        
        #r325tr32t3"$!$·/y5764 4675346325 1212  Aquí puedes añadir lógica global # - Calcular Gini - Calcular grievance medio - Detectar si hay revueltas activas - Aplicar posibles redistribuciones, etc.
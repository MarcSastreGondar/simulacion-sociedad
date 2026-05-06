#safr342? =?¿=?=?=! ?¿=·$"·$$?="=$~$!-.   Documento para la lógica principal de la simulación. Incluye todos los 
# parámetros configurables y la instanciación de prácticamente todo lo que se tenga que usar y
# y los métodos que calculen y modifiquen cosas generales del programa. Básicamente el documento main.
'''
gashfd
'''

import mesa
from mesa.experimental.scenarios import Scenario


import pandas as pd
import numpy as np  #Para el data collector

# Imports de los agentes
from agentes.trabajador import Trabajador
from agentes.empresario import Empresario
from agentes.antisistema import Antisistema

'''Escenario de la sociedad, el cual contiene todos los parámetros de la ejecución'''
class EscenarioSociedad(Scenario):
    #Tamaño del tablero en el que pueden estar los agentes
    anchuraGrid: int = 20
    alturaGrid: int = 20

    #Generador de números pseudoaleatorios para poder repetir resultados en las ejecuciones
    rng: int = 150

    # Parámetros de configuración de los agentes en general
    #Variables relacionadas con el tiempo del que dispone el agente para actuar cada día
    tiempoMaxPosible: float = 24.0            #Tiempo en horas que el agente tiene disponibles en un dia
    tiempoVital: float = 8.0                  #Tiempo en horas que se utiliza en hacer acciones necesarias para la supervivencia (comida, higiene, etc.)

    #Energia para realizar las acciones
    energiaMax: int = 100               #Energia máxima que puede llegar a tener este agente totalmente descansado
    energiaMaxObtenible: int = 180      #Energia máxima que pueden llegar a tener los agentes

    felicidadMax: int = 100

    #Cantidad de cada tipo de agente
    n_trabajadores: int = 100               #Cantidad de trabajadores
    n_empresarios: int = 20                 #Cantidad de empresarios
    n_antisistemas: int = 10                 #Cantidad de agentes antisistema

    porcentajeAleatorio: float = 0.5

    umbralDepresion: int = 10        #A partir de qué punto de felicidad empezamos a considerar que el agente tiene depresión
    mesesSuicidio: int = 5          #Cantidad de meses con depresión acumulados que llevan al agente a ser borrado


    #Distancia a la que los agentes pueden ver, en todas direcciones
    visionAgente: int = 3
    movimientoAgente: int = 1

    gastosDiarios: int = 20         #Dinero que se gasta cada día en cosas cuotidianas

    # Parámetros de configuración de agentes específicos
    #Trabajador
    dineroInicialT: int = 500
    felicidadInicialT: int = 85

    tiempoTrabajo: float = 8.0          #Horas que dedica a trabajar de manera directa
    maxTiempoAlTrabajo: float = 1.5     #Cantidad máxima de tiempo en horas que puede tardar el agente en transportarse al trabajo (ida + vuelta)


    #Empresario
    dineroInicialE: int = 15000
    felicidadInicialE: int = 100


    #Antisistema
    dineroInicialA: int = 50
    felicidadInicialA: int = 50


    #Parámetros de configuración necesarios de las acciones que pueden realizar los agentes:
    #Parámetros comunes entre todos los agentes:
    #Dormir
    horasMinimasDormir: float = 4.0
    horasMaximasDormir: float = 8.0
    
    #Entrenar
    energiaEntrenar: int = 10
    tiempoEntrenar: float = 1.5              #1.5 horas
    cuotaGimnasio: int = 50
    aumentoEnergiaMaxEntrenar: int = 5
    aumentoFelicidadEntrenar: int = 1
    

'''Modelo principal de la simulación'''
class ModeloSociedad(mesa.Model):    
    
    def __init__(self, escenario:EscenarioSociedad | None = None):

        #Si no se ha instanciado con un EscenarioSociedad por parámetro, lo instanciamos ahora
        if escenario is None:
            escenario = EscenarioSociedad()

        super().__init__(scenario=escenario)

        # Si los agentes no caben bien dentro de las casillas, aumentamos la cantidad de casillas
        totalAgentes = escenario.n_antisistemas + escenario.n_empresarios + escenario.n_trabajadores
        auxTotalAgentes = 2.5 * totalAgentes                                                             #Para quepan mejor y puedan moverse

        while(auxTotalAgentes > (escenario.alturaGrid * escenario.anchuraGrid)):
            escenario.alturaGrid += 1
            escenario.anchuraGrid += 1


        # Creamos las casillas en las que pueden moverse los agentes
        self.grid = mesa.discrete_space.OrthogonalMooreGrid((self.scenario.anchuraGrid, self.scenario.alturaGrid), torus=True, random=self.random)  #torus = True para que los bordes del mapa están conectados entre sí

        # Creamos los agentes de cada tipo
        self.trabajadores = Trabajador.create_agents(self, self.scenario.n_trabajadores)
        
        self.empresarios = Empresario.create_agents(self, self.scenario.n_empresarios)
        
        self.antisistemas = Antisistema.create_agents(self, self.scenario.n_antisistemas)        


        # Recorremos cada agente de la lista de agentes y le asignamos una casilla aleatoria
        for agente in self.agents:                
            agente.cell = self.grid.all_cells.select_random_cell()
        

        #####TEMP!!!! Hacemos algunos step de cada agente para verificar que funcionan correctamente. De esta manera, nos saltará un error detallado al
        #ejecutar (en el gráfico de Solara los errores no son nada descriptivos o ni aparecen)
        self.agents.shuffle_do("step")
        self.agents.shuffle_do("step")
        self.agents.shuffle_do("step")


        print(f"Agentes correctamente instanciados. Se han creado {len(self.agents)} agentes, siendo {len(self.trabajadores)} trabajadores, {len(self.empresarios)} empresarios y {len(self.antisistemas)} antisistema.")   
        #self.agents.do("printCaracteristicas")
        
        
        #Inicializamos el data collector para que recoja los datos durante la ejecución
        #Datos recogidos del modelo en general
        model_reporters={
            "Felicidad_Media": lambda m: m.agents.agg("felicidad", np.mean)
        }
            
        #Datos recogidos de cada agente
        agent_reporters={
            "Felicidad": "felicidad"
        }

        #Lo inicializamos
        self.datacollector = mesa.DataCollector(model_reporters=model_reporters, agent_reporters=agent_reporters)

        self.running = True
        self.datacollector.collect(self)



    def esNuevoDia(self):
        '''Poner mejor nombre? Método que determina si han pasado 24 horas (steps) para empezar un nuevo día. Empieza los eventos diarios propios de los agentes'''
        ######ESTO DEBERÍA IMPLEMENTARLO COMO UN MÉTODO QUE SE LEE EN CADA STEP, O COMO UN recurring_event??? (CREO QUE COMO UN recurring_event() mejor)

    '''Paso de tiempo de toda la simulación'''
    def step(self):        

        # Ejecutamos el step() de todos los agentes en orden aleatorio.
        self.agents.shuffle_do("step")

        #Recojemos los datos de todo el modelo una vez hayan actuado los agentes
        self.datacollector.collect(self)        
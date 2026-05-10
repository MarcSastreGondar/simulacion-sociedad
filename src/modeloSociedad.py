#safr342? =?¿=?=?=! ?¿=·$"·$$?="=$~$!-.   Documento para la lógica principal de la simulación. Incluye todos los 
# parámetros configurables y la instanciación de prácticamente todo lo que se tenga que usar y
# y los métodos que calculen y modifiquen cosas generales del programa. Básicamente el documento main.
'''
gashfd
'''

import mesa
from mesa.experimental.scenarios import Scenario
from mesa.time import Schedule


import pandas as pd
import numpy as np  #Para el data collector

# Imports de los agentes
from agentes.trabajador import Trabajador
from agentes.empresario import Empresario
from agentes.antisistema import Antisistema

'''Escenario de la sociedad, el cual contiene todos los parámetros de la ejecución. El valor de los parámetros de los recursos (como la energia, felicidad, etc.) deben ser
   positivos en caso de que quiera que se aumenten o negativos si se quieren disminuir excepto en el caso del tiempo, que debe ser siempre positivo.'''
class EscenarioSociedad(Scenario):
    #Tamaño del tablero en el que pueden estar los agentes (se adapta automáticamente en caso de ser demasiado pequeño)
    anchuraGrid: int = 15
    alturaGrid: int = 15

    #Generador de números pseudoaleatorios para poder repetir resultados en las ejecuciones
    rng: int = 150

    # Parámetros de configuración de los agentes en general
    #Variables relacionadas con el tiempo del que dispone el agente para actuar cada día
    tiempoMaxPosible: float = 24.0            #Tiempo en horas que el agente tiene disponibles en un dia
    tiempoVital: float = 2.0                  #Tiempo en horas que se utiliza en hacer acciones necesarias para la supervivencia (comida, higiene, etc.). No incluye dormir

    #Energia para realizar las acciones
    energiaMax: int = 100               #Energia máxima que puede llegar a tener este agente totalmente descansado
    energiaMinObtenible: int = 50       #Energia mínima que pueden llegar a tener los agentes
    energiaMaxObtenible: int = 180      #Energia máxima que pueden llegar a tener los agentes

    felicidadMax: float = 100.0

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


    #Cambios diarios en los recursos de los agentes
    reduccionDiariaFelicidad: int = -2          #Cada día se reduce en 2 la felicidad del agente

    porcentajeGastosCuotidianos: float = 0.01   #Gastan un 1% de su dinero en gastos cuotidianos, con un máximo y mínimo
    gastosDiariosMin: int = -10                 #Dinero que se gasta cada día en cosas cuotidianas
    gastosDiariosMax: int = -30

    # Parámetros de configuración de agentes específicos
    #Trabajador
    dineroInicialT: int = 500
    felicidadInicialT: float = 85

    #Empresario
    dineroInicialE: int = 15000
    felicidadInicialE: float = 100

    #Antisistema
    dineroInicialA: int = 50
    felicidadInicialA: float = 50


    #Parámetros de configuración necesarios de las acciones que pueden realizar los agentes:
    #Parámetros comunes entre todos los agentes:
    #Dormir
    horasMinimasDormir: float = 4.0
    horasMaximasDormir: float = 8.0
    felicidadDormirMal: float = -2
    felicidadDormirBien: float = 3
    
    #Entrenar
    energiaEntrenar: int = -10
    tiempoEntrenar: float = 1.5              #1.5 horas
    cuotaGimnasio: int = -50
    felicidadEntrenar: int = 1
    aumentoEnergiaMaxEntrenar: int = 5

    #Compra lujosa
    costeLujo: int = -300
    felicidadLujo: float = 6
    tiempoLujo: int = 1

    #Ocio
    energiaOcio: int = -3
    tiempoOcio: float = 3                       #3 horas
    costeOcio: int = -25
    felicidadOcio: float = 6

    #Comida basura
    energiaComidaBasura: int = -2
    felicidadComidaBasura: float = 2
    tiempoComidaBasura: float = 1               #Tiempo placeholder para simular un paso de tiempo en el step (para no poder hacer esta acción infinitamente)
    porcentajeAhorro: int = 0.2                 #Porcentaje de los gastos cuotidianos que se ahorran al comer comida basura
    reduccionEnergiaMaxComidaBasura: int = -1


    #Parámetros de las acciones de los trabajadores:
    sueldoMedio: int = 1500                 #Dinero de 1 sueldo completo al mes.
    diasLaborablesSemanales: int = 5        #Cantidad de días que trabajarán cada semana (no podrán trabajar ni más ni menos)
    diasLaborablesAlMes: int = 22           #Suponemos que trabajan, de media, 22 días al mes

    #Trabajar
    tiempoTrabajo: float = 8.0          #Horas que dedica a trabajar de manera directa
    maxTiempoAlTrabajo: float = 1.5     #Cantidad máxima de tiempo en horas que puede tardar el agente en transportarse al trabajo (ida + vuelta)
    energiaTrabajar: int = -10
    felicidadTrabajar: float = -5

    #TrabajoDoble. Son necesarios pocos parámetros porque es simplemente el doble de trabajar
    reduccionEnergiaMaxDobleTrabajo: int = -2

    #Teletrabajar
    porcentajeSueldoTeletrabajo: float = 0.8            #Porcentaje del sueldo normal que se cobra en el trabajo (si es < 1, se cobra menos teletrabajando)
    porcentajeEnergiaTeletrabajo: float = 0.6           #Porcentaje de la energia gastada en el trabajo (si es < 1, se usa menos teletrabajando)

    
    #Contagiar Felicidad (si está feliz, hace más feliz a la gente que tiene cerca)
    umbralContagiarFelicidad: int = 90             #A partir de qué punto contiaga la felicidad a sus vecinos
    felicidadContagiarTrabajador: float = 0.5           #Cantidad de felicidad que aporta a sus vecinos


    #Parámetros de las acciones de los empresarios:


    #Parámetros de las acciones de los antisistema:
    

# Función auxiliar para poder recolectar los datos de manera segura sin que haya errores
def media_segura(agentes, atributo):
    #Si no hay agentes de este tipo, se devuelve una media de 0
    if len(agentes) == 0:
        return 0.0 
    
    #Si hay agentes sobre los que calcular la media, simplemente se calcula
    return agentes.agg(atributo, np.mean)

'''Modelo principal de la simulación'''
class ModeloSociedad(mesa.Model):    
    
    def __init__(self, n_trabajadores=10, n_empresarios=5, n_antisistemas=5):
        
        #Instanciamos el escenario con los parámetros que se utilizarán para configurar la simulación
        escenario = EscenarioSociedad()        

        #En caso de ser necesario, actualizamos los parámetros del escenario antes de crear el modelo
        # Si los agentes no caben bien dentro de las casillas, aumentamos la cantidad de casillas
        totalAgentes = n_trabajadores + n_empresarios + n_antisistemas
        auxTotalAgentes = 2.5 * totalAgentes                                                             #Para que quepan mejor y puedan moverse


        while(auxTotalAgentes > (escenario.alturaGrid * escenario.anchuraGrid)):
            escenario.alturaGrid += 1
            escenario.anchuraGrid += 1

    
        super().__init__(scenario=escenario)

        # Creamos las casillas en las que pueden moverse los agentes
        self.grid = mesa.discrete_space.OrthogonalMooreGrid((self.scenario.anchuraGrid, self.scenario.alturaGrid), torus=True, random=self.random)  #torus = True para que los bordes del mapa están conectados entre sí

        # Creamos los agentes de cada tipo
        self.trabajadores = Trabajador.create_agents(self, n_trabajadores)
        
        self.empresarios = Empresario.create_agents(self, n_empresarios)
        
        self.antisistemas = Antisistema.create_agents(self, n_antisistemas)        


        # Recorremos cada agente de la lista de agentes y le asignamos una casilla aleatoria
        for agente in self.agents:                
            agente.cell = self.grid.all_cells.select_random_cell()
        

        #####TEMP!!!! Hacemos algunos step de cada agente para verificar que funcionan correctamente. De esta manera, nos saltará un error detallado al
        #ejecutar (en el gráfico de Solara los errores no son nada descriptivos o ni aparecen)
        self.agents.shuffle_do("step")
        self.agents.shuffle_do("step")
        self.agents.shuffle_do("step")

        print("Valores vars cant de agentes:", n_trabajadores, n_empresarios, n_antisistemas)
        print(f"Agentes correctamente instanciados. Se han creado {len(self.agents)} agentes, siendo {len(self.trabajadores)} trabajadores, {len(self.empresarios)} empresarios y {len(self.antisistemas)} antisistema.")   
        #self.agents.do("printCaracteristicas")
        
        
        #Inicializamos el data collector para que recoja los datos durante la ejecución
        #Datos recogidos del modelo
        model_reporters={
            # Gráficos generales
            "Felicidad Media": lambda m: media_segura(m.agents, "felicidad"),
            "Energia Media": lambda m: media_segura(m.agents, "energia"),
            "Dinero Medio": lambda m: media_segura(m.agents, "dinero"),

            # Específicos de Trabajadores con chequeo de existencia
            "Felicidad Media Trabajadores": lambda m: media_segura(m.agents.select(lambda a: a.tipo == "Trabajador"), "felicidad"),
            "Energia Media Trabajadores": lambda m: media_segura(m.agents.select(lambda a: a.tipo == "Trabajador"), "energia"),
            "Dinero Medio Trabajadores": lambda m: media_segura(m.agents.select(lambda a: a.tipo == "Trabajador"), "dinero"),

            # Específicos de Empresarios
            "Felicidad Media Empresarios": lambda m: media_segura(m.agents.select(lambda a: a.tipo == "Empresario"), "felicidad"),
            "Energia Media Empresarios": lambda m: media_segura(m.agents.select(lambda a: a.tipo == "Empresario"), "energia"),
            "Dinero Medio Empresarios": lambda m: media_segura(m.agents.select(lambda a: a.tipo == "Empresario"), "dinero"),

            # Específicos de Antisistemas
            "Felicidad Media Antisistema": lambda m: media_segura(m.agents.select(lambda a: a.tipo == "Antisistema"), "felicidad"),
            "Energia Media Antisistema": lambda m: media_segura(m.agents.select(lambda a: a.tipo == "Antisistema"), "energia"),
            "Dinero Medio Antisistema": lambda m: media_segura(m.agents.select(lambda a: a.tipo == "Antisistema"), "dinero")
        }
            
        #Datos recogidos de cada agente
        agent_reporters={
            "Felicidad": "felicidad",
            "Energia": "energia",
            "Dinero": "dinero"
        }

        #Creamos los eventos que ocurrirán periódicamente durante la ejecución
        #Paso del tiempo de 1 día
        horasDia = 24.0
        self.schedule_recurring(
            self.cambioDia,
            Schedule(interval=horasDia)
        )

        #Paso de tiempo de 1 semana
        horasSemana = horasDia * 7
        self.schedule_recurring(
            self.cambioSemana,
            Schedule(interval=horasSemana)
        )

        #Lo inicializamos
        self.datacollector = mesa.DataCollector(model_reporters=model_reporters, agent_reporters=agent_reporters)
        self.datacollector.collect(self)


    def cambioDia(self):
        '''Método que determina si han pasado 24 horas (steps) para empezar un nuevo día. Empieza los eventos diarios propios de los agentes'''
        #Llamamos al método que se encarga de las modificaciones diarias propias de todos los agentes
        self.agents.shuffle_do("avanceDiarioGeneral")

        #Llamamos al método que se encarga de las modificaciones diarias propias de cada tipo de agente
        self.agents.shuffle_do("avanceDiarioEspecifico")

    
    def cambioSemana(self):
        '''Método que determina si han pasado 24 horas (steps) para empezar un nuevo día. Empieza los eventos diarios propios de los agentes'''

        #Llamamos al método que se encarga de las modificaciones diarias propias de cada tipo de agente
        self.agents.shuffle_do("avanceSemanalEspecifico")


    '''Paso de tiempo de toda la simulación'''
    def step(self):        

        #Antes de iniciar los steps, comprobamos que quedan agentes vivos
        if len(self.agents) > 0:
            # Ejecutamos el step() de todos los agentes en orden aleatorio.
            self.agents.shuffle_do("step")

            #Recojemos los datos de todo el modelo una vez hayan actuado los agentes
            #if self.steps % 20 == 0:
            self.datacollector.collect(self)

        else:
            print("ENTRA AQUÍ??")
            #Si no quedan agentes, paramos la ejecución
            self.running = False
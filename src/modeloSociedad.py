#safr342? =?¿=?=?=! ?¿=·$"·$$?="=$~$!-.   Documento para la lógica principal de la simulación. Incluye todos los 
# parámetros configurables y la instanciación de prácticamente todo lo que se tenga que usar y
# y los métodos que calculen y modifiquen cosas generales del programa. Básicamente el documento main.
'''
gashfd
'''
import os
from datetime import datetime

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
    n_trabajadores: int = 5               #Cantidad de trabajadores
    n_empresarios: int = 5                 #Cantidad de empresarios
    n_antisistemas: int = 5                 #Cantidad de agentes antisistema

    porcentajeAleatorio: float = 0.25

    umbralDepresion: float = 10.0        #A partir de qué punto de felicidad empezamos a considerar que el agente tiene depresión
    mesesSuicidio: int = 5          #Cantidad de meses con depresión acumulados que llevan al agente a ser borrado


    visionAgente: int = 3           #Distancia a la que los agentes pueden ver, en todas direcciones
    movimientoAgente: int = 2       #Distancia a la que se pueden, como máximo, mover los agentes, en todas direcciones


    #Cambios temporales en los recursos de los agentes
    reduccionDiariaFelicidad: int = -2          #Cada día se reduce en 2 la felicidad del agente

    porcentajeGastosCuotidianos: float = 0.01   #Gastan un 1% de su dinero en gastos cuotidianos, con un máximo y mínimo
    gastosDiariosMin: int = -10                 #Dinero que se gasta cada día en cosas cuotidianas
    gastosDiariosMax: int = -30

    # Parámetros de configuración de agentes específicos y modificaciones temporales de sus recursos
    #Trabajador
    dineroInicialT: int = 500
    felicidadInicialT: float = 85
    sueldoMinimo: int = 600
    sueldoMedio: int = 1500                 #Dinero de 1 sueldo completo al mes.
    diasLaborablesSemanales: int = 5        #Cantidad de días que trabajarán cada semana (no podrán trabajar ni más ni menos)
    diasLaborablesAlMes: int = 22           #Suponemos que trabajan, de media, 22 días al mes

    #Empresario
    dineroInicialE: int = 15000
    felicidadInicialE: float = 100

    #Antisistema
    dineroInicialA: int = 50
    felicidadInicialA: float = 50
    odioMaximo: int = 100

    reduccionPasivaOdio: int = -5


    #Parámetros de configuración necesarios de las acciones que pueden realizar los agentes:
    #Acciones comunes para todos los agentes:
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
    aumentoEnergiaMaxEntrenar: int = 2

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
    porcentajeAhorro: int = 0.2                 #Porcentaje de los gastos cuotidianos que se ahorran al comer comida basura
    reduccionEnergiaMaxComidaBasura: int = -1
    maxComidasPorDia: int = 2                   #Cantidad máxima de comidas que puede reemplazar cada día un agente por comida basura


    #Parámetros de las acciones de los trabajadores:
    #Trabajar
    tiempoTrabajo: float = 8.0          #Horas que dedica a trabajar de manera directa
    maxTiempoAlTrabajo: float = 1.5     #Cantidad máxima de tiempo en horas que puede tardar el agente en transportarse al trabajo (ida + vuelta)
    energiaTrabajar: int = -10

    felicidadTrabajar: float = -5
    felicidadMaxTrabajar: float = 0     #Cantidad máxima de felicidad que puede aportarle trabajar

    #TrabajoDoble. Son necesarios pocos parámetros porque es simplemente el doble de trabajar
    reduccionEnergiaMaxDobleTrabajo: int = -2

    #Teletrabajar
    porcentajeSueldoTeletrabajo: float = 0.8            #Porcentaje del sueldo normal que se cobra en el trabajo (si es < 1, se cobra menos teletrabajando)
    porcentajeEnergiaTeletrabajo: float = 0.6           #Porcentaje de la energia gastada en el trabajo (si es < 1, se usa menos teletrabajando)

    #Estudiar      
    energiaEstudiar: int = -30
    felicidadEstudiar: float = -5
    costeEstudiar: int = -200
    aumentoSueldoEstudiar: int = 100
    aumentoFelicidadTrabajoEstudiar: float = 1         
    tiempoEstudiar: float = (24 * 5)                    #5 días

    #Contagiar Felicidad pasivamente
    umbralContagiarFelicidadT: float = 90.0             #A partir de qué punto contiaga la felicidad a sus vecinos
    felicidadContagiarT: float = 0.5                #Cantidad de felicidad que aporta a sus vecinos


    #Parámetros de las acciones de los empresarios:
    #Invertir
    tiempoInvertir: float = 2                  #2 horas
    energiaInvertir: int = -5
    felicidadInvertir: float = 1               #Sumamos un poco de felicidad ya que, aunque gana dinero, es un poco estresante
    porcentajeDineroInvertir: float = 0.01     #Aumenta su patrimonio en un 1%

    #Bonificación Monetaria
    umbralFelicidadBonificacionMonetaria: float = 50        #Dar recompensas monetarias a los Trabajadores que sólo tengan menos de una cierta cantidad de felicidad
    dineroPorTrabajadorBonificacion: int = 100              #Cantidad de dinero que gana el Trabajador (y el que pierde el empresario)
    aumentoFelicidadTrabajadorBonificacion: float = 10
    tiempoBonificacion: float = 1.0                         #1 hora


    #Generacion Pasiva de Dinero
    dineroPasivoPorTrabajador: int = 10


    #Contagiar Felicidad pasivamente
    umbralContagiarFelicidadE: float = 90.0
    felicidadContagiarE: float = 0.5          #Cantidad de felicidad que le da a los Trabajadores cercanos


    #Parámetros de las acciones de los antisistema:
    #Robar
    porcentajeDineroRobado: float = 0.1                 #Porcentaje del dinero que le es robado al agente y que recibe el Antisistema
    felicidadAtracado: float = -10                   
    tiempoAtracar: float = 1.5
    energiaAtracar: int = -5
    felicidadAtracar: float = 2
    odioAtracar: int = 20                               #Cantidad de odio que gana el antisistema

    #Quejarse
    felicidadQuejarse: float = -1                   #Felicidad que pierde el antisistema al quejarse
    felicidadQuejarseReceptor: float = -2           #Felicidad que pierden los oyentes al escuchar al antisistema quejarse
    energiaQuejarse: int = -3
    tiempoQuejarse: float = 1

    #Vandalismo
    felicidadVandalismo: float = 3
    energiaVandalismo: int = -3
    dineroVandalismo: int = -5                      #Dinero para gastar en material necesario para el vandalismo
    tiempoVandalismo: float = 1.5                   #1.5 horas por cada Empresario cercano
    odioVandalismo: int = 5                         #Cantidad de odio que recibe el Antisistema
    felicidadVandalismoEmpresario: float = -4
    dineroVandalismoEmpresario: int = -200          #Dinero que pierde el Empresario en reparaciones

    #Contagiar Odio pasivamente
    umbralContagiarOdio: float = 50.0
    felicidadContagiarA: float = -1          #Cantidad de felicidad que le da a los trabajadores cercanos

    

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

        print(f"Agentes correctamente instanciados. Se han creado {len(self.agents)} agentes, siendo {len(self.trabajadores)} trabajadores, {len(self.empresarios)} empresarios y {len(self.antisistemas)} antisistema.")   
        
        
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
        agent_reporters = {
            "Tipo": "tipo",
            "Estado": "estado",
            "Felicidad": "felicidad",
            "Energia": "energia",
            "Dinero": "dinero"
        }

        #Lo inicializamos
        self.datacollector = mesa.DataCollector(model_reporters=model_reporters, agent_reporters=agent_reporters)
        self.datacollector.collect(self)


        #Creamos los eventos que ocurrirán periódicamente durante la ejecución
        #Paso de tiempo de 1 semana
        horasDia = 24.0
        horasSemana = horasDia * 7

        self.schedule_recurring(
            self.cambioSemana,
            Schedule(interval=horasSemana, start=1)
        )
        
        #Paso del tiempo de 1 día
        self.schedule_recurring(
            self.cambioDia,
            Schedule(interval=horasDia, start=1)
        )


    def exportarDatos(self):
        '''Método para guardar los datos recolectados durante la simulación en la carpeta de resultados'''
        if not os.path.exists("../resultados"):
            os.makedirs("../resultados")
        
        # Generamos un nombre basado en la fecha y hora actuales
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Exportamos los datos del modelo
        model_df = self.datacollector.get_model_vars_dataframe()
        model_df.to_csv(f"../resultados/sim_{timestamp}_modelo.csv", index_label="Step")
        
        # Exportamos los datos de los agentes
        agent_df = self.datacollector.get_agent_vars_dataframe()
        agent_df.to_csv(f"../resultados/sim_{timestamp}_agentes.csv")
        
        print(f"Datos exportados correctamente como sim_{timestamp}")


    def comprobarAgentesMuertos(self):
        '''Método que analiza todos los agentes y elimina aquellos que estén muertos. Si ya no quedan agentes vivos, acaba la simulación'''

        agentesMuertos = []

        #Comprobamos si ya se ha llegado al límite de agentes
        if len(self.agents) == 1:
            print("Parando simulación: Todos los agentes han sido eliminados de la sociedad")
            self.running = False
        
        else:

            #Recorremos cada agente y, si está muerto, lo guardamos
            for agente in self.agents:
                if agente.estado == "Muerto":

                    agentesMuertos.append(agente)


            for agenteMuerto in agentesMuertos:

                #Lo comprobamos en cada iteración para evitar que se eliminen todos los agentes restantes
                if len(self.agents) == 1:
                        print("Parando simulación: Todos los agentes han sido eliminados de la sociedad")
                        self.running = False
                        break
                else:
                    agenteMuerto.remove()
        

    
    def cambioDia(self):
        '''Método que determina si han pasado 24 horas (steps) para empezar un nuevo día. Empieza los eventos diarios propios de los agentes'''
        
        if self.running:
            #Llamamos al método que se encarga de las modificaciones diarias propias de todos los agentes
            self.agents.shuffle_do("avanceDiarioGeneral")

            #Llamamos al método que se encarga de las modificaciones diarias propias de cada tipo de agente
            self.agents.shuffle_do("avanceDiarioEspecifico")

    def cambioSemana(self):
        '''Método que determina si han pasado 24 horas (steps) para empezar un nuevo día. Empieza los eventos diarios propios de los agentes'''
        
        if self.running:
            #Llamamos al método que se encarga de las modificaciones diarias propias de cada tipo de agente
            self.agents.shuffle_do("avanceSemanalEspecifico")


    def step(self):        
        '''Paso de tiempo de toda la simulación'''

        #Aseguramos de que el modelo siga activo
        if self.running:
            
            # Ejecutamos el step() de todos los agentes en orden aleatorio.
            self.agents.shuffle_do("step")

            #Recojemos los datos de todo el modelo una vez hayan actuado los agentes
            self.datacollector.collect(self)

            #Miramos si durante el paso anterior ha muerto algún agente, en cuyo caso lo eliminamos del modelo. Si no quedan agentes, acabamos la ejecución
            self.comprobarAgentesMuertos()
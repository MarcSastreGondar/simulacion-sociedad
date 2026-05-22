#safr342? =?¿=?=?=! ?¿=·$"·$$?="=$~$!-.   Documento para la lógica principal de la simulación. Incluye todos los 
# parámetros configurables y la instanciación de prácticamente todo lo que se tenga que usar y
# y los métodos que calculen y modifiquen cosas generales del programa. Básicamente el documento main.
'''
gashfd
'''
import os
from datetime import datetime

import json


import mesa
from mesa.experimental.scenarios import Scenario
from mesa.time import Schedule


import pandas as pd
import numpy as np  #Para el data collector

# Imports de los agentes
from agentes.trabajador import Trabajador
from agentes.empresario import Empresario
from agentes.antisistema import Antisistema

from metricas import mediaSegura

'''Escenario de la sociedad, el cual contiene todos los parámetros de la ejecución. El valor de los parámetros de los recursos (como la energia, felicidad, etc.) deben ser
   positivos en caso de que quiera que se aumenten o negativos si se quieren disminuir excepto en el caso del tiempo, que debe ser siempre positivo.'''
class EscenarioSociedad(Scenario):
    #Tamaño del tablero en el que pueden estar los agentes (se adapta automáticamente en caso de ser demasiado pequeño)
    anchuraGrid: int = 15
    alturaGrid: int = 15

    #Generador de números pseudoaleatorios para poder repetir resultados en las ejecuciones
    rng: int = 150

    # Parámetros de configuración de los agentes en general

    #Estados posibles
    estadoFeliz: str = "Feliz"
    estadoDeprimido: str = "Deprimido"
    estadoMuerto: str = "Muerto"

    #Variables relacionadas con el tiempo del que dispone el agente para actuar cada día
    tiempoMaxPosible: float = 24.0            #Tiempo en horas que el agente tiene disponibles en un dia
    tiempoVital: float = 2.0                  #Tiempo en horas que se utiliza en hacer acciones necesarias para la supervivencia (comida, higiene, etc.). No incluye dormir

    #Energia para realizar las acciones
    energiaMax: int = 100               #Energia máxima que puede llegar a tener este agente totalmente descansado
    energiaMinObtenible: int = 50       #Energia mínima que pueden llegar a tener los agentes
    energiaMaxObtenible: int = 180      #Energia máxima que pueden llegar a tener los agentes

    felicidadMax: float = 100.0

    #Cantidad de cada tipo de agente
    cantTrabajadores: int = 5               #Cantidad de trabajadores
    cantEmpresarios: int = 5                 #Cantidad de empresarios
    cantAntisistemas: int = 5                 #Cantidad de agentes antisistema

    porcentajeAleatorio: float = 0.25

    umbralDepresion: float = 10.0        #A partir de qué punto de felicidad empezamos a considerar que el agente tiene depresión
    mesesSuicidio: int = 6               #Cantidad de meses con depresión acumulados que llevan al agente a ser borrado


    visionAgente: int = 3           #Distancia a la que los agentes pueden ver, en todas direcciones
    movimientoAgente: int = 2       #Distancia a la que se pueden, como máximo, mover los agentes, en todas direcciones

    #Relacionados con el Entrenamiento de los agentes y el Q-Learning
    episodiosEntrenamiento: int = 30       #Cantidad de simulaciones enteras que deben realizarse para entrenar a los agentes
    maxStepsEpisodio: int = 25       #Cantidad máxima de steps que puede haber en 1 sólo ciclo de entrenamiento
    
    alfaQ: float = 0.1
    gammaQ: float = 0.9
    epsilonQ: float = 1.0
    reduccionEpsilonEpisodio: float = 0.05  #Cantidad que se reduce el Epsilon en cada ciclo completo de entrenamiento
    epsilonMinimo: float = 0.01             #Siempre un 1% de probabilidades de realizar una acción aleatoria
    epsilonSimulacion: float = 0.005          #Probabilidad de explorar en una simulación real

    porcentajeDineroRecompensa: float = 0.05    #Qué porcentaje del dinero perdido se resta a la recompensa obtenida


    porcentajePocaEnergiaQ: float = 0.33        #Poca energía si energiaAgente < energiaMax * porcentajePocaEnergiaQ
    porcentajeMediaEnergiaQ: float = 0.66       #Media energía si energiaAgente < energiaMax * porcentajeMediaEnergiaQ

    divisionPocoDinero: int = 5                 #Dinero bajo si dineroAgente < sueldoMedio / divisionPocoDinero
    multiplicacionMedioDinero: int = 2          #Dinero alto si dineroAgente > sueldoMedio * multiplicacionMedioDinero


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
    sueldoMedio: int = 1200                 #Dinero de 1 sueldo completo al mes.
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
    maxDormirPorDia: int = 1
    
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

    

'''Modelo principal de la simulación'''
class ModeloSociedad(mesa.Model):    
    
    def __init__(self, cantTrabajadores=10, cantEmpresarios=5, cantAntisistemas=5, episodiosEntrenamiento=10):
        
        #Instanciamos el escenario con los parámetros que se utilizarán para configurar la simulación
        escenario = EscenarioSociedad()        

        #En caso de ser necesario, actualizamos los parámetros del escenario antes de crear el modelo
        # Si los agentes no caben bien dentro de las casillas, aumentamos la cantidad de casillas
        totalAgentes = cantTrabajadores + cantEmpresarios + cantAntisistemas
        auxTotalAgentes = 2.5 * totalAgentes                                                             #Para que quepan mejor y puedan moverse


        while(auxTotalAgentes > (escenario.alturaGrid * escenario.anchuraGrid)):
            escenario.alturaGrid += 1
            escenario.anchuraGrid += 1

    
        super().__init__(scenario=escenario)

        self.modoEntrenamiento = False  # Si es True, entrenamiento (actualiza la matriz Q). Si es False, es una simulación con lo que ya se sabe
        self.episodiosEntrenamiento = episodiosEntrenamiento

        self.cantTrabajadores = cantTrabajadores
        self.cantEmpresarios = cantEmpresarios
        self.cantAntisistemas = cantAntisistemas

        # Creamos las casillas en las que pueden moverse los agentes
        self.grid = mesa.discrete_space.OrthogonalMooreGrid((self.scenario.anchuraGrid, self.scenario.alturaGrid), torus=True, random=self.random)  #torus = True para que los bordes del mapa están conectados entre sí
        
        # Creamos los agentes de cada tipo
        self.trabajadores = Trabajador.create_agents(self, cantTrabajadores)
        
        self.empresarios = Empresario.create_agents(self, cantEmpresarios)
        
        self.antisistemas = Antisistema.create_agents(self, cantAntisistemas)        

        self.colocarAgentes()

        print(f"Agentes correctamente instanciados. Se han creado {len(self.agents)} agentes, siendo {len(self.trabajadores)} trabajadores, {len(self.empresarios)} empresarios y {len(self.antisistemas)} antisistema.")   


        #Inicializamos el data collector para que recoja los datos durante la ejecución
        #Datos recogidos del modelo
        model_reporters={
            # Gráficos generales
            "Felicidad Media": lambda m: mediaSegura(m.agents, "felicidad"),
            "Energia Media": lambda m: mediaSegura(m.agents, "energia"),
            "Dinero Medio": lambda m: mediaSegura(m.agents, "dinero"),

            # Específicos de Trabajadores con chequeo de existencia
            "Felicidad Media Trabajadores": lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Trabajador"), "felicidad"),
            "Energia Media Trabajadores": lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Trabajador"), "energia"),
            "Dinero Medio Trabajadores": lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Trabajador"), "dinero"),

            # Específicos de Empresarios
            "Felicidad Media Empresarios": lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Empresario"), "felicidad"),
            "Energia Media Empresarios": lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Empresario"), "energia"),
            "Dinero Medio Empresarios": lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Empresario"), "dinero"),

            # Específicos de Antisistemas
            "Felicidad Media Antisistema": lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Antisistema"), "felicidad"),
            "Energia Media Antisistema": lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Antisistema"), "energia"),
            "Dinero Medio Antisistema": lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Antisistema"), "dinero")
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
        horasDia = 24.0
        horasSemana = horasDia * 7

        #Paso de tiempo de 1 semana
        self.schedule_recurring(
            self.cambioSemana,
            Schedule(interval=horasSemana, start=1)
        )
        
        #Paso del tiempo de 1 día
        self.schedule_recurring(
            self.cambioDia,
            Schedule(interval=horasDia, start=1)
        )

        self.epsilon = self.scenario.epsilonSimulacion       #Inicializamos el valor del epsilon inicial


    def colocarAgentes(self):
        '''Asigna una celda vacía o aleatoria del grid a cada agente vivo.'''
        for agente in self.agents:                
            agente.cell = self.grid.all_cells.select_random_cell()

    #####Prime
    def decaimientoEpsilon(self):
        '''Método que sirve para reducir el epsilon después de acabar cada episodio de entrenamiento'''
        self.epsilon -= self.scenario.reduccionEpsilonEpisodio

        if self.epsilon < self.scenario.epsilonMinimo:
            self.epsilon = self.scenario.epsilonMinimo


    #####Prime
    def reiniciarModeloEntrenamiento(self, finalEntrenamiento=False):
        '''
        Método para reiniciar durante el entrenamiento. En caso de ser el final del entrenamiento, vuelve a activar el datacollector y fusiona las tablas Q en una sola (por tipo)
        '''
        self.running = True
        self.steps = 0

        if finalEntrenamiento:
            self.modoEntrenamiento = False

            # Agrupación final del conocimiento por tipo
            self.tablasQPorTipo = self.consolidarTablasPorTipo()

        # Reinicio de valores del agente
        for agente in list(self.agents):
            
            # El agente restaura sus recursos al estado por defecto
            agente.reiniciar(self.epsilon)      #Le asignamos el nuevo epsilon (por el decay)
            
            # Si es el fin del entrenamiento, le asginamos la tabla Q compartida
            if finalEntrenamiento and agente.tipo in self.tablasQPorTipo:
                agente.tablaQ = self.tablasQPorTipo[agente.tipo]

        # Reposicionar a la población de forma aleatoria en el mapa
        self.colocarAgentes()
        
        if (finalEntrenamiento) and (self.datacollector is not None):
            self.datacollector.collect(self)


    #####Prime
    def entrenamientoAgentes(self):
        '''Ejecuta un entrenamiento completo sin gráficos'''
        
        self.modoEntrenamiento = True

        self.epsilon = self.scenario.epsilonQ       #Reiniciamos el valor del epsilon
        
        #Desactivamos el data collector durante el entrenamiento para mejorar la velocidad
        datacollectorAux = self.datacollector
        self.datacollector = None 


        for episodio in range(self.episodiosEntrenamiento):
            self.running = True
            self.steps = 0

            if ((episodio + 1) % 5) == 0:
                print(f"    Ejecutando episodio {episodio + 1}/{self.episodiosEntrenamiento}...")

            while (self.running) and (self.steps < self.scenario.maxStepsEpisodio):
                self.step()

            if not self.running:
                print(f"        Episodio {episodio + 1} FINALIZADO PREMATURAMENTE en el step {self.steps} por colapso social.")

            # Reinicio intermedio del modelo
            if episodio < self.episodiosEntrenamiento - 1:
                self.decaimientoEpsilon()
                self.reiniciarModeloEntrenamiento(finalEntrenamiento=False)

        # Restauramos el recolector de datos antes del reinicio final
        self.datacollector = datacollectorAux
        
        # Reinicio final en el que se preparan los agentes con los datos de la ejecución
        self.reiniciarModeloEntrenamiento(finalEntrenamiento=True)


    #####Prime
    def consolidarTablasPorTipo(self):
        '''
        Agrupa las tablas Q de todos los agentes según su tipo, calculando la media de los valores Q para cada estado y acción detectados.
        El formato de las tablas que se devuelven son: { tipoAgente: { estado: [valoresQMedios] } }
        '''
        # Estructura temporal para recopilar todos los valores Q de cada estado para cada tipo { tipo: { estado: [ [val_agente1], [val_agente2] ] } }
        recopilador = {"Trabajador": {}, "Empresario": {}, "Antisistema": {}}
        qTablasPorTipoMedias = {}

        #Recorremos cada agente y agrupamos los valores de sus qTablas por tipo de agente y estado
        for agente in self.agents:

            tipo = agente.tipo
            if tipo not in recopilador:      #Controlamos posibles errores
                continue
                
            for estado, valores in agente.tablaQ.items():

                #Si este estado no ha sido aún encontrado para este tipo de agentes, lo añadimos
                if estado not in recopilador[tipo]:
                    recopilador[tipo][estado] = []

                #Añadimos los qValores de este agente desde este estado
                recopilador[tipo][estado].append(valores)


        #Calculamos la media para cada estado-acción
        for tipo, estadosRecopilador in recopilador.items():                        #Recorremos todos los estados de cada tipo de agente
            qTablasPorTipoMedias[tipo] = {}

            #Para cada estado, recorremos su lista que contiene todas las Q de cada agente de ese tipo
            for estado, listaQValores in estadosRecopilador.items():
                
                matrizQValores = np.array(listaQValores)

                #Hacemos la media de cada acción
                mediaPorAccion = np.mean(matrizQValores, axis=0)
                qTablasPorTipoMedias[tipo][estado] = mediaPorAccion.tolist()

        return qTablasPorTipoMedias

    #####Prime
    def exportarDatosSimulacion(self):
        '''Método para guardar los datos recopilados por el DataCollector durante la simulación actual'''

        #Creamos la carpeta si aún no existe
        if not os.path.exists("../resultados"):
            os.makedirs("../resultados")
        
        #Guardamos la fecha en la que se ha realizado la petición de exportar los datos. Se usará para el nombre del archivo
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        
        #Nos aseguramos de que se ha accedido en el contexto correcto a este método
        if self.datacollector:

            #Exportamos los datos del modelo
            model_df = self.datacollector.get_model_vars_dataframe()
            model_df.to_csv(f"../resultados/simulacion{timestamp}_modelo.csv", index_label="Step")

            #Exportamos los datos de los agentes
            agent_df = self.datacollector.get_agent_vars_dataframe()
            agent_df.to_csv(f"../resultados/simulacion{timestamp}_agentes.csv")

            print(f"\nDatos de la simulación exportados correctamente: simulacion_{timestamp}_modelo.csv y simulacion_{timestamp}_agentes.csv")
        else:
            print("ERROR: No se han podido exportar los datos porque el DataCollector no está activo.")

    #####Prime
    def exportarPesosAgentes(self):
        '''Método para serializar y guardar las matrices Q de los agentes en formato JSON usando la tabla unificada'''

        # Si no existe el directorio de resultados, lo creamos
        if not os.path.exists("../resultados"):
            os.makedirs("../resultados")

        # Guardamos la fecha en la que se ha realizado la petición de exportar los datos
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        pathArchivo = f"../resultados/tablasQPorTipo_{timestamp}.json"

        qValoresPorTipo = {}

        # Iteramos sobre nuestra tabla de valores Q por tipo que ya tenemos. Iteramos para cada tipo de agente
        for tipoAgente, tablaQEstado in self.tablasQPorTipo.items():

            # Convertimos cada tupla de estado-acciones en un string para que JSON lo acepte
            tablaSerializable = {
                f"{estado[0]},{estado[1]},{estado[2]}": valores
                for estado, valores in tablaQEstado.items()
            }

            # Asignamos la tabla convertida al tipo de agente correspondiente
            qValoresPorTipo[tipoAgente] = tablaSerializable

        # Guardamos todo en el archivo .json estructurado
        with open(pathArchivo, "w") as f:
            json.dump(qValoresPorTipo, f, indent=4)

        return pathArchivo


    def importarDatos(self, nombreArchivo):
        '''
        Lee un archivo JSON con las tablas consolidadas por tipo, actualiza la 
        estructura centralizada del modelo e inyecta las Q-Tables a todos los agentes.
        '''
        #nombreArchivo = "tablasQPorTipo_2026-05-21_171242.json"
        ruta = f"../resultados/{nombreArchivo}"
        if not os.path.exists(ruta):
            print(f"Error: El archivo {nombreArchivo} no existe en la carpeta de resultados.")
            return False

        with open(ruta, "r") as f:
            pesos_json = json.load(f)

        # Reconstruimos el JSON: de claves String "2,3,3" pasamos a Tuplas (2, 3, 3)
        tablas_reconstruidas = {}
        for tipo, tabla_cruda in pesos_json.items():
            tabla_reconstruida = {}
            for estado_str, valores in tabla_cruda.items():
                # Volvemos a transformar el texto "2,3,3" en la tupla original (2, 3, 3)
                estado_tupla = tuple(map(int, estado_str.split(",")))
                tabla_reconstruida[estado_tupla] = valores
            tablas_reconstruidas[tipo] = tabla_reconstruida

        # Guardamos los datos cargados en la variable centralizada del modelo
        self.tablasQPorTipo = tablas_reconstruidas

        # Inyectamos las tablas correspondientes a todos los agentes vivos según su tipo
        for agente in self.agents:
            if agente.tipo in self.tablasQPorTipo:
                # Apuntamos la tablaQ del agente directamente al diccionario centralizado en memoria
                agente.tablaQ = self.tablasQPorTipo[agente.tipo]

        self.modoEntrenamiento = False  # Apagamos el modo entrenamiento al cargar conocimiento experto
        
        return nombreArchivo


    def comprobarAgentesMuertos(self):
        '''Método que analiza todos los agentes y, en caso de que ya no queden agentes vivos, acaba la simulación'''

        agentesMuertos = []

        #Recorremos cada agente y, si está muerto, lo guardamos
        for agente in self.agents:

            if agente.estado == self.scenario.estadoMuerto:
                agentesMuertos.append(agente)


        #Al terminar, comprobamos si la cantidad de agentes muertos es la misma que la cantidad de agentes totales
        if len(self.agents) == len(agentesMuertos):
            self.running = False
        

    
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
            if self.datacollector is not None:
                self.datacollector.collect(self)

            #Miramos si durante el paso anterior ha muerto algún agente, en cuyo caso lo eliminamos del modelo. Si no quedan agentes, acabamos la ejecución
            self.comprobarAgentesMuertos()
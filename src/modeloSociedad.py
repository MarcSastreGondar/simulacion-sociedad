'''
Documento con la lógica principal de la simulación. Se encarga de inicializar los elementos principales del Modelo, como 
son los agentes, el DataCollector y los eventos temporales, e incluye todos los parámetros configurables en el EscenarioSociedad.
También implementa el entrenamiento con Q-Learning y la importación y exportación de los datos generados.
'''
import os
from datetime import datetime

import json
import csv


import mesa
from mesa.experimental.scenarios import Scenario
from mesa.time import Schedule



import numpy as np  #Para el data collector

#Imports de los agentes
from agentes.trabajador import Trabajador
from agentes.empresario import Empresario
from agentes.antisistema import Antisistema

from metricas import mediaSegura


class EscenarioSociedad(Scenario):
    '''Escenario que contiene todos los parámetros de la ejecución. El valor de los parámetros de los recursos (como la energia, felicidad, etc.) 
    debe ser positivo para que se aumente o negativo si se quiere disminuir (excepto el tiempo, que debe ser siempre positivo)'''
    
    #Tamaño del tablero en el que pueden estar los agentes (se adapta automáticamente en caso de ser demasiado pequeño)
    anchuraGrid: int = 15
    alturaGrid: int = 15

    #Generador de números pseudoaleatorios para poder repetir resultados en las ejecuciones
    rng: int = 42

    #Parámetros de configuración de los agentes en general
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
    cantEmpresarios: int = 5                #Cantidad de empresarios
    cantAntisistemas: int = 5               #Cantidad de agentes antisistema

    porcentajeAleatorio: float = 0.25

    umbralDepresion: float = 15.0        #A partir de qué punto de felicidad empezamos a considerar que el agente tiene depresión
    mesesSuicidio: int = 6               #Cantidad de meses con depresión acumulados que llevan al agente a ser borrado


    visionAgente: int = 3           #Distancia a la que los agentes pueden ver, en todas direcciones
    movimientoAgente: int = 2       #Distancia a la que se pueden, como máximo, mover los agentes, en todas direcciones

    umbralCansancio: int = 30               #A partir de menos de qué cantidad de energía se considera al agente como cansado
    perdidaFelicidadCansancio: int = -1     #Cantidad de felicidad que pierde el agente en caso de realizar una acción que no le guste cansado

    #Relacionados con el Entrenamiento de los agentes y el Q-Learning
    episodiosEntrenamiento: int = 25        #Cantidad de simulaciones enteras que deben realizarse para entrenar a los agentes
    maxStepsEpisodio: int = 50              #Cantidad máxima de steps que puede haber en 1 sólo ciclo de entrenamiento
    
    alfaQ: float = 0.1
    gammaQ: float = 0.9
    epsilonQ: float = 1.0
    reduccionEpsilonEpisodio: float = 0.05      #Cantidad que se reduce el Epsilon en cada ciclo completo de entrenamiento
    epsilonMinimo: float = 0.02                 #Siempre un 2% de probabilidades de realizar una acción aleatoria
    epsilonSimulacion: float = 0.005            #Probabilidad de explorar en una simulación real. 0,5%
    disminucionRecompensaFallo: float = -1      #Cantidad en la que se reduce el Q valor en caso de que el agente intente realizar la acción pero no acabe pudiendo

    porcentajeDineroRecompensa: float = 0.05    #Qué porcentaje del dinero perdido se resta a la recompensa obtenida

    recompensaMuerte: float = -100.0

    porcentajePocaEnergiaQ: float = 0.33        #Poca energía si energiaAgente < energiaMax * porcentajePocaEnergiaQ
    porcentajeMediaEnergiaQ: float = 0.66       #Media energía si energiaAgente < energiaMax * porcentajeMediaEnergiaQ

    divisionPocoDinero: int = 5                 #Dinero bajo si dineroAgente < sueldoMedio / divisionPocoDinero
    multiplicacionMedioDinero: int = 2          #Dinero alto si dineroAgente > sueldoMedio * multiplicacionMedioDinero


    #Parámetros de configuración de agentes específicos
    #Trabajador
    dineroInicialT: int = 1000
    felicidadInicialT: float = 85
    sueldoMinimo: int = 600
    sueldoMedio: int = 1200                 #Dinero de 1 sueldo completo al mes.
    diasLaborablesSemanales: int = 5        #Cantidad de días que trabajarán cada semana (no podrán trabajar ni más ni menos)
    diasLaborablesAlMes: int = 22           #Suponemos que trabajan, de media, 22 días al mes

    #Empresario
    dineroInicialE: int = 5000
    felicidadInicialE: float = 90

    #Antisistema
    dineroInicialA: int = 200
    felicidadInicialA: float = 60
    odioMaximo: int = 100


    #Cambios en los recursos de los agentes según el paso del tiempo
    reduccionDiariaFelicidad: int = -2          #Cada día se reduce en 2 la felicidad del agente

    porcentajeGastosCuotidianos: float = 0.01   #Gastan un 1% de su dinero en gastos cuotidianos, con un máximo y mínimo
    gastosDiariosMin: int = -10           
    gastosDiariosMax: int = -30

    reduccionPasivaOdio: int = -5               #Odio que pierden los antisistema cada semana


    #Parámetros de configuración necesarios de las acciones que pueden realizar los agentes
    #Acciones comunes para todos los agentes
    #Dormir
    horasMinimasDormir: float = 4.0
    horasMaximasDormir: float = 8.0
    felicidadDormirMal: float = -2
    felicidadDormirBien: float = 3
    maxDormirPorDia: int = 1                #Cantidad de veces que puede dormir un agente cada día
    
    #Entrenar
    energiaEntrenar: int = -10
    tiempoEntrenar: float = 1.5             #1.5 horas
    cuotaGimnasio: int = -50
    felicidadEntrenar: int = 1
    aumentoEnergiaMaxEntrenar: int = 2

    #Compra lujosa
    costeLujo: int = -300
    felicidadLujo: float = 6
    tiempoLujo: int = 1

    #Ocio
    energiaOcio: int = -3
    tiempoOcio: float = 3                   #3 horas
    costeOcio: int = -25
    felicidadOcio: float = 6

    #Comida basura
    energiaComidaBasura: int = -2
    felicidadComidaBasura: float = 2
    porcentajeAhorro: float = 0.2                 #Porcentaje de los gastos cuotidianos que se ahorran al comer comida basura
    reduccionEnergiaMaxComidaBasura: int = -1
    maxComidasPorDia: int = 2                   #Cantidad máxima de comidas que puede reemplazar cada día un agente por comida basura


    #Parámetros de las acciones de los trabajadores:
    #Trabajar
    tiempoTrabajo: float = 8.0          #Horas que dedica a trabajar de manera directa
    maxTiempoAlTrabajo: float = 1.5     #Cantidad máxima de tiempo en horas que puede tardar el agente en transportarse al trabajo (ida + vuelta)
    energiaTrabajar: int = -10

    felicidadTrabajar: float = -5
    felicidadMaxTrabajar: float = 0     #Cantidad máxima de felicidad que puede aportarle trabajar

    #TrabajoDoble, simplemente el doble de trabajar
    reduccionEnergiaMaxDobleTrabajo: int = -2           #Pierde energía máxima por el desgaste físico

    #Teletrabajar
    porcentajeSueldoTeletrabajo: float = 0.8            #Porcentaje del sueldo normal que se cobra en el trabajo (si es < 1, se cobra menos teletrabajando)
    porcentajeEnergiaTeletrabajo: float = 0.6           #Porcentaje de la energia gastada en el trabajo (si es < 1, se usa menos teletrabajando)

    #Estudiar, para mejorar las condiciones laborales
    energiaEstudiar: int = -30
    felicidadEstudiar: float = -5
    costeEstudiar: int = -200
    aumentoSueldoEstudiar: int = 100                    #Incrementa el sueldo mensual (no el diario)
    aumentoFelicidadTrabajoEstudiar: float = 1          #Incrementa la felicidad que recibe el agente por trabajar
    tiempoEstudiar: float = (24 * 5)                    #5 días

    #Contagiar Felicidad pasivamente
    umbralContagiarFelicidadT: float = 90.0             #A partir de qué punto contagia la felicidad a sus vecinos
    felicidadContagiarT: float = 0.5                    #Cantidad de felicidad que aporta a sus vecinos


    #Parámetros de las acciones de los empresarios:
    #Invertir
    tiempoInvertir: float = 2                  #2 horas
    energiaInvertir: int = -5
    felicidadInvertir: float = 0.5             #Sumamos poco a la felicidad ya que, aunque gana dinero, es un poco estresante
    porcentajeDineroInvertir: float = 0.01     #Aumenta su patrimonio en un 1%

    #Bonificación Monetaria
    umbralFelicidadBonificacionMonetaria: float = 50        #Dar recompensas monetarias sólo a los Trabajadores que tengan menos de una cierta cantidad de felicidad
    dineroPorTrabajadorBonificacion: int = 100              #Cantidad de dinero que pierde el Empresario por cada Trabajador (y la que gana cada Empresario)
    aumentoFelicidadTrabajadorBonificacion: float = 10      #Lo que aumenta la felicidad de cada Trabajador
    tiempoBonificacion: float = 1.0                         #1 hora


    #Generacion Pasiva de Dinero
    dineroPasivoPorTrabajador: int = 10

    #Contagiar Felicidad pasivamente
    umbralContagiarFelicidadE: float = 90.0         #A partir de qué punto contagia la felicidad a los Trabajadores cercanos
    felicidadContagiarE: float = 0.5                #Cantidad de felicidad que le da a los Trabajadores cercanos


    #Parámetros de las acciones de los antisistema:
    #Robar
    porcentajeDineroRobado: float = 0.1                 #Porcentaje del dinero que le es robado al agente y que recibe el Antisistema
    felicidadAtracado: float = -10                   
    tiempoAtracar: float = 1.5
    energiaAtracar: int = -5
    felicidadAtracar: float = 2
    odioAtracar: int = 20                               #Cantidad de odio que gana el antisistema

    #Quejarse
    felicidadQuejarse: float = -1                       #Felicidad que pierde el antisistema al quejarse
    felicidadQuejarseReceptor: float = -2               #Felicidad que pierden los oyentes al escuchar al antisistema quejarse
    energiaQuejarse: int = -3
    tiempoQuejarse: float = 1
    odioQuejarse: int = 2

    #Vandalismo
    felicidadVandalismo: float = 3
    energiaVandalismo: int = -3
    dineroVandalismo: int = -5                      #Dinero para gastar en material necesario para el vandalismo. Cuantos más Empresarios se vandalicen, mayor es el coste
    tiempoVandalismo: float = 1.5                   #1.5 horas por cada Empresario cercano
    odioVandalismo: int = 5                         #Cantidad de odio que recibe el Antisistema
    felicidadVandalismoEmpresario: float = -4
    dineroVandalismoEmpresario: int = -200          #Dinero que pierde el Empresario en reparaciones

    #Contagiar Odio pasivamente
    umbralContagiarOdio: float = 30.0               #A partir de menos de qué cantidad de felicidad el Antisistema contagiará su infelicidad
    felicidadContagiarA: float = -1                 #Cantidad de felicidad que le da a los trabajadores cercanos

    

class ModeloSociedad(mesa.Model):
    '''Modelo principal de la Simulación de la Sociedad'''
    
    def __init__(self, cantTrabajadores=10, cantEmpresarios=5, cantAntisistemas=5, episodiosEntrenamiento=10):
        
        #Instanciamos el escenario con los parámetros que se utilizarán para configurar la simulación
        escenario = EscenarioSociedad()        

        #Si los agentes no caben bien dentro de las casillas, aumentamos la cantidad de casillas
        totalAgentes = cantTrabajadores + cantEmpresarios + cantAntisistemas
        auxTotalAgentes = 2.5 * totalAgentes                                    #Mayor margen para que quepan mejor y puedan moverse

        while(auxTotalAgentes > (escenario.alturaGrid * escenario.anchuraGrid)):
            escenario.alturaGrid += 1
            escenario.anchuraGrid += 1

    
        super().__init__(scenario=escenario)

        self.modoEntrenamiento = False                  #Si es True, se entrena y se actualiza la matriz Q. Si es False, hace la simulación con lo que ya sabe

        self.episodiosEntrenamiento = episodiosEntrenamiento


        self.cantTrabajadores = cantTrabajadores
        self.cantEmpresarios = cantEmpresarios
        self.cantAntisistemas = cantAntisistemas

        #Creamos las casillas en las que pueden moverse los agentes
        self.grid = mesa.discrete_space.OrthogonalMooreGrid((self.scenario.anchuraGrid, self.scenario.alturaGrid), torus=True, random=self.random)  #torus = True para que los bordes del mapa están conectados entre sí
        
        #Creamos los agentes de cada tipo
        self.trabajadores = Trabajador.create_agents(self, cantTrabajadores)
        self.empresarios = Empresario.create_agents(self, cantEmpresarios)
        self.antisistemas = Antisistema.create_agents(self, cantAntisistemas)        

        #Los colocamos en una casilla aleatoria
        self.colocarAgentes()

        print(f"Agentes correctamente instanciados. Se han creado {len(self.agents)} agentes, siendo {len(self.trabajadores)} trabajadores, {len(self.empresarios)} empresarios y {len(self.antisistemas)} antisistema.")   


        #Inicializamos el data collector para que recoja los datos durante la ejecución
        #Datos recogidos del modelo
        model_reporters={
            #Gráficos generales
            "Felicidad Media" : lambda m: mediaSegura(m.agents, "felicidad"),
            "Energia Media"   : lambda m: mediaSegura(m.agents, "energia"),
            "Dinero Medio"    : lambda m: mediaSegura(m.agents, "dinero"),

            #Específicos de Trabajadores
            "Felicidad Media Trabajadores": lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Trabajador"), "felicidad"),
            "Energia Media Trabajadores"  : lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Trabajador"), "energia"),
            "Dinero Medio Trabajadores"   : lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Trabajador"), "dinero"),

            #Específicos de Empresarios
            "Felicidad Media Empresarios": lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Empresario"), "felicidad"),
            "Energia Media Empresarios"  : lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Empresario"), "energia"),
            "Dinero Medio Empresarios"   : lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Empresario"), "dinero"),

            #Específicos de Antisistemas
            "Felicidad Media Antisistema": lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Antisistema"), "felicidad"),
            "Energia Media Antisistema"  : lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Antisistema"), "energia"),
            "Dinero Medio Antisistema"   : lambda m: mediaSegura(m.agents.select(lambda a: a.tipo == "Antisistema"), "dinero")
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
        self.tablasQPorTipo = {}
        self.historialRecompensas = {}
        self.historialFallos = {}


    def colocarAgentes(self):
        '''Asigna una celda vacía o aleatoria del grid a cada agente vivo'''
        for agente in self.agents:                
            agente.cell = self.grid.all_cells.select_random_cell()

    
    def decaimientoEpsilon(self):
        '''Método que sirve para reducir el epsilon después de acabar cada episodio de entrenamiento, para fomentar una exploración inicial e ir explotando más con el tiempo'''
        self.epsilon -= self.scenario.reduccionEpsilonEpisodio

        if self.epsilon < self.scenario.epsilonMinimo:
            self.epsilon = self.scenario.epsilonMinimo

    

    def inicializarHistorialEntrenamiento(self):
        '''Método para inicializar los historiales que contendrán el rendimiento obtenido durante el entrenamiento'''
        
        historialRecompensas = {             #Media de recompensa obtenida en cada episodio
            "Trabajador": [],
            "Empresario": [],
            "Antisistema": [],
            "Total": []
            }
        
        historialFallos = {                 #Media de fallos realizados en cada episodio
            "Trabajador": [],
            "Empresario": [],
            "Antisistema": [],
            "Total": []
            }

        #Antes de empezar el entrenamiento, iniciamos el valor de los historiales            
        for tipoAgente in historialRecompensas:

            #Para cada episodio, inicializamos todos los historiales a 0
            for _ in range(self.episodiosEntrenamiento):
                historialRecompensas[tipoAgente].append(0.0)
                historialFallos[tipoAgente].append(0)               #Si el tipo está en el historial de recompensas, asumimos que también estará en el de fallos
        
        #Devolvemos ambos historiales inicializados
        return historialRecompensas, historialFallos

    
    def sumarEpisodioHistoriales(self, episodio):
        '''Método para añadir los datos obtenidos durante 1 episodio de entrenamiento a los historiales que indican el rendimiento del entrenamiento'''
        
        #Definimos los acumuladores para el episodio actual
        recompensasAcumuladas = {"Trabajador": 0.0, "Empresario": 0.0, "Antisistema": 0.0, "Total": 0.0}
        fallosAcumulados = {"Trabajador": 0.0, "Empresario": 0.0, "Antisistema": 0.0, "Total": 0.0}

        #Recorremos cada agente y sumamos su recompensa y fallos al contador de su tipo de agente y al total
        for agente in self.agents:

            if agente.tipo in recompensasAcumuladas:
                recompensasAcumuladas[agente.tipo] += agente.recompensaAcumulada
                fallosAcumulados[agente.tipo] += agente.fallosAcumulados

            recompensasAcumuladas["Total"] += agente.recompensaAcumulada
            fallosAcumulados["Total"] += agente.fallosAcumulados


        #Obtenemos la cantidad de cada tipo de agente
        cantidades = {
            "Trabajador": self.cantTrabajadores,
            "Empresario": self.cantEmpresarios,
            "Antisistema": self.cantAntisistemas,
            "Total": len(self.agents)
        }

        #Calculamos las medias y las añadimos al historial
        for tipo in recompensasAcumuladas:
            cant = cantidades[tipo]

            #Si hay agentes de esa clase, guardamos la media, si no, se queda en 0.0
            self.historialRecompensas[tipo][episodio] = (recompensasAcumuladas[tipo] / cant) if cant > 0 else 0.0

            #Lo mismo para los fallos realizados
            self.historialFallos[tipo][episodio] = (fallosAcumulados[tipo] / cant) if cant > 0 else 0.0



    def reiniciarModeloEntrenamiento(self, finalEntrenamiento=False):
        '''
        Método para reiniciar durante el entrenamiento. En caso de ser el final del entrenamiento, vuelve a activar el datacollector y fusiona las tablas Q en una sola (por tipo)
        '''
        self.running = True
        self.steps = 0

        if finalEntrenamiento:
            self.modoEntrenamiento = False

            #Agrupación final del conocimiento por tipo
            self.tablasQPorTipo = self.consolidarTablasPorTipo()

        #Reinicio de valores del agente
        for agente in list(self.agents):
            
            #El agente restaura sus recursos al estado por defecto
            agente.reiniciarAgente(self.epsilon)      #Le asignamos el nuevo epsilon (por el decay)
            
            #Si es el fin del entrenamiento, le asginamos la tabla Q compartida
            if finalEntrenamiento and agente.tipo in self.tablasQPorTipo:
                agente.tablaQ = self.tablasQPorTipo[agente.tipo]

        #Reposicionar a la población de forma aleatoria en el mapa
        self.colocarAgentes()
        
        if (finalEntrenamiento) and (self.datacollector is not None):
            self.datacollector.collect(self)



    def imprimirResultadoEntrenamiento(self, historialRecompensas, historialFallos):
        '''Método para enseñar por terminal un resumen del resultado del entrenamiento'''
        
        print("El resumen de los resultados obtenidos durante el entrenamiento son:")
        
        #Recorremos cada tipo de agente
        for tipoAgente in historialRecompensas:

            #Para cada tipo de agente, comparamos su rendimiento entre el principio y el final
            if tipoAgente != "Total":
                print("\tLos agentes", tipoAgente,":")
                
                print("\t\tHan empezado obteniendo una Recompensa Total Media de", historialRecompensas[tipoAgente][0], "y han acabado con una Recompensa Total Media de", historialRecompensas[tipoAgente][len(historialRecompensas[tipoAgente]) - 1])
                print("\t\tHan empezado cometiendo una cantidad Media de", historialFallos[tipoAgente][0], "fallos, y han acabado cometiendo una Media de", historialFallos[tipoAgente][len(historialRecompensas[tipoAgente]) - 1], "fallos")
            

            #Comparamos el rendimiento total entre el principio y el final
            else:
                print("\tEntre todos los agentes:")

                print("\t\tHan empezado obteniendo una Recompensa Total Media de", historialRecompensas[tipoAgente][0], "y han acabado con una Recompensa Total Media de", historialRecompensas[tipoAgente][len(historialRecompensas[tipoAgente]) - 1])
                print("\t\tHan empezado cometiendo una cantidad Media de", historialFallos[tipoAgente][0], "fallos, y han acabado cometiendo una Media de", historialFallos[tipoAgente][len(historialRecompensas[tipoAgente]) - 1], "fallos")



    def entrenamientoAgentes(self):
        '''Ejecuta un entrenamiento completo sobre los agentes y les asigna la media de las tablas Q aprendidas durante este (por tipo). 
           No se guardan los datos en el datacollector durante el proceso para mejorar la eficiencia'''
    
        self.modoEntrenamiento = True

        self.epsilon = self.scenario.epsilonQ       #Inicializamos el valor del epsilon
        
        #Desactivamos el data collector durante el entrenamiento para mejorar la velocidad
        datacollectorAux = self.datacollector
        self.datacollector = None 

        #Creamos un historial para guardar las métricas de rendimiento del entrenamiento y lo inicializamos
        self.historialRecompensas, self.historialFallos = self.inicializarHistorialEntrenamiento()


        #Ahora ya podemos empezar con el entrenamiento
        for episodio in range(self.episodiosEntrenamiento):

            #Reiniciamos algunos parámetros necesarios para el entrenamiento
            self.running = True
            self.steps = 0

            #Cada 10 steps indicamos el progreso del entrenamiento en la terminal
            if (((episodio + 1) % 10) == 0) or ((episodio + 1) == self.episodiosEntrenamiento):
                print(f"    Ejecutando episodio {episodio + 1}/{self.episodiosEntrenamiento}...")

            #Hacemos una simulación de la sociedad completa, haciendo steps hasta llegar al máximo por episodio o hasta llegar al colapso social
            while (self.running) and (self.steps < self.scenario.maxStepsEpisodio):
                self.step()

            #Si el episodio ha acabado prematuramente por la muerte de todos los agentes, lo comunicamos
            if not self.running:
                print(f"        Episodio {episodio + 1} FINALIZADO PREMATURAMENTE en el step {self.steps} por colapso social.")


            #Al acabar el episodio, sumamos la recompesa acumulada y los fallos acumulados de cada uno de los agentes
            self.sumarEpisodioHistoriales(episodio)


            #Reinicio intermedio del modelo
            if episodio < self.episodiosEntrenamiento - 1:
                self.decaimientoEpsilon()                                       #Reducimos el epsilon
                self.reiniciarModeloEntrenamiento(finalEntrenamiento=False)     #Reiniciamos las variables de los agentes


        #Al acabar, imprimimos el resultado del entrenamiento
        self.imprimirResultadoEntrenamiento(self.historialRecompensas, self.historialFallos)

        #Restauramos el datacollector antes del reinicio final
        self.datacollector = datacollectorAux
        
        #Reinicio final en el que se preparan los agentes para seguir la simulación. Se les carga la media de las tablas Q obtenidas
        self.reiniciarModeloEntrenamiento(finalEntrenamiento=True)


    
    def consolidarTablasPorTipo(self):
        '''Agrupa las tablas Q de todos los agentes según su tipo, calculando la media de los valores Q para cada estado y acción detectados.
           El formato de las tablas que se devuelven son: { tipoAgente: { estado: [valoresQMedios] } }'''

        #Acumulador para todos los valores Q de cada estado para cada tipo de agente
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

    
    def exportarDatosSimulacion(self):
        '''Método para guardar en un archivo los datos recopilados por el DataCollector durante la simulación actual, desde el último reinicio'''

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

    
    def exportarPesosAgentes(self):
        '''Método para serializar y guardar en un archivo las matrices Q de los agentes en formato JSON'''

        #Si no existe el directorio de resultados, lo creamos
        if not os.path.exists("../resultados"):
            os.makedirs("../resultados")

        #Guardamos la fecha en la que se ha realizado la petición de exportar los datos
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        pathArchivo = f"../resultados/tablasQPorTipo_{timestamp}.json"

        qValoresPorTipo = {}

        #Iteramos sobre nuestra tabla de valores Q por tipo de agente que ya tenemos
        for tipoAgente, tablaQEstado in self.tablasQPorTipo.items():

            #Convertimos cada tupla de estado-acciones en un string para que JSON lo acepte
            tablaSerializable = {
                f"{estado[0]},{estado[1]},{estado[2]}": valores
                for estado, valores in tablaQEstado.items()
            }

            #Asignamos la tabla convertida al tipo de agente correspondiente
            qValoresPorTipo[tipoAgente] = tablaSerializable

        #Guardamos todo en un único archivo .json
        with open(pathArchivo, "w") as f:
            json.dump(qValoresPorTipo, f, indent=4)

        return pathArchivo
    

    def exportarDatosEntrenamiento(self):
        '''Exporta las métricas de rendimiento (recompensas medias y fallos) acumuladas durante el entrenamiento a dos archivos .csv independientes para su posterior análisis'''

        #Si no existe el directorio de resultados, lo creamos
        if not os.path.exists("../resultados"):
            os.makedirs("../resultados")


        #Guardamos la fecha en la que se ha realizado la petición de exportar los datos
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        path_recompensas = f"../resultados/entrenamiento{timestamp}_recompensas.csv"
        path_fallos = f"../resultados/entrenamiento{timestamp}_fallos.csv"


        #Definimos las columnas del CSV
        columnas = ["Episodio", "Trabajador", "Empresario", "Antisistema", "Total"]

        #Controlamos el caso de que no se haya realizado ningún entrenamiento
        datosCorrectos = True
        if (self.historialRecompensas == {}) or (self.historialFallos == {}):
            self.historialRecompensas, self.historialFallos = self.inicializarHistorialEntrenamiento()
            datosCorrectos = False

        #Exportamos el historial de recompensas
        with open(path_recompensas, mode="w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            escritor.writerow(columnas)     #Añadimos la cabecera

            #Iteramos por cada episodio
            for ep in range(self.episodiosEntrenamiento):
                fila = [
                    ep + 1,                                         #Número del episodio
                    self.historialRecompensas["Trabajador"][ep],    #Recompensa del Trabajador en este episodio
                    self.historialRecompensas["Empresario"][ep],
                    self.historialRecompensas["Antisistema"][ep],
                    self.historialRecompensas["Total"][ep]
                ]
                escritor.writerow(fila)

                #En caso de que los datos no sean correctos, sólo añadimos la primera fila
                if not datosCorrectos:
                    break
            

        #Exportamos el historial de fallos realizados
        with open(path_fallos, mode="w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            escritor.writerow(columnas)     #Añadimos la cabecera

            for ep in range(self.episodiosEntrenamiento):

                #Usamos la misma lógica
                fila = [
                    ep + 1,
                    self.historialFallos["Trabajador"][ep],
                    self.historialFallos["Empresario"][ep],
                    self.historialFallos["Antisistema"][ep],
                    self.historialFallos["Total"][ep]
                ]
                escritor.writerow(fila)

                #En caso de que los datos no sean correctos, sólo añadimos la primera fila
                if not datosCorrectos:
                    break
        
        #Si los datos eran incorrectos, volvemos a vaciarlos
        if not datosCorrectos:
            self.historialRecompensas = {}
            self.historialFallos = {}

        print(f" Los datos del entrenamiento han sido exportados con éxito en {path_recompensas} y {path_fallos}")


    def importarPesosAgentes(self, nombreArchivo):
        '''Lee un archivo JSON con las tablas Q de cada tipo de usuario y se las asigna a los agentes. 
           Diseñado para recibir la salida del método exportarPesosAgentes'''
 
        #Abrimos el archivo pasado por parámetro
        ruta = f"../resultados/{nombreArchivo}"

        if not os.path.exists(ruta):
            print(f"Error: El archivo {nombreArchivo} no existe en la carpeta de resultados.")
            return False

        #Lo abrimos en modo lectura y cargamos el contenido
        with open(ruta, "r") as f:
            pesosJson = json.load(f)

        #Reconstruimos los pesos del archivo
        tablasReconstruidas = {}

        #Recorremos cada tabla
        for tipo, tablaSinTratar in pesosJson.items():

            tablaReconstruida = {}
            
            #Para cada tabla, recorremos cada uno de sus estados
            for estadoString, valores in tablaSinTratar.items():

                #Transformamos las claves de String "2,3,3" a Tuplas (2, 3, 3)
                estadoTupla = tuple(map(int, estadoString.split(",")))
                tablaReconstruida[estadoTupla] = valores

            tablasReconstruidas[tipo] = tablaReconstruida

        #Guardamos los datos cargados
        self.tablasQPorTipo = tablasReconstruidas

        #Sobreescribimos las tablas actuales de cada agente por las que acabamos de cargar
        for agente in self.agents:
            if agente.tipo in self.tablasQPorTipo:
                agente.tablaQ = self.tablasQPorTipo[agente.tipo]        #Sustituimos su tabla de Q Valores
  
        return nombreArchivo



    def comprobarAgentesMuertos(self):
        '''Método que analiza todos los agentes y, en caso de que ya no quede ninguno vivo, acaba la simulación'''

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
            #Llamamos al método que se encarga de las modificaciones diarias comunes para todos los agentes
            self.agents.shuffle_do("avanceDiarioGeneral")

            #Llamamos al método que se encarga de las modificaciones diarias específicas para cada tipo de agente
            self.agents.shuffle_do("avanceDiarioEspecifico")

    def cambioSemana(self):
        '''Método que determina si han pasado 7 días (168 steps) para empezar una nueva semana. Empieza los eventos semanales propios de los agentes'''
        
        if self.running:
            #Llamamos al método que se encarga de las modificaciones semanales específicas para cada tipo de agente
            self.agents.shuffle_do("avanceSemanalEspecifico")


    def step(self):        
        '''Paso de tiempo de 1 hora para toda la simulación'''

        #Aseguramos de que el modelo siga activo
        if self.running:
            
            #Ejecutamos el step() de todos los agentes en orden aleatorio.
            self.agents.shuffle_do("step")

            #Recojemos los datos de todo el modelo una vez hayan actuado los agentes
            if self.datacollector is not None:
                self.datacollector.collect(self)

            #Comprobamos si no quedan agentes, en cuyo caso terminamos la ejecución
            self.comprobarAgentesMuertos()
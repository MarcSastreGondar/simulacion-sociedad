#¿?¿$"acs"   Documento con el código común entre los distintos agentes para evitar la repetición de código
'''
gashfd
'''

#Importamos la clase con el agente por defecto de Mesa
import mesa
from mesa.discrete_space import Cell

from metricas import *

class AgenteBase(mesa.discrete_space.CellAgent):
    """Clase base que contiene atributos y métodos comunes a todos los agentes."""

    def __init__(self, modelo, dineroInicial, felicidadInicial):
        super().__init__(modelo)

        # Definimos los atributos comunes entre todos los agentes
        #Usamos el mismo RandomNumberGenerator que tiene el modelo
        self.aleat = modelo.rng
        
        self.tipo = "Ninguno"
        self.estado = "Feliz"        

        self.visionAgente = self.scenario.visionAgente
        self.visionMovimiento = self.scenario.movimientoAgente

        #Variables relacionadas con el tiempo del que dispone el agente para actuar cada día
        self.tiempoMaxPosible = self.scenario.tiempoMaxPosible - self.scenario.tiempoVital          #Tiempo en horas que el agente tiene disponibles en un dia
        self.tiempoDisponible = self.tiempoMaxPosible                                               #Tiempo que aún le queda disponible al agente para realizar acciones

        #Energia, la cual es necesaria para realizar acciones
        self.energia = self.scenario.energiaMax                       #Energia que tiene ahora mismo el agente
        self.energiaMax = self.scenario.energiaMax                    #Energia máxima que puede llegar a tener este agente totalmente descansado


        self.porcentajeAleatorio = self.scenario.porcentajeAleatorio

        #Cantidad de dinero que posee un agente en un cierto momento
        dineroAleat = self.porcentajeAleatorio * dineroInicial
        dineroAleat = int(self.aleat.uniform(-dineroAleat, dineroAleat))    #Introducimos aleatoriedad en la cantidad de dinero que tendrá cada agente inicialmente (+- un porcentaje)        
        self.dinero = int(dineroInicial) + dineroAleat


        #Grado de desagrado por la situación en la que se encuentra el agente. Entre 0 (mínimo) y 100 (máximo)
        felicidadAleat = self.porcentajeAleatorio * felicidadInicial
        felicidadAleat = int(self.aleat.uniform(-felicidadAleat, felicidadAleat))   #+- un porcentaje del que tiene inicialmente
        
        self.felicidad = 0.0                                                          #Inicializamos el valor de la felicidad para poder modificarlo en el método
        valFelicidad = int(felicidadInicial) + felicidadAleat
        self.modificarEnergiaFelicidadDinero(felicidad=valFelicidad)
        

        self.diasDepresion = 0                                          #Cantidad de días que lleva el agente en depresión
        self.diasSuicidio = self.scenario.mesesSuicidio * 31            #Cantidad de días con depresión acumulados que llevan al agente a ser borrado. Meses * Dias en un mes

        #Parámetros relacionados con las acciones
        self.ocupado = 0.0              #Contador que indica si el agente está realizando alguna acción que le obligue a esperar en los steps (si realiza acciones que tarden más de 1 step)
        self.gastosCuotidianos = 0
        self.tiempoMensualidadGym = 0   #Empieza sin estar suscrito al gimnasio                                       
            


    # Métodos comunes de los agentes
    # Métodos auxiliares
    def actualizarVecinos(self):
        '''Miramos las casillas cercanas al agente y detectamos cuales son sus vecinos. Debería llamarse al principio de cada step para evitar errores'''
        #Obtenemos los vecinos que tiene el agente alrededor (en su campo visual)
        self.vecindario = self.cell.get_neighborhood(radius=self.visionAgente)
        self.vecinos = self.vecindario.agents

        #Obtenemos las casillas a las que puede moverse el agente actualmente
        self.vecindarioMovimiento = self.cell.get_neighborhood(radius=self.visionMovimiento)
        self.casillasVacias = [c for c in self.vecindarioMovimiento if c.is_empty]


    def eliminarAgente(self):
        '''Método que elimina permanentemente de la simulación a un agente. Es equivalente a la muerte de una persona y 
           los agentes deben intentar evitarla a toda costa'''
        
        #Si es el último agente vivo, en vez de borrarlo, simplemente paramos la simulación
        if len(self.model.agents) == 1:
            print("Parando simulación: Todos los agentes han sido eliminados de la sociedad")
            self.model.running = False

        else:
            #Actualizamos su estado a muerto (se eliminará desde el modelo)
            self.estado = "Muerto"


    #Métodos auxiliares para modificar los recursos de los agentes de manera controlada
    def calcularGastosCuotidianos(self):
        '''Método que calcula los gastos cuotidianos del agente durante este día teniendo en cuenta la cantidad de dinero que posee acutalmente'''
        gastosCuotidianos = (-1) * self.dinero * self.scenario.porcentajeGastosCuotidianos    #Como el dinero del agente es un valor positivo, lo multiplicamos por -1 para que represente un gasto
            
        #Comprobamos si el gasto sobrepasa la frontera
        if abs(gastosCuotidianos) > abs(self.scenario.gastosDiariosMax):
            gastosCuotidianos = self.scenario.gastosDiariosMax

        if abs(gastosCuotidianos) < abs(self.scenario.gastosDiariosMin):
            gastosCuotidianos = self.scenario.gastosDiariosMin

        return gastosCuotidianos
    

    def comprobarTiempoEnergiaFelicidadDinero(self, tiempo=None, energia=None, felicidad=None, dinero=None):
        '''Método principal para comprobar si el agente puede realizar una acción. Comprueba si el agente tiene los recursos necesarios para realizar una cierta acción'''
        #Si el agente tiene igual o más energía de la necesaria y más o igual tiempo disponible que los que requieren la acción, devolvemos true
        if (tiempo is None or self.tiempoDisponible >= tiempo) and (energia is None or self.energia >= abs(energia)) and (felicidad is None or self.felicidad >= abs(felicidad)) and (dinero is None or self.dinero >= abs(dinero)):
            return True
        else:
            return False
        
    def modificarEnergiaFelicidadDinero(self, energia=None, felicidad=None, dinero=None):
        '''Método para modificar los recursos del agente. Los valores introducidos pueden ser positivos o negativos dependiendo de si se quieren aumentar o disminuir los recursos.'''
        #Comprobamos si se ha modificado la energía
        if (energia is not None):
            self.energia += energia

            #Si tiene más energía de la que es posible, simplemente la ponemos al máximo
            if self.energia > self.energiaMax:
                self.energia = self.energiaMax

            #Realizamos también comprobación sobre el mínimo en caso de que la acción sea obligatoria
            #Si tiene menos energía de la que es posible, simplemente la ponemos al mínimo
            elif self.energia < 0:
                self.energia = 0

        #Comprobamos si se ha modificado la felicidad
        if (felicidad is not None):
            self.felicidad += felicidad

            #Si su felicidad supera el máximo establecido, lo reestablecemos al máximo posible
            if self.felicidad > self.scenario.felicidadMax:
                self.felicidad = self.scenario.felicidadMax

            #Si su felicidad supera el mínimo establecido, lo reestablecemos al mínimo posible
            elif self.felicidad < 0:
                self.felicidad = 0 
        
        #Comprobamos si se ha modificado el dinero
        if (dinero is not None):
            self.dinero += dinero

            #Comprobamos que no tenga una cantidad negativa de dinero
            if self.dinero < 0:
                self.dinero = 0


    def modificarEnergiaMax(self, energiaMax):
        '''Modificamos la energia máxima que puede obtener el agente estando totalmente descansado'''
        self.energiaMax += energiaMax

        #Si su energía máxima supera el máximo establecido, lo reestablecemos al máximo posible
        if self.energiaMax > self.scenario.energiaMaxObtenible:
            self.energiaMax = self.scenario.energiaMaxObtenible

        #Si su energía mínima está por debajo del mínimo establecido, lo reestablecemos al mínimo posible
        elif self.energiaMax < self.scenario.energiaMinObtenible:
            self.energiaMax = self.scenario.energiaMinObtenible


    def ocupar(self, cantidadTiempo):
        '''Método al que se llama cuando ya se ha comprobado que el agente tiene tiempo suficiente para realizar la acción y que ocupa al agente durante una cierta cantidad de time steps.
            Diseñado para ser llamado en la propia acción que ocupa al agente'''
        
        self.tiempoDisponible -= cantidadTiempo     #Le reducimos la cantidad de tiempo que tiene disponible el agente

        cantidadTiempo -= 1.0                       #Restamos 1 al tiempo que se mantiene ocupado ya que la primera hora (primer step) ya la invierte al realizar la acción
        self.ocupado += cantidadTiempo              #Agregamos el tiempo que aún le queda por estar parado en otros steps a su contador de ocupado


    def modificarVecinos(self, cantidadAgentes=None, tipo=None, energia=None, felicidad=None, dinero=None, tiempo=None):
        '''Método para modificar recursos de todos los vecinos de un Agente, pudiéndose filtrar por tipo y por cantidad de agentes (None = Todos). Devuelve una lista con los agentes afectados.
           Se supone que los agentes vecinos están obligados a gastar sus recursos (consecuencias inevitables de los actos de otro agente)'''
        agentesAfectados = []

        #Recorremos cada agente
        for agente in self.vecindario.agents:

            #Si se ha introducido una cantidad de agentes y esta no es un número positivo, dejamos de buscar
            if (cantidadAgentes is not None) and (cantidadAgentes <= 0):
                break

            #Si han introducido un filtro por tipo, nos aseguramos de que sea de ese tipo
            if tipo is not None:
                if agente.tipo == tipo:  

                    #Se les pasan los valores directamente ya que modificarEnergiaFelicidadDinero ya gestiona posibles nulos  
                    agente.modificarEnergiaFelicidadDinero(energia=energia, felicidad=felicidad, dinero=dinero)

                    #Comprobamos si debe modificarse el tiempo
                    if tiempo is not None:
                        agente.ocupar(tiempo)

                    agentesAfectados.append(agente)

                    #Si hay un límite de agentes, reducimos en 1 los que quedan por buscar
                    if (cantidadAgentes is not None):
                        cantidadAgentes -= 1           


            else:   #Si no hay filtro por tipo, simplemente modificamos cualquier agente
                agente.modificarEnergiaFelicidadDinero(energia=energia, felicidad=felicidad, dinero=dinero)

                if tiempo is not None:
                    agente.ocupar(tiempo)

                agentesAfectados.append(agente)

                #Si hay un límite de agentes, reducimos en 1 los que quedan por buscar
                if (cantidadAgentes is not None):
                    cantidadAgentes -= 1  
        
        return agentesAfectados


    def estaDisponible(self):
        '''Método que determina si el agente está disponible y puede realizar acciones, o se encuentra ocupado y no puede'''
        #Si está disponible (no está ocupado), devolvemos true
        if self.ocupado < 1.0:
            return True
        else:
            return False


    #Acciones que pueden realizar los agentes
    def move(self):
        '''Moverse a una celda aleatoria que se encuentre cerca suya'''
        if self.casillasVacias:
            nuevaPosicion = self.random.choice(self.casillasVacias)
            self.move_to(nuevaPosicion)
        

    def dormir(self, horas):
        '''Dormir para recuperar energia'''
        #Comprobamos que no pretenda dormir o demasiado o demasiado poco tiempo
        if horas < self.scenario.horasMinimasDormir:
            horas = self.scenario.horasMinimasDormir

        if horas > self.scenario.horasMaximasDormir:
            horas = self.scenario.horasMaximasDormir

        #Nos aseguramos de que duerma una cantidad de tiempo fácilmente controlable
        redondearDecimalMedio(horas)

        #En caso de que no tenga tiempo suficiente para dormir tanto como quiere, reducimos la cantidad de horas que podrá dormir hasta que, o bien pueda dormir, o bien no llegue al mínimo
        while((not self.comprobarTiempoEnergiaFelicidadDinero(tiempo=horas)) and (horas > self.scenario.horasMinimasDormir)):
            horas -= 0.5      #Restamos media hora

        #Comprobamos si tiene la cantidad suficiente de horas disponibles para dormir
        if self.comprobarTiempoEnergiaFelicidadDinero(tiempo=horas):
            #Duerme la cantidad de horas decidida y recupera energía en función de la cantidad de horas que duerme
            porcentajeRecuperado = 1/self.scenario.horasMaximasDormir * horas
            energiaRecuperada = int(self.energiaMax * porcentajeRecuperado)

            #Si duerme especialmente bien o especialmente mal modifica su felicidad
            cambioFelicidad = None    
            if horas >= 0.8*self.scenario.horasMaximasDormir:               #Si duerme un 80% o más del máximo, aumenta su felicidad
                cambioFelicidad = self.scenario.felicidadDormirBien
            if horas <= 0.6*self.scenario.horasMaximasDormir:               #Si duerme un 60% o menos del máximo, disminuye su felicidad
                cambioFelicidad = self.scenario.felicidadDormirMal

            self.modificarEnergiaFelicidadDinero(energia=energiaRecuperada, felicidad=cambioFelicidad)
            
            #Lo ocupamos durmiendo
            self.ocupar(horas)

            return True
        
        #Si no tiene la suficiente cantidad de tiempo para dormir, no duerme
        return False    


    def entrenarGimnasio(self):
        '''Método que simula que el agente decide entrenar en el gimnasio'''
        
        #Comprobamos si al agente le toca pagar el gimnasio
        cuotaGimnasio = 0
        if self.tiempoMensualidadGym <= 0:
            cuotaGimnasio = self.scenario.cuotaGimnasio


        #Comprobamos que el agente tenga la energia, tiempo y dinero (si necesita pagar) necesarios para realizar esta acción
        if self.comprobarTiempoEnergiaFelicidadDinero(energia=self.scenario.energiaEntrenar, tiempo=self.scenario.tiempoEntrenar, dinero=cuotaGimnasio):
            
            #Si hoy ha sido el día en el que se ha tenido que pagar la suscripción, reiniciamos el contador de días
            if cuotaGimnasio != 0:
                self.tiempoMensualidadGym = 30
            
            #Modificamos los recursos necesarios por haber realizado las acciones
            self.modificarEnergiaFelicidadDinero(energia=self.scenario.energiaEntrenar, felicidad=self.scenario.felicidadEntrenar, dinero=cuotaGimnasio)
            self.modificarEnergiaMax(self.scenario.aumentoEnergiaMaxEntrenar)
            self.ocupar(self.scenario.tiempoEntrenar)

            return True
        
        #Si no puede realizar la acción, devolvemos False
        return False
    

    def compraLujosa(self):
        '''Acción que representa realizar una compra cara que no es vital para la supervivencia'''
        #Comprobamos si el agente tiene los recursos necesarios para realizar la acción
        if self.comprobarTiempoEnergiaFelicidadDinero(tiempo=self.scenario.tiempoLujo, dinero=self.scenario.costeLujo):

            #Modificamos los recursos del agente y lo ocupamos
            self.modificarEnergiaFelicidadDinero(felicidad=self.scenario.felicidadLujo, dinero=self.scenario.costeLujo)
            self.ocupar(self.scenario.tiempoLujo)

            return True
        
        #Si no ha podido realizar la acción, devolvemos False
        return False


    def ocio(self):
        '''Acción que representa realizar actividades de ocio que no representan un deporte, como podría ser ir al cine con unos amigos'''
        #Comprobamos si el agente tiene los recursos necesarios para realizar la acción
        if self.comprobarTiempoEnergiaFelicidadDinero(energia=self.scenario.energiaOcio, tiempo=self.scenario.tiempoOcio, dinero=self.scenario.costeOcio):

            #Modificamos los recursos del agente y lo ocupamos
            self.modificarEnergiaFelicidadDinero(energia=self.scenario.energiaOcio, felicidad=self.scenario.felicidadOcio, dinero=self.scenario.costeOcio)
            self.ocupar(self.scenario.tiempoOcio)

            return True
        
        #Si no ha podido realizar la acción, devolvemos False
        return False
    

    def comidaBasura(self):
        '''Acción que representa comer comida basura, lo cual supone un ahorro económico a expensas del bienestar del agente'''
        #No es necesaria ninguna comprobación porque el usuario no necesita recursos
        #Modificamos los recursos del agente y lo ocupamos
        ahorro = (-1) * self.gastosCuotidianos * self.scenario.porcentajeAhorro             #Multiplicamos por -1 porque antes representaba un gasto (valor negativo) y ahora tenemos que convertirlo en un ahorro
        self.modificarEnergiaFelicidadDinero(energia=self.scenario.energiaComidaBasura, felicidad=self.scenario.felicidadComidaBasura, dinero=ahorro)

        self.modificarEnergiaMax(energiaMax=self.scenario.reduccionEnergiaMaxComidaBasura)

        self.ocupar(self.scenario.tiempoComidaBasura)
    
    
    #Métodos para controlar el flujo de acciones o estado de los agentes
    def actualizarDepresion(self):
        '''Método que lleva un contador de los días que un agente ha estado deprimido. Si lleva demasiados días deprimido, el agente es eliminado'''
        #Si tiene demasiada poca felicidad está deprimido y le sumamos un día con depresión
        if self.felicidad < self.scenario.umbralDepresion:
            self.diasDepresion += 1

            self.estado = "Deprimido"

            #Si lleva demasiado tiempo deprimido, borramos el agente
            if self.diasDepresion >= self.diasSuicidio:
                self.eliminarAgente()

        else:
            #Si no está deprimido, disminuimos sus dias con depresión
            self.diasDepresion -= 3

            self.estado = "Feliz"

            #Aseguramos que no sea menor al mínimo
            if self.diasDepresion < 0:
                self.diasDepresion = 0


    def printCaracteristicas(self):
        print(f"ID = {self.unique_id}. Tipo del agente = {self.tipo}. Dinero = {self.dinero}. Felicidad = {self.felicidad}. Energia = {self.energia}. Tiempo disponible = {self.tiempoDisponible}. Tiempo máximo posible = {self.tiempoMaxPosible}.")


    def avanceDiarioGeneral(self):
        '''Método que simula el paso de un día a otro. Avanza los contadores y implementa cambios que están diseñados para avanzar diariamente'''
        
        #Reestablecemos la cantidad de tiempo disponible para el agente a su máximo
        self.tiempoDisponible = self.tiempoMaxPosible

        self.actualizarDepresion()

        #Avanzamos en 1 día la cuota del gimnasio
        if self.tiempoMensualidadGym > 0:
            self.tiempoMensualidadGym -= 1

        reduccionFelicidad = self.scenario.reduccionDiariaFelicidad             #Cojemos la cantidad de felicidad que pierde un agente cada día de manera pasiva

        self.gastosCuotidianos = self.calcularGastosCuotidianos()               #Realizamos los gastos cuotidianos del agente y los guardamos por si es necesario calcular el ahorro sobre estos en algún otro momento del día      

        self.modificarEnergiaFelicidadDinero(felicidad=reduccionFelicidad, dinero=self.gastosCuotidianos)


    #Métodos que deben ser sobreescritos por los hijos
    def avanceDiarioEspecifico(self):
        '''Método que simula el paso de un día a otro en las circunstancias específicas para cada tipo de agente. Cada tipo de agente debe
         definir el suyo (aunque lo deje vacío)'''
        raise NotImplementedError("Los agentes deben implementar el método step()")
    
    def avanceSemanalEspecifico(self):
        '''Método que simula el paso de una semana a otra en las circunstancias específicas para cada tipo de agente. Cada tipo de agente debe
         definir el suyo (aunque lo deje vacío)'''
        raise NotImplementedError("Los agentes deben implementar el método step()")

    def step(self):
        '''Método que define qué deben hacer los agentes en cada step, el cual representa 1 hora'''
        raise NotImplementedError("Los agentes deben implementar el método step()")
    
    def elegirAccion(self):
        """Método que define qué acciones puede tomar un agente en un cierto momento"""
        raise NotImplementedError("Los agentes deben implementar el método elegirAccion()")
    
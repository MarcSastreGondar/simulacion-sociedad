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

        self.visionAgente = self.scenario.visionAgente
        self.visionMovimiento = self.scenario.movimientoAgente

        #Variables relacionadas con el tiempo del que dispone el agente para actuar cada día
        self.tiempoVital = self.scenario.tiempoVital
        self.tiempoMaxPosible = self.scenario.tiempoMaxPosible - self.tiempoVital              #Tiempo en horas que el agente tiene disponibles en un dia
        self.tiempoDisponible = self.tiempoMaxPosible                                          #Tiempo que aún le queda disponible al agente para realizar acciones

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
        
        self.felicidad = 0                                                          #Inicializamos el valor de la felicidad para poder modificarlo en el método
        valFelicidad = int(felicidadInicial) + felicidadAleat
        self.modificarEnergiaFelicidadDinero(felicidad=valFelicidad)
        # Aseguramos de que no sobrepase ni el mínimo ni el máximo
        '''if(self.felicidad > 100.0):
            self.felicidad = 100.0
        #################BORRAR
        elif (self.felicidad < 0.0):
            self.felicidad = 0.0'''
        
        self.diasDepresion = 0                                          #Cantidad de días que lleva el agente en depresión
        self.diasSuicidio = self.scenario.mesesSuicidio * 31            #Cantidad de días con depresión acumulados que llevan al agente a ser borrado. Meses * Dias en un mes

        #Parámetros relacionados con las acciones
        self.ocupado = 0.0              #Contador que indica si el agente está realizando alguna acción que le obligue a esperar en los steps (si realiza acciones que tarden más de 1 step)

        self.tiempoMensualidadGym = 0   #Empieza sin estar suscrito al gimnasio                                       
            


    # Métodos comunes de los agentes
    # Métodos auxiliares
    def actualizar_vecinos(self):
        '''
        Miramos las casillas cercanas al agente
        '''
        #Obtenemos los vecinos que tiene el agente alrededor
        self.vecindario = self.cell.get_neighborhood(radius=self.visionAgente)
        self.vecinos = self.vecindario.agents

        #Obtenemos las casillas a las que puede moverse el agente actualmente
        self.vecindarioMovimiento = self.cell.get_neighborhood(radius=self.visionMovimiento)
        self.casillasVacias = [c for c in self.vecindarioMovimiento if c.is_empty]


    def eliminarAgente(self):
        '''Método que elimina permanentemente de la simulación a un agente. Es equivalente a la muerte de una persona y 
           los agentes deben intentar evitarla a toda costa'''
        self.remove()


    #Métodos auxiliares para modificar los recursos de los agentes de manera controlada
    def comprobarEnergiaTiempoDinero(self, energia=None, tiempo=None, dinero=None):
        '''Método principal para comprobar si el agente puede realizar una acción. Comprueba si el agente tiene los recursos necesarios para realizar una cierta acción'''
        #Si el agente tiene igual o más energía de la necesaria y más o igual tiempo disponible que los que requieren la acción, devolvemos true
        if (self.energia >= abs(energia) or energia is None) and (self.tiempoDisponible >= tiempo or tiempo is None) and (self.dinero >= abs(dinero) or dinero is None):
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

            #Si tiene menos energía de la que es posible, simplemente la ponemos al mínimo
            if self.energia < 0:
                self.energia = 0

        #Comprobamos si se ha modificado la felicidad
        if (felicidad is not None):
            self.felicidad += felicidad

            #Si su felicidad supera el máximo establecido, lo reestablecemos al máximo posible
            if self.felicidad > self.scenario.felicidadMax:
                self.felicidad = self.scenario.felicidadMax

            #Si su felicidad supera el mínimo establecido, lo reestablecemos al mínimo posible
            if self.felicidad < 0:
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
        if self.energiaMax < self.scenario.energiaMinObtenible:
            self.energiaMax = self.scenario.energiaMinObtenible


    def ocupar(self, cantidadTiempo):
        '''Método al que se llama cuando ya se ha comprobado que el agente tiene tiempo suficiente para realizar la acción y que ocupa al agente durante una cierta cantidad de time steps.
            Diseñado para ser llamado en la propia acción que ocupa al agente'''
        
        self.tiempoDisponible -= cantidadTiempo     #Le reducimos la cantidad de tiempo que tiene disponible el agente

        cantidadTiempo -= 1.0                       #Restamos 1 al tiempo que se mantiene ocupado ya que la primera hora (primer step) ya la invierte al realizar la acción
        self.ocupado += cantidadTiempo              #Agregamos el tiempo que aún le queda por estar parado en otros steps a su contador de ocupado


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
        while((not self.comprobarEnergiaTiempoDinero(tiempo=horas)) and (horas > self.scenario.horasMinimasDormir)):
            horas -= 0.5      #Restamos media hora

        #Comprobamos si tiene la cantidad suficiente de horas disponibles para dormir
        if self.comprobarEnergiaTiempoDinero(tiempo=horas):
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
        if self.comprobarEnergiaTiempoDinero(self.scenario.energiaEntrenar, self.scenario.tiempoEntrenar, cuotaGimnasio):
            
            #Si hoy ha sido el día en el que se ha tenido que pagar la suscripción, reiniciamos el contador de días
            if cuotaGimnasio != 0:
                self.tiempoMensualidadGym = 30
            
            #Modificamos los recursos necesarios por haber realizado las acciones
            self.modificarEnergiaFelicidadDinero(energia=self.scenario.energiaEntrenar, felicidad=self.scenario.aumentoFelicidadEntrenar, dinero=cuotaGimnasio)
            self.modificarEnergiaMax(self.scenario.aumentoEnergiaMaxEntrenar)
            self.ocupar(self.scenario.tiempoEntrenar)

            return True
        
        #Si no puede realizar la acción, devolvemos False
        return False
    

    def compraLujosa(self):
        '''Acción que representa realizar una compra cara que no es vital para la supervivencia'''
        #Comprobamos si el agente tiene los recursos necesarios para realizar la acción
        if self.comprobarEnergiaTiempoDinero(tiempo=self.scenario.tiempoLujo, dinero=self.scenario.costeLujo):

            #Modificamos los recursos del agente y lo ocupamos
            self.modificarEnergiaFelicidadDinero(felicidad=self.scenario.felicidadLujo, dinero=self.scenario.costeLujo)
            self.ocupar(self.scenario.tiempoLujo)

            return True
        
        #Si no ha podido realizar la acción, devolvemos False
        return False


    def ocio(self):
        '''Acción que representa realizar actividades de ocio que no representan un deporte, como podría ser ir al cine con unos amigos'''
        

    
    #Métodos para controlar el flujo de acciones o estado de los agentes
    def actualizarDepresion(self):

        #Si tiene demasiada poca felicidad está deprimido y le sumamos un día con depresión
        if self.felicidad < self.scenario.umbralDepresion:
            self.diasDepresion += 1

            #Si lleva demasiado tiempo deprimido, borramos el agente
            if self.diasDepresion >= self.diasSuicidio:
                self.eliminarAgente()

        else:
            #Si no está deprimido, disminuimos sus dias con depresión
            self.diasDepresion -= 3

            #Aseguramos que no sea menor al mínimo
            if self.diasDepresion < 0:
                self.diasDepresion = 0


    def printCaracteristicas(self):
        print(f"Tipo del agente = {self.tipo}. Tiempo máximo posible = {self.tiempoMaxPosible}. Dinero inicial = {self.dinero}. Felicidad inicial = {self.felicidad}.")


    ##### QUE PASE UN DÍA CADA 24 STEPS, LLEVAR UN CONTADOR EN EL modeloSociedad
    def avanceDiarioGeneral(self):
        '''Método que simula el paso de un día a otro. Avanza los contadores y implementa cambios que están diseñados para avanzar diariamente'''
        
        #Reestablecemos la cantidad de tiempo disponible para el agente a su máximo
        self.tiempoDisponible = self.tiempoMaxPosible

        #Realizamos los gastos cuotidianos del agente
        gastosCuotidianos = -1 * self.dinero * self.scenario.porcentajeGastosCuotidianos    #Como el dinero del agente es un valor positivo, lo multiplicamos por -1 para que represente un gasto
        
        #Comprobamos si el gasto sobrepasa la frontera
        if abs(gastosCuotidianos) > abs(self.scenario.gastosDiariosMax):
            gastosCuotidianos = self.scenario.gastosDiariosMax

        if abs(gastosCuotidianos) < abs(self.scenario.gastosDiariosMin):
            gastosCuotidianos = self.scenario.gastosDiariosMin

        self.modificarEnergiaFelicidadDinero(dinero=gastosCuotidianos)


        #Avanzamos en 1 día la cuota del gym
        if self.tiempoMensualidadGym > 0:
            self.tiempoMensualidadGym -= 1


    #Métodos que deben ser sobreescritos por los hijos
    def avanceDiarioEspecifico(self):
        '''Método que simula el paso de un día a otro en las circunstancias específicas para cada tipo de agente. Cada tipo de agente debe
         definir el suyo (aunque lo deje vacío)'''
        raise NotImplementedError("Los agentes deben implementar el método step()")

    def step(self):
        '''Método que define qué deben hacer los agentes en cada step, el cual representa 1 hora'''
        raise NotImplementedError("Los agentes deben implementar el método step()")
    
    def elegirAccion(self):
        """Método que define qué acciones puede tomar un agente en un cierto momento"""
        raise NotImplementedError("Los agentes deben implementar el método elegirAccion()")
    
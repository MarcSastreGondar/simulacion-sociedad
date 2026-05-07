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
        felicidadAleat = int(self.aleat.uniform(-felicidadAleat, felicidadAleat))  #+- un porcentaje del que tiene inicialmente

        self.felicidad = int(felicidadInicial) + felicidadAleat

        
        self.diasDepresion = 0                                          #Cantidad de días que lleva el agente en depresión
        self.diasSuicidio = self.scenario.mesesSuicidio * 31            #Cantidad de días con depresión acumulados que llevan al agente a ser borrado. Meses * Dias en un mes

        #Parámetros relacionados con las acciones
        self.ocupado = 0.0              #Contador que indica si el agente está realizando alguna acción que le obligue a esperar en los steps (si realiza acciones que tarden más de 1 step)


        self.tiempoMensualidadGym = 0   #Empieza sin estar suscrito al gimnasio                                       

        # Aseguramos de que no sobrepase ni el mínimo ni el máximo
        if(self.felicidad > 100.0):
            self.felicidad = 100.0
        
        elif (self.felicidad < 0.0):
            self.felicidad = 0.0
            


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
        self.casillasVacias = [c for c in self.vecindarioMovimiento if c.is_empty] #####Meter que mire los agentes en la celda y que todos estén muertos


    def eliminarAgente(self):
        '''Método que elimina permanentemente de la simulación a un agente. Es equivalente a la muerte de una persona y 
           los agentes deben intentar evitarla a toda costa'''
        self.remove()


    #Métodos auxiliares para aumentar los recursos de los agentes de manera controlada
    def aumentoEnergia(self, energiaAumentar):
        self.energia += energiaAumentar

        #Si tiene más energía de la que es posible, simplemente la ponemos al máximo
        if self.energia > self.energiaMax:
            self.energia = self.energiaMax

    def aumentoFelicidad(self, felicidadAumentar):
        '''Aumentamos la felicidad que tiene actualmente el agente'''
        self.felicidad += felicidadAumentar

        #Si su felicidad supera el máximo establecido, lo reestablecemos al máximo posible
        if self.felicidad > self.scenario.felicidadMax:
            self.felicidad = self.scenario.felicidadMax

    def aumentoEnergiaMax(self, energiaAumentar):
        '''Aumentamos la energia máxima que puede obtener el agente estando totalmente descansado'''
        self.energiaMax += energiaAumentar

        #Si su energía máxima supera el máximo establecido, lo reestablecemos al máximo posible
        if self.energiaMax > self.scenario.energiaMaxObtenible:
            self.energiaMax = self.scenario.energiaMaxObtenible

    #Métodos auxiliares para reducir los recursos de los agentes de manera controlada
    def comprobarEnergiaTiempoDinero(self, energia=None, tiempo=None, dinero=None):
        '''Método para comprobar si el agente tiene los recursos necesarios para realizar una cierta acción'''
        #Si el agente tiene igual o más energía de la necesaria y más o igual tiempo disponible que los que requieren la acción, devolvemos true
        if (self.energia >= energia or energia is None) and (self.tiempoDisponible >= tiempo or tiempo is None) and (self.dinero >= dinero or dinero is None):
            return True
        else:
            return False
        

    def disminuirDinero(self, dineroDisminuir):
        '''Método para reducir el dinero que tiene el agente. Debería utilizarse única y exclusivamente en caso de que no importe que el agente
        no tenga dinero suficiente para completar la acción ya que esta debe realizarse sí o sí (como los gastos cuotidianos obligatorios)'''
        self.dinero -= dineroDisminuir

        #Comprobamos que no tenga una cantidad negativa de dinero
        if self.dinero < 0:
            self.dinero = 0


    def ocupar(self, cantidadTiempo):
        '''Método al que se llama cuando ya se ha comprobado que el agente tiene tiempo suficiente para realizar la acción y que ocupa al agente durante una cierta cantidad de time steps.
            Diseñado para ser llamado en la propia acción que ocupa al agente'''
        
        self.tiempoDisponible -= cantidadTiempo     #Le reducimos la cantidad de tiempo que tiene disponible el agente

        cantidadTiempo -= 1.0                       #Restamos 1 al tiempo que se mantiene ocupado ya que la primera hora (primer step) ya la invierte al realizar la acción
        self.ocupado += cantidadTiempo              #Agregamos el tiempo que aún le queda por estar parado en otros steps a su contador de ocupado


    def estaDisponible(self):
        '''Método que determina si el agente está disponible y puede realizar acciones, o se encuentra ocupado o muerto y no puede'''
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
        
    #####
    def dormir(self, horas):
        '''Dormir para recuperar energia. Devuelve al cantidad de energia recuperada'''
        #Comprobamos que no pretenda dormir o demasiado o demasiado poco tiempo
        if horas < self.scenario.horasMinimasDormir:
            horas = self.scenario.horasMinimasDormir

        if horas > self.scenario.horasMaximasDormir:
            horas = self.scenario.horasMaximasDormir

        #Nos aseguramos de que duerma una cantidad de tiempo fácilmente controlable
        redondearDecimalMedio(horas)

        #Duerme la cantidad de horas decidida y recupera energía en función de la cantidad de horas que duerme
        energiaRecuperada = 1/self.energiaMax * horas
        energiaRecuperada = redondearDecimalMedio(energiaRecuperada)
        self.aumentoEnergia(energiaRecuperada)
        
        ##################AUMENTAR FELICIDAD
        
        #Lo ocupamos durmiendo
        self.ocupar(horas)

        return energiaRecuperada

        

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
            
            self.dinero -= cuotaGimnasio

            self.energia -= self.scenario.energiaEntrenar 

            self.aumentoEnergiaMax(self.scenario.aumentoEnergiaMaxEntrenar)
            self.aumentoFelicidad(self.scenario.aumentoFelicidadEntrenar)
            self.ocupar(self.scenario.tiempoEntrenar)

    
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

        #########GASTOS CUOTIDIANOS!!!!!!!!!!!!!!

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
    
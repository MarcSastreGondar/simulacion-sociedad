#¿?¿$"acs"   Documento con el código común entre los distintos agentes para evitar la repetición de código
'''
gashfd
'''

#Importamos la clase con el agente por defecto de Mesa
import mesa

class AgenteBase(mesa.discrete_space.CellAgent):
    """Clase base que contiene atributos y métodos comunes a todos los agentes."""

    def __init__(self, modelo, tiempoMaxPosible=24, tiempoVital=8, energiaInicial=100, porcentajeAleatorio=0.5, umbralDepresion=10, mesesSuicidio=24, visionAgente=3, movimientoAgente=1, dineroInicial=500, felicidadInicial=60.0):
        super().__init__(modelo)

        # Definimos los atributos comunes entre todos los agentes
        #Usamos el mismo RandomNumberGenerator que tiene el modelo
        self.aleat = modelo.rng
        
        self.tipo = "Ninguno"        

        self.visionAgente = visionAgente
        self.visionMovimiento = movimientoAgente

        #Variables relacionadas con el tiempo del que dispone el agente para actuar cada día
        self.tiempoMaxPosible = tiempoMaxPosible - tiempoVital                                          #Tiempo en horas que el agente tiene disponibles en un dia
        self.tiempoDisponible = self.tiempoMaxPosible                                                   #Tiempo que aún le queda disponible al agente para realizar acciones

        #Energia, la cual es necesaria para realizar acciones
        self.energia = energiaInicial


        #Cantidad de dinero que posee un agente en un cierto momento
        dineroAleat = porcentajeAleatorio * dineroInicial
        dineroAleat = int(self.aleat.uniform(-dineroAleat, dineroAleat))    #Introducimos aleatoriedad en la cantidad de dinero que tendrá cada agente inicialmente (+- un porcentaje)        
        self.dinero = int(dineroInicial) + dineroAleat


        #Grado de desagrado por la situación en la que se encuentra el agente. Entre 0 (mínimo) y 100 (máximo)
        felicidadAleat = porcentajeAleatorio * felicidadInicial
        felicidadAleat = int(self.aleat.uniform(-felicidadAleat, felicidadAleat))  #+- un porcentaje del que tiene inicialmente

        self.felicidad = int(felicidadInicial) + felicidadAleat

        
        self.umbralDepresion = umbralDepresion          #A partir de qué punto de felicidad empezamos a considerar que el agente tiene depresión
        self.diasDepresion = 0                          #Cantidad de días que lleva el agente en depresión
        self.diasSuicidio = mesesSuicidio * 31          #Cantidad de días con depresión acumulados que llevan al agente a ser borrado. Meses * Dias en un mes

        # Aseguramos de que no sobrepase ni el mínimo ni el máximo
        if(self.felicidad > 100.0):
            self.felicidad = 100.0
        
        elif (self.felicidad < 0.0):
            self.felicidad = 0.0
            


    # Métodos comunes de los agentes
    def actualizar_vecinos(self):
        """
        Miramos las casillas cercanas al agente
        """
        #Obtenemos los vecinos que tiene el agente alrededor
        self.vecindario = self.cell.get_neighborhood(radius=self.visionAgente)
        #print(self.vecindario)
        self.vecinos = self.vecindario.agents

        #Obtenemos las casillas a las que puede moverse el agente actualmente
        self.vecindarioMovimiento = self.cell.get_neighborhood(radius=self.visionMovimiento)
        #print(self.vecindarioMovimiento)
        self.casillasVacias = [c for c in self.vecindarioMovimiento if c.is_empty]


    def move(self):
        """Move to a random empty neighboring cell if movement is enabled."""
        if self.casillasVacias:
            nuevaPosicion = self.random.choice(self.casillasVacias)
            self.move_to(nuevaPosicion)


    def actualizarDepresion(self):

        #Si tiene demasiada poca felicidad está deprimido y le sumamos un día con depresión
        if self.felicidad < self.umbralDepresion:
            self.diasDepresion += 1

            #Si lleva demasiado tiempo deprimido, borramos el agente
            if self.diasDepresion >= self.diasSuicidio:
                eliminarAgente(self)

        else:
            #Si no está deprimido, disminuimos sus dias con depresión
            self.diasDepresion -= 3

            #Aseguramos que no sea menor al mínimo
            if self.diasDepresion < 0:
                self.diasDepresion = 0
        

    
    def eliminarAgente(self):
        '''Método que elimina permanentemente de la simulación a un agente. Es equivalente a la muerte de una persona y 
           los agentes deben intentar evitarla a toda costa'''
        self.remove()


    def printCaracteristicas(self):
        print(f"Tipo del agente = {self.tipo}. Tiempo máximo posible = {self.tiempoMaxPosible}. Dinero inicial = {self.dinero}. Felicidad inicial = {self.felicidad}.")


    def step(self):
        """Método que define qué deben hacer los agentes en cada step"""
        raise NotImplementedError("Los agentes deben implementar el método step()")
    
    def elegirAccion(self):
        """Método que define qué acciones puede tomar un agente en un cierto momento"""
        raise NotImplementedError("Los agentes deben implementar el método elegirAccion()")
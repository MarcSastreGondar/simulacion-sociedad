#¿?¿$"acs"   Documento con el código común entre los distintos agentes para evitar la repetición de código
'''
gashfd
'''

#Importamos la clase con el agente por defecto de Mesa
import mesa

class AgenteBase(mesa.discrete_space.CellAgent):
    """Clase base que contiene atributos y métodos comunes a todos los agentes."""

    def __init__(self, modelo, tiempoMaxPosible=24, tiempoVital=8, energiaInicial=100, porcentajeAleatorio=0.2, visionAgente=3, movimientoAgente=1, dineroInicial=500, insatisfaccionInicial=15.0):
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
        insatisfaccionAleat = porcentajeAleatorio * insatisfaccionInicial
        insatisfaccionAleat = int(self.aleat.uniform(0, insatisfaccionAleat))  #- un porcentaje del que tiene inicialmente

        self.insatisfaccion = int(insatisfaccionInicial) - insatisfaccionAleat

        if(self.insatisfaccion > 100.0):    #Aseguramos de que no sobrepase el máximo
            self.insatisfaccion = 100.0


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


    def printCaracteristicas(self):
        print(f"Tipo del agente = {self.tipo}. Tiempo máximo posible = {self.tiempoMaxPosible}. Dinero inicial = {self.dinero}. Insatisfacción inicial = {self.insatisfaccion}.")


    def step(self):
        """Método que deben sobrescribir las clases hijas"""
        raise NotImplementedError("Las clases hijas deben implementar step()")
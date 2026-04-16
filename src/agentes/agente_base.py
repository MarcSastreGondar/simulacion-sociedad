#¿?¿$"acs"   Documento con el código común entre los distintos agentes para evitar la repetición de código
'''
gashfd
'''

#Importamos la clase con el agente por defecto de Mesa
import mesa


class AgenteBase(mesa.Agent):
    """Clase base que contiene atributos y métodos comunes a todos los agentes."""
    
    def __init__(self, model):
        super().__init__(model)

        # Definimos los atributos que tienen todos los agentes

        self.dinero = 0.0               #Cantidad de dinero que posee un agente en un cierto momento
        self.insatisfaccion = 0.0       #Grado de desagrado por la situación en la que se encuentra el agente. Entre 0 (mínimo) y 100 (máximo)

        #Variables relacionadas con el tiempo del que dispone el agente para actuar cada día
        self.tiempoMaxPosible = 24                                          #Tiempo en horas que el agente tiene disponibles en un dia
        self.tiempoVital = 3                                                #Tiempo que se utiliza en hacer acciones necesarias para la supervivencia (comida, higiene, etc.)
        self.tiempoDisponible = self.tiempoMaxPosible - self.tiempoVital    #Tiempo que aún le queda disponible al agente para realizar acciones

        self.energia = 100                                 #Energia, la cual es necesaria para realizar acciones


        

    def step(self):
        """Método que deben sobrescribir las clases hijas"""
        raise NotImplementedError("Las clases hijas deben implementar step()")
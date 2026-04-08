#¿?¿$"acs"   Documento con el código común entre los distintos agentes para evitar la repetición de código
'''
gashfd
'''

#Importamos la clase con el agente por defecto de Mesa
import mesa
from mesa import Agent

class AgenteBase(mesa.Agent):
    """Clase base que contiene atributos y métodos comunes a todos los agentes."""
    
    def __init__(self, model):
        super().__init__(model)
        # Aquí pondrás los atributos comunes: riqueza, grievance, etc.
        self.riqueza = 0.0
        self.grievance = 0.0
        # ...

    def step(self):
        """Método que deben sobrescribir las clases hijas"""
        raise NotImplementedError("Las clases hijas deben implementar step()")
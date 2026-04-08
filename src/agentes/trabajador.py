#¿?¿$"acs"   Agente que hereda de BaseAgent y representa a un trabajador, que (¡¡¡INCLUIR CÓMO SE COMPORTA!!!)
'''
gashfd
'''

#Importamos todos los métodos comunes entre los distintos tipos de agentes
from .agente_base import AgenteBase


#Creamos la clase del agente Trabajador, que hereda del agente base
class Trabajador(AgenteBase):
    """Agente especializado: comportamiento de producción/recolecta"""
    
    def __init__(self, model, productividad=1.0):
        super().__init__(model)           # Llama al __init__ de BaseAgent
        self.productividad = productividad
        # Puedes añadir más atributos específicos aquí

    def step(self):
        # Aquí va la lógica específica del trabajador
        pass
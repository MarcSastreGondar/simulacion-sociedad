#¿?¿$"acs"   Agente que hereda de BaseAgent y representa a un inversor, que (¡¡¡INCLUIR CÓMO SE COMPORTA!!!)
'''
gashfd
'''

#Importamos todos los métodos comunes entre los distintos tipos de agentes
from .agente_base import AgenteBase


#Creamos la clase del agente Empresario, que hereda del agente base
class Empresario(AgenteBase):
    """Agente especializado: comportamiento de acumulación/inversión"""
    
    def __init__(self, model, productividad=1.0):
        super().__init__(model)           # Llama al __init__ de BaseAgent
        self.productividad = productividad
        # Puedes añadir más atributos específicos aquí

    def step(self):
        pass
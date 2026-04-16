#¿?¿$"acs"   Agente que hereda de BaseAgent y representa a un inversor, que (¡¡¡INCLUIR CÓMO SE COMPORTA!!!)
'''
gashfd
'''

#Importamos todos los métodos comunes entre los distintos tipos de agentes
from .agente_base import AgenteBase


#Agente Empresario, cuyo comportamiento se basa en acumular dinero y dar trabajo a los demás
class Empresario(AgenteBase):
    
    def __init__(self, model, productividad=1.0):
        
        # Llamamos al __init__ de BaseAgent
        super().__init__(model)
        self.productividad = productividad


    def step(self):
        pass
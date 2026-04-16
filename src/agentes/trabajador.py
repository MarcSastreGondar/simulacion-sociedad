#¿?¿$"acs"   Agente que hereda de BaseAgent y representa a un trabajador, que (¡¡¡INCLUIR CÓMO SE COMPORTA!!!)
'''
gashfd
'''

#Importamos todos los métodos comunes entre los distintos tipos de agentes
from .agente_base import AgenteBase


#Agente Trabajador, cuyo comportamiento se basa en asistir siempre al trabajo y ser relativamente obediente
class Trabajador(AgenteBase):
        
    
    def __init__(self, modelo, tiempoTrabajo=8, maxTiempoAlTrabajo=1.5):
        
        # Llamamos al __init__ de BaseAgent
        super().__init__(modelo)
        self.tiempoTrabajo = tiempoTrabajo + 
       

    def step(self):        
        pass
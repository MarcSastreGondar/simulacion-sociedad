#¿?¿$"acs"   Agente que hereda de BaseAgent y representa a un rebelde, que (¡¡¡INCLUIR CÓMO SE COMPORTA!!!)
'''
gashfd
'''

#Importamos todos los métodos comunes entre los distintos tipos de agentes
from .agente_base import AgenteBase


#Agente Antisistema, cuyo comportamiento se basa en no querer trabajar, aprovecharse de los demás y intentar causar revueltas
class Antisistema(AgenteBase):
        
    
    def __init__(self, modelo, tiempoMaxPosible=24, tiempoVital=8, energiaInicial=100, porcentajeAleatorio=0.2, dineroInicial=50, insatisfaccionInicial=50):
        
        # Llamamos al __init__ de BaseAgent con los parámetros comunes entre todos los agentes
        super().__init__(modelo, tiempoMaxPosible, tiempoVital, energiaInicial, porcentajeAleatorio, dineroInicial, insatisfaccionInicial)
        
        self.tipo = "Antisistema"

    def step(self):
        pass
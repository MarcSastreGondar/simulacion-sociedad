#¿?¿$"acs"   Agente que hereda de BaseAgent y representa a un inversor, que (¡¡¡INCLUIR CÓMO SE COMPORTA!!!)
'''
gashfd
'''

#Importamos todos los métodos comunes entre los distintos tipos de agentes
from .agente_base import AgenteBase


#Agente Empresario, cuyo comportamiento se basa en acumular dinero y dar trabajo a los demás
class Empresario(AgenteBase):
        
    
    def __init__(self, modelo, tiempoMaxPosible=24, tiempoVital=8, energiaInicial=100, porcentajeAleatorio=0.2, visionAgente=3, movimientoAgente=1, dineroInicial=15000, insatisfaccionInicial=0):
        
        # Llamamos al __init__ de BaseAgent con los parámetros comunes entre todos los agentes
        super().__init__(modelo, tiempoMaxPosible, tiempoVital, energiaInicial, porcentajeAleatorio, visionAgente, movimientoAgente, dineroInicial, insatisfaccionInicial)

        self.tipo = "Empresario"

    def step(self):
        self.actualizar_vecinos()
        self.move()
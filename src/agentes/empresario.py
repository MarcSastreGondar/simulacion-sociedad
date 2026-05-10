#¿?¿$"acs"   Agente que hereda de BaseAgent y representa a un inversor, que (¡¡¡INCLUIR CÓMO SE COMPORTA!!!)
'''
gashfd
'''

#Importamos todos los métodos comunes entre los distintos tipos de agentes
from .agente_base import AgenteBase


#Agente Empresario, cuyo comportamiento se basa en acumular dinero y dar trabajo a los demás
class Empresario(AgenteBase):
        
    
    def __init__(self, modelo):
        
        # Llamamos al __init__ de BaseAgent con los parámetros comunes entre todos los agentes
        super().__init__(modelo, modelo.scenario.dineroInicialE, modelo.scenario.felicidadInicialE)

        self.tipo = "Empresario"



    def step(self):
        self.actualizar_vecinos()
        self.move()

        self.actualizarDepresion()


    def avanceDiarioEspecifico(self):
        '''Método que simula el paso de un día a otro para los Empresarios'''

    def avanceSemanalEspecifico(self):
        '''Método que simula el paso de una semana a otra para los Empresarios'''

    def elegirAccion(self):
        """Método que define qué acciones puede tomar un Empresario en un cierto momento"""
        print()
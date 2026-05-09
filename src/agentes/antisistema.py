#¿?¿$"acs"   Agente que hereda de BaseAgent y representa a un rebelde, que (¡¡¡INCLUIR CÓMO SE COMPORTA!!!)
'''
gashfd
'''

#Importamos todos los métodos comunes entre los distintos tipos de agentes
from .agente_base import AgenteBase


#Agente Antisistema, cuyo comportamiento se basa en no querer trabajar, aprovecharse de los demás y intentar causar revueltas
class Antisistema(AgenteBase):
        
    
    def __init__(self, modelo):
        
        # Llamamos al __init__ de BaseAgent con los parámetros comunes entre todos los agentes
        super().__init__(modelo, modelo.scenario.dineroInicialA, modelo.scenario.dineroInicialA)
        
        self.tipo = "Antisistema"

    def step(self):
        self.actualizar_vecinos()
        self.move()

        if self.felicidad > 0:
            self.felicidad += 1
        self.actualizarDepresion()


    def avanceDiarioEspecifico(self):
        '''Método que simula el paso de un día a otro para los Antisistema'''

    def avanceSemanalEspecifico(self):
        '''Método que simula el paso de una semana a otra para los Antisistema'''

    def elegirAccion(self):
        """Método que define qué acciones puede tomar un Antisistema en un cierto momento"""
        print()
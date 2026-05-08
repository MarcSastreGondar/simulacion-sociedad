#¿?¿$"acs"   Agente que hereda de BaseAgent y representa a un trabajador, que (¡¡¡INCLUIR CÓMO SE COMPORTA!!!)
'''
gashfd
'''

#Importamos todos los métodos comunes entre los distintos tipos de agentes
from .agente_base import AgenteBase
import mesa

from metricas import *

#Agente Trabajador, cuyo comportamiento se basa en asistir siempre al trabajo y ser relativamente obediente
class Trabajador(AgenteBase):
        
    
    def __init__(self, modelo):
        
        # Llamamos al __init__ de BaseAgent con los parámetros comunes entre todos los agentes
        super().__init__(modelo, modelo.scenario.dineroInicialT, modelo.scenario.felicidadInicialT)

        self.tipo = "Trabajador"            
        
        #Obtenemos la cantidad de tiempo que pasa trabajando el agente
        self.tiempoTrabajo = self.scenario.tiempoTrabajo + self.aleat.uniform(0.25, self.scenario.maxTiempoAlTrabajo)     #Añadimos aleatoriedad en la cantidad de tiempo que necesita un agente para ir y volver del trabajo (entre 20 minutos y el tiempo introducido)
        self.tiempoTrabajo = redondearDecimalMedio(self.tiempoTrabajo)

        #Usando sus gastos de tiempo obligatorios
        self.tiempoMaxPosible = self.tiempoMaxPosible - self.tiempoTrabajo
        self.tiempoDisponible = self.tiempoMaxPosible


    def step(self):
        '''Definimos lo que puede hacer cada agente en su tiempo libre'''
        #Si el agente no está realizando ninguna otra acción, puede decidir qué hacer
        if self.estaDisponible():
            self.actualizar_vecinos()
            self.move()

            if self.felicidad > 0:
                self.felicidad -= 5

            self.actualizarDepresion()

        else:
            #Si el agente está ocupado, simplemente permanece inactivo durante esta hora
            self.ocupado -= 1.0


    def elegirAccion(self):
        '''Método que define qué acciones puede tomar un Trabajador en un cierto momento'''
        print()
        
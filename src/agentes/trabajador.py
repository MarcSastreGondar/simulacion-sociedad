#¿?¿$"acs"   Agente que hereda de BaseAgent y representa a un trabajador, que (¡¡¡INCLUIR CÓMO SE COMPORTA!!!)
'''
gashfd
'''

#Importamos todos los métodos comunes entre los distintos tipos de agentes
from .agente_base import AgenteBase
from ..metricas import *
import mesa


#Agente Trabajador, cuyo comportamiento se basa en asistir siempre al trabajo y ser relativamente obediente
class Trabajador(AgenteBase):
        
    
    def __init__(self, modelo, tiempoMaxPosible=24, tiempoVital=8, energiaInicial=100, porcentajeAleatorio=0.2, umbralDepresion=10, mesesSuicidio=24, visionAgente=3, movimientoAgente=1, dineroInicial=500, insatisfaccionInicial=15.0, tiempoTrabajo=8, maxTiempoAlTrabajo=1.5):
        
        # Llamamos al __init__ de BaseAgent con los parámetros comunes entre todos los agentes
        super().__init__(modelo, tiempoMaxPosible, tiempoVital, energiaInicial, porcentajeAleatorio, umbralDepresion, mesesSuicidio, visionAgente, movimientoAgente, dineroInicial, insatisfaccionInicial)

        self.tipo = "Trabajador"            
        
        #Obtenemos la cantidad de tiempo que pasa trabajando el agente
        self.tiempoTrabajo = tiempoTrabajo + self.aleat.uniform(0.25, maxTiempoAlTrabajo)     #Añadimos aleatoriedad en la cantidad de tiempo que necesita un agente para ir y volver del trabajo (entre 20 minutos y el tiempo introducido)
        self.tiempoTrabajo = redondearMediaHora(self.tiempoTrabajo)

        #Usando sus gastos de tiempo obligatorios
        self.tiempoMaxPosible = self.tiempoMaxPosible - self.tiempoTrabajo
        self.tiempoDisponible = self.tiempoMaxPosible


    def step(self):
        '''Definimos las acciones que tomarán los trabajadores'''
        self.actualizar_vecinos()
        self.move()

        if self.felicidad > 0:
            self.felicidad -= 1

        self.actualizarDepresion()

    def elegirAccion(self):
        """Método que define qué acciones puede tomar un Trabajador en un cierto momento"""
        print()
        
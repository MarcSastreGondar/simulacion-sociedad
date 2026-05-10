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



    #Métodos auxiliares 
    def contagiarFelicidadEmpresario(self):
        '''Método que, en caso de que un Empresario esté contento, pone de mejor humor a los demás Trabajadores que tenga cerca. No es una acción, simplemente ocurre de manera pasiva en cada step'''
        #Si está suficientemente feliz, contagia a los demás Trabajadores
        if self.felicidad >= self.scenario.umbralContagiarFelicidadE:
            
            #Recorremos cada agente y le aumentamos su felicidad si es un Trabajador
            for agente in self.vecindario.agents:
                if agente.tipo == "Trabajador":
                    agente.modificarEnergiaFelicidadDinero(felicidad=self.scenario.felicidadContagiarE)


    #Acciones que sólo pueden realizar los Empresarios
    def bonificacionMonetaria(self):
        '''Método en el que un Empresario da una bonificación monetaria a los Trabajadores cercanos para ponelos de mejor humor. O les paga a todos o a ninguno'''
        
        trabajadoresBeneficiados = []

        #Primero comprobamos cuantos Trabajadores hay cerca que tengan menos de una cierta cantidad de felicidad
        for agente in self.vecindario.agents:
            if (agente.tipo == "Trabajador") and (agente.felicidad < self.scenario.umbralFelicidadBonificacionMonetaria):
                trabajadoresBeneficiados.append(agente)


        #Una vez obtenida la lista, comprobamos si el empresario tiene dinero suficiente para recompensar a los Trabajadores
        cantTrabajadores = len(trabajadoresBeneficiados)

        if cantTrabajadores > 0:
            dineroTotalGastar = (-1) * cantTrabajadores * self.scenario.dineroPorTrabajadorBonificacion     #Por -1 porque representa un gasto

            if self.comprobarEnergiaTiempoDinero(dinero=dineroTotalGastar):
                #En caso de tener dinero suficiente, el empresario lo gasta en bonificarles
                self.modificarEnergiaFelicidadDinero(dinero=dineroTotalGastar)      #El empresario usa el dinero

                #Recorremos cada agente para darles el dinero a cada uno
                for agente in trabajadoresBeneficiados:
                    agente.modificarEnergiaFelicidadDinero(felicidad=agente.scenario.aumentoFelicidadTrabajadorBonificacion, dinero=agente.scenario.dineroPorTrabajadorBonificacion)

                return True
        
        #Si no se han encontrado trabajadores que cumplan las condiciones o el Empresario no tiene dinero suficiente, devolvemos False
        return False


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
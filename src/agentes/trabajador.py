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
        
        #Obtenemos la cantidad de tiempo que pasa trabajando presencialmente el agente
        self.tiempoAlTrabajo = self.aleat.uniform(0.25, self.scenario.maxTiempoAlTrabajo)     #Añadimos aleatoriedad en la cantidad de tiempo que necesita un agente para ir y volver del trabajo (entre 20 minutos y el tiempo introducido)
        self.tiempoPresencialTrabajo = self.scenario.tiempoTrabajo + self.tiempoAlTrabajo
        self.tiempoPresencialTrabajo = redondearDecimalMedio(self.tiempoPresencialTrabajo)


        #Obtenemos la cantidad de dinero que obtiene el agente después de un día estándar presencial en el trabajo (para no recalcularlo cada vez)
        self.sueldoMensual = self.scenario.sueldoMedio

        #Añadimos una aleatoriedad inicial en el sueldo
        parteAleatoria = self.porcentajeAleatorio * self.scenario.sueldoMedio
        parteAleatoria = int(self.aleat.uniform(-parteAleatoria, parteAleatoria))
        self.modificarSueldoMensual(dinero=parteAleatoria)                              

        #Inicializamos el contador de días que tiene que trabajar esta semana
        self.diasLaborablesPendientes = self.scenario.diasLaborablesSemanales
        


    #Métodos auxiliares 
    def contagiarFelicidadTrabajador(self):
        '''Método que, en caso de que un Trabajador esté contento, pone de mejor humor a los demás agentes que tenga cerca. No es una acción, simplemente ocurre de manera pasiva en cada step'''
        #Si está suficientemente feliz, contagia a los demás
        if self.felicidad >= self.scenario.umbralContagiarFelicidadT:
            
            self.modificarVecinos(felicidad=self.scenario.felicidadContagiarT)

    
    def modificarSueldoMensual(self, dinero):
        '''Método para aumentar o disminuir el sueldo que cobra cada mes el Trabajador y, por extensión, el que gana por cada día de Trabajo'''

        self.sueldoMensual += dinero

        if self.sueldoMensual < self.scenario.sueldoMinimo:
            self.sueldoMensual = self.scenario.sueldoMinimo

        self.dineroDiaTrabajo = self.sueldoMensual / self.scenario.diasLaborablesAlMes


    #Acciones que sólo pueden realizar los Trabajadores
    def trabajar(self):
        '''Acción de trabajar presencialmente'''

        #Comprobamos que el agente tenga el tiempo necesario para trabajar
        if self.comprobarEnergiaTiempoDinero(tiempo=self.tiempoPresencialTrabajo):
            
            #Modificamos los recursos necesarios por haber trabajado
            self.modificarEnergiaFelicidadDinero(energia=self.scenario.energiaTrabajar, felicidad=self.scenario.felicidadTrabajar, dinero=self.dineroDiaTrabajo)
            self.ocupar(self.tiempoPresencialTrabajo)

            return True
        
        #Si no puede realizar la acción, devolvemos False
        return False

    
    def trabajarDoble(self):
        '''Acción que representa tener 2 trabajos presenciales distintos'''
        #Comprobamos que el agente tenga el tiempo necesario para trabajar
        tiempoDoble = 2 * self.tiempoPresencialTrabajo
        if self.comprobarEnergiaTiempoDinero(tiempo=tiempoDoble):
            energiaDoble = 2 * self.scenario.energiaTrabajar
            felicidadDoble = 2 * self.scenario.felicidadTrabajar
            dineroDoble = 2 * self.dineroDiaTrabajo

            #Modificamos los recursos necesarios por haber trabajado
            self.modificarEnergiaFelicidadDinero(energia=energiaDoble, felicidad=felicidadDoble, dinero=dineroDoble)
            self.modificarEnergiaMax(self.scenario.reduccionEnergiaMaxDobleTrabajo)
            self.ocupar(tiempoDoble)

            return True
        
        #Si no puede realizar la acción, devolvemos False
        return False
    

    def teletrabajar(self):
        '''Acción de teletrabajar (en vez de trabajar presencialmente)'''
        #Comprobamos que el agente tenga el tiempo necesario para trabajar
        if self.comprobarEnergiaTiempoDinero(tiempo=self.scenario.tiempoTrabajo):
            
            dineroTeletrabajo = self.scenario.porcentajeSueldoTeletrabajo * self.dineroDiaTrabajo
            energiaTeletrabajo = self.scenario.porcentajeEnergiaTeletrabajo * self.scenario.energiaTrabajar
            #Modificamos los recursos necesarios por haber trabajado
            self.modificarEnergiaFelicidadDinero(energia=energiaTeletrabajo, dinero=dineroTeletrabajo)
            self.ocupar(self.scenario.tiempoTrabajo)

            return True
        
        #Si no puede realizar la acción, devolvemos False
        return False
    


    #Métodos relacionados con el flujo de los agentes
    def avanceDiarioEspecifico(self):
        '''Método que simula el paso de un día a otro para los Trabajadores'''

        #Si aún le quedan días por trabajar esta semana, el agente debe trabajar
        if(self.diasLaborablesPendientes > 0):
            
            #Elegimos qué jornada laboral va a tener. En caso de estar ocupado, seguirá asistiendo al trabajo igualmente (simplemente se añadirán más horas a su contador)
            opcion = self.aleat.integers(0,2)    ##########
            ##########
            if opcion == 0:
                self.trabajar()
            elif opcion == 1:
                self.trabajarDoble()
            elif opcion == 2:
                self.teletrabajar()
            
            self.diasLaborablesPendientes -= 1      #Restamos en 1 la cantidad de días que puede trabajar el agente esta semana


    def avanceSemanalEspecifico(self):
        '''Método que simula el paso de una semana a otra para los Trabajadores'''
        #Reiniciamos el contador de días que pueden trabajar esta semana
        self.diasLaborablesPendientes = self.scenario.diasLaborablesSemanales
    

    def step(self):
        '''Definimos lo que puede hacer cada agente en su tiempo libre'''

        self.actualizarVecinos()

        #Si el agente no está realizando ninguna otra acción, puede decidir qué hacer
        if self.estaDisponible():            
            self.move()

            ###################
            if self.felicidad > 0:
                self.felicidad -= 5

        else:
            #Si el agente está ocupado, simplemente permanece inactivo durante esta hora
            self.ocupado -= 1.0
        
        #Antes de acabar el paso, si está muy feliz, contagia su felicidad a los agentes cercanos
        self.contagiarFelicidadTrabajador()

    
    def elegirAccion(self):
        '''Método que define qué acciones puede tomar un Trabajador en un cierto momento'''
        print()
        
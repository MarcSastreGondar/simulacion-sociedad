'''
Documento en el que se define el comportamiento específico de todos los agentes de tipo Trabajador, cuyo comportamiento se basa en asistir siempre al trabajo y no ser problemático
'''

#Importamos todos los métodos comunes entre los distintos tipos de agentes
from .agenteBase import AgenteBase

from metricas import *


class Trabajador(AgenteBase):
        
    
    def __init__(self, modelo):
        
        #Instanciamos las acciones específicas de su tipo que puede realizar
        accionesTrabajador = ["trabajar", "trabajarDoble", "teletrabajar", "estudiar"]          #En caso de añadir nuevas acciones, hacerlo siempre a partir de Teletrabajar

        #Llamamos al __init__ del agenteBase con los parámetros comunes entre todos los agentes
        super().__init__(modelo=modelo, dineroInicial=modelo.scenario.dineroInicialT, felicidadInicial=modelo.scenario.felicidadInicialT, accionesEspecificas=accionesTrabajador)

        self.tipo = "Trabajador"            

        #Establecemos los límites inferiores y superiores de la lista de acciones que representen acciones de ir al trabajo
        idxTrabMin = 0          #Desde trabajar
        idxTrabMax = 2          #Hasta teletrabajar

        #En los índices, saltamos todas las acciones generales
        self.idxTrabMin = len(self.listaAcciones) - len(accionesTrabajador) + idxTrabMin    #Todas las acciones - las acciones sólo del trabajador = Acciones generales
        self.idxTrabMax = len(self.listaAcciones) - len(accionesTrabajador) + idxTrabMax    #-1 para que represente el índice real a cojer (por como funciona el length)


        self.reiniciarAgente()    #Instanciamos el valor de sus variables. La primera vez con el epsilon por defecto


    def reiniciarAgente(self, epsilon=None):
        '''Método que instancia las variables del Trabajador con el valor por defecto, importante que el __init__ lo llame'''
        self.reiniciarAgenteGeneral(epsilon=epsilon)

        #Obtenemos la cantidad de tiempo que pasa trabajando presencialmente el agente
        self.tiempoAlTrabajo = self.aleat.uniform(0.25, self.scenario.maxTiempoAlTrabajo)     #Añadimos aleatoriedad en la cantidad de tiempo que necesita un agente para ir y volver del trabajo (entre 15 minutos y el tiempo introducido)
        self.tiempoPresencialTrabajo = self.scenario.tiempoTrabajo + self.tiempoAlTrabajo
        self.tiempoPresencialTrabajo = redondearDecimalMedio(self.tiempoPresencialTrabajo)


        #Obtenemos la cantidad de dinero que obtiene el agente después de un día estándar presencial en el trabajo (para no recalcularlo cada vez)
        self.sueldoMensual = self.scenario.sueldoMedio

        #Añadimos una aleatoriedad inicial en el sueldo
        parteAleatoria = self.porcentajeAleatorio * self.scenario.sueldoMedio
        parteAleatoria = int(self.aleat.uniform(-parteAleatoria, parteAleatoria))


        self.felicidadTrabajar = self.scenario.felicidadTrabajar        #Felicidad que gana o pierde al trabajar, puede irse modificando dependiendo de las condiciones laborales del Trabajador

        self.dineroDiaTrabajo = 0                                       #Para evitar posibles errores
        self.modificarCondicionesLaborales(dinero=parteAleatoria)    



    #Métodos auxiliares 
    def contagiarFelicidadTrabajador(self):
        '''Método que, en caso de que un Trabajador esté contento, pone de mejor humor a los demás agentes que tenga cerca. No es una acción, simplemente ocurre de manera pasiva en cada step'''

        #Si está suficientemente feliz, contagia a los demás
        if self.comprobarTiempoEnergiaFelicidadDinero(felicidad=self.scenario.umbralContagiarFelicidadT):

            self.modificarVecinos(felicidad=self.scenario.felicidadContagiarT)


    def modificarCondicionesLaborales(self, dinero=None, felicidadTrab=None):
        '''Método para aumentar o disminuir el sueldo que cobra cada mes el Trabajador y, por extensión, el que gana por cada día de Trabajo.
           También modifica la felicidad que obtiene por trabajar'''

        #Si ha habido un cambio de sueldo, lo tratamos
        if dinero is not None:
            self.sueldoMensual += dinero

            if self.sueldoMensual < self.scenario.sueldoMinimo:
                self.sueldoMensual = self.scenario.sueldoMinimo

            #Calculamos la nueva cantidad de dinero que obtiene por 1 día de trabajo
            self.dineroDiaTrabajo = int(self.sueldoMensual / self.scenario.diasLaborablesAlMes)

        #Si ha habido un cambio en la felicidad que obtiene el agente por trabajar, la tratamos
        if felicidadTrab is not None:
            self.felicidadTrabajar += felicidadTrab

            if self.felicidadTrabajar > self.scenario.felicidadMaxTrabajar:
                self.felicidadTrabajar = self.scenario.felicidadMaxTrabajar

    

    #Acciones que sólo pueden realizar los Trabajadores
    def trabajar(self, obligatorio=False):
        '''Acción de trabajar presencialmente'''
                
        #Trabaja si es obligatorio que trabaje o, si no es obligatorio pero tiene los recursos necesarios para trabajar
        if (obligatorio is not None and obligatorio) or (self.comprobarTiempoEnergiaFelicidadDinero(tiempo=self.tiempoPresencialTrabajo, energia=self.scenario.energiaTrabajar)):
            
            #Modificamos los recursos necesarios por haber trabajado
            self.modificarEnergiaFelicidadDinero(energia=self.scenario.energiaTrabajar, felicidad=self.scenario.felicidadTrabajar, dinero=self.dineroDiaTrabajo)
            self.ocupar(self.tiempoPresencialTrabajo)

            return True
        
        #Si no puede trabajar, devolvemos False
        return False


    def trabajarDoble(self):
        '''Acción que representa tener 2 trabajos presenciales distintos'''
        
        #Comprobamos que el agente tenga los recursos necesarios para trabajar
        tiempoDoble = 2 * self.tiempoPresencialTrabajo
        energiaDoble = 2 * self.scenario.energiaTrabajar

        #Comprobamos si tiene recursos suficientes para trabajar 2 veces hoy
        if self.comprobarTiempoEnergiaFelicidadDinero(tiempo=tiempoDoble, energia=energiaDoble):
            felicidadDoble = 2 * self.scenario.felicidadTrabajar
            dineroDoble = 2 * self.dineroDiaTrabajo

            #Modificamos los recursos necesarios por haber trabajado 2 veces
            self.modificarEnergiaFelicidadDinero(energia=energiaDoble, felicidad=felicidadDoble, dinero=dineroDoble)
            self.modificarEnergiaMax(self.scenario.reduccionEnergiaMaxDobleTrabajo)
            self.ocupar(tiempoDoble)

            return True
        
        #Si no puede realizar la acción, devolvemos False
        return False
    

    def teletrabajar(self):
        '''Acción de teletrabajar (en vez de trabajar presencialmente)'''

        energiaTeletrabajo = redondearDecimalMedio(self.scenario.porcentajeEnergiaTeletrabajo * self.scenario.energiaTrabajar)

        #Comprobamos que el agente tenga el tiempo necesario para teletrabajar
        if self.comprobarTiempoEnergiaFelicidadDinero(tiempo=self.scenario.tiempoTrabajo, energia=energiaTeletrabajo):
            
            dineroTeletrabajo = int(self.scenario.porcentajeSueldoTeletrabajo * self.dineroDiaTrabajo)

            #Modificamos los recursos necesarios por haber teletrabajado
            self.modificarEnergiaFelicidadDinero(energia=energiaTeletrabajo, dinero=dineroTeletrabajo)
            self.ocupar(self.scenario.tiempoTrabajo)

            return True
        
        #Si no puede realizar la acción, devolvemos False
        return False
    

    def estudiar(self):
        '''Acción de que el agente estudia durante su tiempo libre y consigue algún tipo de experiencia formativa que le permite optar a unas mejores condiciones laborales'''

        #Comprobamos si tiene los recursos suficientes para estudiar (no tenemos en cuenta el tiempo, porque no se considera posible sacarse una formación en menos horas totales de las que tiene un día)
        if self.comprobarTiempoEnergiaFelicidadDinero(energia=self.scenario.energiaEstudiar, dinero=self.scenario.costeEstudiar):

            #Modificamos los recursos por haber estudiado
            self.modificarEnergiaFelicidadDinero(energia=self.scenario.energiaEstudiar, felicidad=self.scenario.felicidadEstudiar, dinero=self.scenario.costeEstudiar)
            self.modificarCondicionesLaborales(dinero=self.scenario.aumentoSueldoEstudiar, felicidadTrab=self.scenario.aumentoFelicidadTrabajoEstudiar)
            
            self.ocupar(self.scenario.tiempoEstudiar)   #El agente entrará en "deuda" de tiempo, así que le ocupará todo su tiempo libre durante algún tiempo

            return True
        
        #Si no ha podido estudiar, devolvemos False
        return False

    

    #Métodos relacionados con el flujo de los agentes
    def avanceSemanalEspecifico(self):
        '''Método que simula el paso de una semana a otra para los Trabajadores'''

        #Sólo participa en el funcionamiento de la simulación si está vivo
        if self.estado != self.scenario.estadoMuerto:
        
            #Reiniciamos el contador de días que pueden trabajar esta semana
            self.diasLaborablesPendientes = self.scenario.diasLaborablesSemanales

    
    def avanceDiarioEspecifico(self):
        '''Método que simula el paso de un día a otro para los Trabajadores'''
        #Sólo participa en el funcionamiento de la simulación si está vivo
        if self.estado != self.scenario.estadoMuerto:

            #Si aún le quedan días por trabajar esta semana, el agente debe trabajar
            if(self.diasLaborablesPendientes > 0):
            
                #Elige la jornada laboral que más le convenga
                trabajado = self.elegirAccion(idxInf=self.idxTrabMin, idxSup=self.idxTrabMax)
                
                #Si no tenía recursos suficientes para hacerla, asiste al trabajo estandar obligado (simplemente se le ocupa aún más tiempo)
                if not trabajado:
                    self.trabajar(obligatorio=True)
                
                self.diasLaborablesPendientes -= 1      #Restamos en 1 la cantidad de días que puede trabajar el agente esta semana


    def step(self):
        '''Definimos lo que puede hacer cada agente en su tiempo libre'''
        
        #Sólo participa en el funcionamiento del modelo si está vivo
        if self.estado != self.scenario.estadoMuerto:

            self.actualizarVecinos()

            #Si el agente no está realizando ninguna otra acción, puede decidir qué hacer
            if self.estaDisponible():        

                self.elegirAccion()
                self.move()

            else:
                #Si el agente está ocupado, simplemente permanece inactivo durante esta hora
                self.ocupado -= 1.0

            #Antes de acabar el paso, si está muy feliz, contagia su felicidad a los agentes cercanos
            self.contagiarFelicidadTrabajador()
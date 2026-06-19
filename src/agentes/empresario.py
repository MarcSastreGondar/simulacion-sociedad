'''
Archivo en el que se define el comportamiento específico de todos los agentes de tipo Empresario, cuyo comportamiento se basa en acumular dinero
'''

#Importamos todos los métodos comunes entre los distintos tipos de agentes
from .agenteBase import AgenteBase


class Empresario(AgenteBase):
        
    
    def __init__(self, modelo):
        
        #Instanciamos las acciones específicas de su tipo que puede realizar
        accionesEmpresario = ["invertir", "bonificacionMonetaria"]

        #Llamamos al __init__ del agenteBase con los parámetros comunes entre todos los agentes
        super().__init__(modelo=modelo, dineroInicial=modelo.scenario.dineroInicialE, felicidadInicial=modelo.scenario.felicidadInicialE, accionesEspecificas=accionesEmpresario)

        self.tipo = "Empresario"

        self.reiniciarAgente()            #Instanciamos los valores que pueden llegar a ser reiniciados



    def reiniciarAgente(self, epsilon=None):
        '''Método que instancia las variables del Empresario con el valor por defecto, importante que el __init__ lo llame'''
        self.reiniciarAgenteGeneral(epsilon=epsilon)


    #Métodos auxiliares
    def contagiarFelicidadEmpresario(self):
        '''Método que, en caso de que un Empresario esté contento, pone de mejor humor a los demás Trabajadores que tenga cerca. No es una acción, simplemente ocurre de manera pasiva en cada step'''
        
        #Si está suficientemente feliz, contagia a los Trabajadores cercanos
        if self.comprobarTiempoEnergiaFelicidadDinero(felicidad=self.scenario.umbralContagiarFelicidadE):
            
            self.modificarVecinos(tipo="Trabajador", felicidad=self.scenario.felicidadContagiarE)


    def generacionPasivaDinero(self):
        '''Método que causa al Empresario ganar una cierta cantidad de dinero en función de la cantidad de Trabajadores que tiene cerca (lo que simula que trabajan para él)'''

        #Obtenemos los trabajadores cercanos
        trabajadoresCercanos = self.modificarVecinos(tipo="Trabajador")
        dineroGenerado = len(trabajadoresCercanos) * self.scenario.dineroPasivoPorTrabajador

        #Simplemente le añadimos el dinero que han generado pasivamente "sus" Trabajadores
        self.modificarEnergiaFelicidadDinero(dinero=dineroGenerado)



    #Acciones que sólo pueden realizar los Empresarios
    def invertir(self):
        '''Acción en la que el Empresario invierte y gana un porcentaje de su dinero'''

        #Si tiene el tiempo y la energía para invertir, lo hace
        if self.comprobarTiempoEnergiaFelicidadDinero(tiempo=self.scenario.tiempoInvertir, energia=self.scenario.energiaInvertir):

            aumentoDinero = self.scenario.porcentajeDineroInvertir * self.dinero        #El dinero que consigue dependerá del dinero que ya tenga el Empresario

            self.modificarEnergiaFelicidadDinero(felicidad=self.scenario.felicidadInvertir, energia=self.scenario.energiaInvertir, dinero=aumentoDinero)
            self.ocupar(self.scenario.tiempoInvertir)

            return True
        
        return False


    def bonificacionMonetaria(self):
        '''Acción en la que un Empresario da una bonificación monetaria a los Trabajadores cercanos para ponelos de mejor humor. O les paga a todos o a ninguno'''

        trabajadoresBeneficiados = []
            
        #Primero comprobamos cuantos Trabajadores hay cerca que tengan menos de una cierta cantidad de felicidad
        for agente in self.vecinos:
            if (agente.tipo == "Trabajador") and (agente.felicidad < self.scenario.umbralFelicidadBonificacionMonetaria):
                trabajadoresBeneficiados.append(agente)


        #Una vez obtenida la lista, comprobamos si el empresario tiene dinero suficiente para recompensar a los Trabajadores
        cantTrabajadores = len(trabajadoresBeneficiados)


        if cantTrabajadores > 0:

            #En caso de que la cantidad de Trabajadores supere el umbral máximo, bonificamos sólo a la cantidad máxima de Trabajadores
            if(cantTrabajadores > self.scenario.maxTrabajadoresBonificacion):
                cantTrabajadores = self.scenario.maxTrabajadoresBonificacion

            dineroTotalGastar = (-1) * cantTrabajadores * self.scenario.maxTrabajadoresBonificacion     #Por -1 porque representa un gasto

            if self.comprobarTiempoEnergiaFelicidadDinero(dinero=dineroTotalGastar):

                #En caso de tener dinero suficiente, el empresario lo gasta en bonificarles
                self.modificarEnergiaFelicidadDinero(dinero=dineroTotalGastar)
                self.ocupar(self.scenario.tiempoBonificacion)

                #Recorremos cada agente para darles el dinero a cada uno
                for agente in trabajadoresBeneficiados:
                    agente.modificarEnergiaFelicidadDinero(felicidad=agente.scenario.aumentoFelicidadTrabajadorBonificacion, dinero=agente.scenario.dineroPorTrabajadorBonificacion)

                    #Disminuimos el contador de Trabajadores restantes, en caso de haber acabado, salimos del bucle
                    cantTrabajadores -= 1
                    if cantTrabajadores <= 0:
                        break
                    
            else:
                #Si el Empresario no tiene recursos suficientes, devolvemos False
                return False
        
        #En caso de haber realizado la bonificación monetaria o de no haber Trabajadores cerca, devolvemos True
        return True


    #Métodos relacionados con el flujo de los agentes
    def avanceDiarioEspecifico(self):
        '''Método que simula el paso de un día a otro para los Empresarios'''
        
        #Sólo participa en el funcionamiento de la simulación si está vivo
        if self.estado != self.scenario.estadoMuerto:
        
            #Cada día obtiene dinero en función de los trabajadores que tiene cerca
            self.generacionPasivaDinero()


    def avanceSemanalEspecifico(self):
        '''Método que simula el paso de una semana a otra para los Empresarios'''
        
        #Sólo participa en el funcionamiento de la simulación si está vivo
        if self.estado != self.scenario.estadoMuerto:
            pass


    def step(self):

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
    
            #Antes de acabar el paso, si está muy feliz, contagia su felicidad a los Trabajadores cercanos
            self.contagiarFelicidadEmpresario()
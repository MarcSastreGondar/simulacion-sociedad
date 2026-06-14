'''
Archivo en el que se define el comportamiento específico de todos los agentes de tipo Empresario, cuyo comportamiento se basa en no querer trabajar y en aprovecharse y molestar a los demás
'''

#Importamos todos los métodos comunes entre los distintos tipos de agentes
from .agenteBase import AgenteBase


class Antisistema(AgenteBase):
        
    
    def __init__(self, modelo):

        #Instanciamos las acciones específicas de su tipo que puede realizar
        accionesAntisistema = ["atracar", "quejarse", "vandalismo"]

        #Llamamos al __init__ del agenteBase con los parámetros comunes entre todos los agentes
        super().__init__(modelo=modelo, dineroInicial=modelo.scenario.dineroInicialA, felicidadInicial=modelo.scenario.felicidadInicialA, accionesEspecificas=accionesAntisistema)
        
        self.tipo = "Antisistema"

        self.reiniciarAgente()            #Instanciamos los valores que pueden llegar a ser reiniciados


    def reiniciarAgente(self, epsilon=None):
        '''Método que instancia las variables del Antisistema con el valor por defecto, importante que el __init__ lo llame'''
        self.reiniciarAgenteGeneral(epsilon=epsilon)

        self.odioSocial = 0         #Cantidad de odio que sienten los demás miembros de la sociedad hacia él. Si tiene demasiado, se le expulsa de la sociedad



    #Métodos auxiliares
    def comprobarOdioSocial(self):
        '''Método que sirve para comprobar si el Antisistema es demasiado odiado, en cuyo caso es expulsado de la sociedad'''

        if self.odioSocial >= self.scenario.odioMaximo:

            self.eliminarAgente()


    def modificarOdioSocial(self, odio):
        '''Método para actualizar de manera controlada el valor del odio social'''

        self.odioSocial += odio

        #Comprobamos que el odioSocial no pase de los límites
        if self.odioSocial > self.scenario.odioMaximo:
            self.odioSocial = self.scenario.odioMaximo
        
        elif self.odioSocial < 0:
            self.odioSocial = 0


    def contagiarOdio(self):
        '''Método que consiste en que el Antisistema, en caso de no estar de buen humor, hace infelices a los agentes que tiene cerca. No es una acción, simplemente ocurre de manera pasiva en cada step'''

        #Si no está suficientemente feliz, contagia a los demás
        if self.felicidad <= self.scenario.umbralContagiarOdio:

            self.modificarVecinos(felicidad=self.scenario.felicidadContagiarA)      #Felicidad negativa


    #Acciones
    def atracar(self):
        '''Acción que representa que el Antisistema atraca a otro agente. Intenta robar a un Empresario, si no puede, intenta robar a un Trabajador'''
        
        #Comprobamos si el Antisistema tiene recursos suficientes para realizar la acción
        if self.comprobarTiempoEnergiaFelicidadDinero(self.scenario.energiaAtracar):

            #Obtenemos los Empresarios que puedan ser víctimas del atraco
            victimasPosibles = self.modificarVecinos(tipo="Empresario")

            #En caso de que no haya Empresarios, intentamos atracar a un Trabajador
            if len(victimasPosibles) <= 0:
                victimasPosibles = self.modificarVecinos(tipo="Trabajador")

            #Si hay Empresarios o Trabajadores cerca (con prioridad de los Empresarios), simplemente atracamos a uno cualquiera
            if len(victimasPosibles) > 0:

                indiceAleat = self.aleat.integers(0, len(victimasPosibles))
                victima = victimasPosibles[indiceAleat]
                dineroRobado = victima.dinero * self.scenario.porcentajeDineroRobado

                #Gastamos los recursos de la Víctima
                victima.modificarEnergiaFelicidadDinero(felicidad=self.scenario.felicidadAtracado, dinero=((-1) * dineroRobado))    #Multiplicamos por -1 para que le suponga un gasto

                #Modificamos los recursos del Antisistema
                self.modificarEnergiaFelicidadDinero(energia=self.scenario.energiaAtracar, felicidad=self.scenario.felicidadAtracar, dinero=dineroRobado)
                self.ocupar(self.scenario.tiempoAtracar)
                self.modificarOdioSocial(self.scenario.odioAtracar)     #Obtiene odio por ello

            return True     #Si tenía recursos suficientes como para atracar a gente, devolvemos True independientemente de si ha podido hacerlo o no

        #Si no tiene recursos para atracar a alguien, devolvemos False
        return False

    
    def quejarse(self):
        '''Acción de que el Antisistema transmita sus quejas sobre el sistema a los agentes que tenga cerca, molestándolos en el proceso'''

        #Comprobamos que tenga los recursos necesarios para realizar la acción
        if self.comprobarTiempoEnergiaFelicidadDinero(energia=self.scenario.energiaQuejarse, tiempo=self.scenario.tiempoQuejarse):
            
            #Reducimos la felicidad de todos los que lo escuchen
            self.modificarVecinos(felicidad=self.scenario.felicidadQuejarseReceptor)

            #Modificamos los recursos del Antisistema
            self.modificarEnergiaFelicidadDinero(energia=self.scenario.energiaQuejarse, felicidad=self.scenario.felicidadQuejarse)
            self.ocupar(self.scenario.tiempoQuejarse)
            self.modificarOdioSocial(self.scenario.odioQuejarse)        #Obtiene odio por ello

            return True
        
        return False    #Si no tiene recursos para quejarse, devolvemos False


    def vandalismo(self):
        '''Acción de romper, pintar o ensuciar propiedades de Empresarios con el fin de tener un impacto negativo sobre estos'''

        #Obtenemos la cantidad de empresarios a los que puede vandalizar
        empresariosVandalizados = self.modificarVecinos(tipo="Empresario")
        cantEmpresarios = len(empresariosVandalizados)

        #Si no tiene ningún empresario cerca, devolvemos True
        if cantEmpresarios == 0:
            return True
        
        
        while cantEmpresarios > 0:

            #Calculamos los recursos necesarios para vandalizar a esta cantidad de empresarios
            energiaReal = cantEmpresarios * self.scenario.energiaVandalismo
            tiempoReal = cantEmpresarios * self.scenario.tiempoVandalismo
            costeReal = cantEmpresarios * self.scenario.dineroVandalismo
            
            #Si tiene recursos suficientes, realiza la acción y salimos del bucle            
            if self.comprobarTiempoEnergiaFelicidadDinero(energia=energiaReal, tiempo=tiempoReal, dinero=costeReal):

                #Vandaliza los negocios de los empresarios que pueda, reduciendo sus recursos
                self.modificarVecinos(cantidadAgentes=cantEmpresarios, tipo="Empresario", felicidad=self.scenario.felicidadVandalismoEmpresario, dinero=self.scenario.dineroVandalismoEmpresario)

                #Actualizamos los recursos del Antisistema
                self.modificarEnergiaFelicidadDinero(energia=energiaReal, felicidad=self.scenario.felicidadVandalismo, dinero=costeReal)
                self.ocupar(tiempoReal)
                self.modificarOdioSocial(self.scenario.odioVandalismo)      #Obtiene odio por ello

                return True
            else:
                #Si no tiene recursos suficientes, intenta vandalizar a 1 empresario menos
                cantEmpresarios -= 1

        #Si no tiene recursos suficientes para vandalizar a algún empresario, devuelve False
        return False
        

    #Métodos relacionados con el flujo de los agentes
    def avanceDiarioEspecifico(self):
        '''Método que simula el paso de un día a otro para los Antisistema'''

        #Sólo participa en el funcionamiento de la simulación si está vivo
        if self.estado != self.scenario.estadoMuerto:
            pass


    def avanceSemanalEspecifico(self):
        '''Método que simula el paso de una semana a otra para los Antisistema'''

        #Sólo participa en el funcionamiento de la simulación si está vivo
        if self.estado != self.scenario.estadoMuerto:

            self.modificarOdioSocial(self.scenario.reduccionPasivaOdio)         #Con el paso del tiempo, los demás agentes van olvidando el odio hacia él


    def step(self):
        #Sólo participa en el funcionamiento de la simulación si está vivo
        if self.estado != self.scenario.estadoMuerto:

            #Comprobamos si el agente es demasiado odiado y debe ser expulsado de la sociedad
            self.comprobarOdioSocial()

            if self.estado == self.scenario.estadoMuerto:       #Si ha tenido que ser expulsado de la sociedad, no realiza ninguna acción
                return

            self.actualizarVecinos()


            #Si el agente no está realizando ninguna otra acción, puede decidir qué hacer
            if self.estaDisponible():            

                self.elegirAccion()
                self.move()

            else:
                #Si el agente está ocupado, simplemente permanece inactivo durante esta hora
                self.ocupado -= 1.0

            #Antes de acabar el paso, si no está feliz, contagia su infelicidad a los agentes cercanos
            self.contagiarOdio()
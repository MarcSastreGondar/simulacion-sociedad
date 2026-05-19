#¿?¿$"acs"   Agente que hereda de BaseAgent y representa a un rebelde, que (¡¡¡INCLUIR CÓMO SE COMPORTA!!!)
'''
gashfd
'''

#Importamos todos los métodos comunes entre los distintos tipos de agentes
from .agenteBase import AgenteBase


#Agente Antisistema, cuyo comportamiento se basa en no querer trabajar, aprovecharse de los demás y intentar causar revueltas
class Antisistema(AgenteBase):
        
    
    def __init__(self, modelo):
        #Instanciamos las acciones específicas de su tipo que puede realizar
        acciones_antisistema = ["atracar", "quejarse", "vandalismo"]

        # Llamamos al __init__ de BaseAgent con los parámetros comunes entre todos los agentes
        super().__init__(modelo=modelo, dineroInicial=modelo.scenario.dineroInicialA, felicidadInicial=modelo.scenario.felicidadInicialA, accionesEspecificas=acciones_antisistema)
        
        self.tipo = "Antisistema"

        self.reiniciar()            #Instanciamos los valores que pueden llegar a ser reiniciados


    def reiniciar(self):
        '''Método que instancia las variables del Antisistema con el valor por defecto'''
        self.reiniciarGeneral()

        self.odioSocial = 0         #Cantidad de odio que sienten los demás miembros de la sociedad hacia él. Si tiene demasiado, se le expulsa de la sociedad

    #Métodos auxiliares
    def comprobarOdioSocial(self):
        '''Método que sirve para comprobar si el Antisistema es demasiado odiado, en cuyo caso es expulsado de la sociedad'''

        if self.odioSocial >= self.scenario.odioMaximo:

            self.eliminarAgente()

    def modificarOdioSocial(self, odio):
        '''Método para actualizar de manera controlada el valor del odio social'''

        self.odioSocial += odio

        #Comprobamos que el odioSocial no pase de las fronteras
        if self.odioSocial > self.scenario.odioMaximo:
            self.odioSocial = self.scenario.odioMaximo
        
        elif self.odioSocial < 0:
            self.odioSocial = 0

    def contagiarOdio(self):
        '''Método que consiste en que el Antisistema, en caso de no estar de buen humor, hace infelices a los agentes que tiene cerca'''
        #Si no está suficientemente feliz, contagia a los demás
        if self.felicidad <= self.scenario.umbralContagiarOdio:

            self.modificarVecinos(felicidad=self.scenario.felicidadContagiarA)      #Felicidad negativa


    #Acciones
    def atracar(self):
        '''Acción que representa que el Antisistema atraca a otro agente. Intenta robar a 1 Empresario, si no puede, intenta robar a un Trabajador'''
        
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
                self.modificarOdioSocial(self.scenario.odioAtracar)

                return True

        #Si no se ha podido atracar a nadie, se devuelve False
        return False

    
    def quejarse(self):
        '''Acción de que el Antisistema transmita sus quejas sobre el sistema a los agentes que tenga cerca'''

        #Comprobamos que tenga los recursos necesarios para realizar la acción
        if self.comprobarTiempoEnergiaFelicidadDinero(energia=self.scenario.energiaQuejarse, tiempo=self.scenario.tiempoQuejarse):
            
            #Reducimos la felicidad de todos los que lo escuchen
            self.modificarVecinos(felicidad=self.scenario.felicidadQuejarseReceptor)

            #Modificamos los recursos del Antisistema
            self.modificarEnergiaFelicidadDinero(energia=self.scenario.energiaQuejarse, felicidad=self.scenario.felicidadQuejarse)
            self.ocupar(self.scenario.tiempoQuejarse)


    def vandalismo(self):
        '''Acción de romper, pintar o ensuciar propiedades de Empresarios con el fin de tener un impacto negativo sobre estos'''

        #Obtenemos la cantidad de empresarios a los que puede vandalizar
        empresariosVandalizados = self.modificarVecinos(tipo="Empresario")      #Recojemos los empresarios que serán vandalizados
        cantEmpresarios = len(empresariosVandalizados)

        while cantEmpresarios > 0:

            #Calculamos los recursos necesarios para vandalizar a esta cantidad de empresarios
            energiaReal = cantEmpresarios * self.scenario.energiaVandalismo
            tiempoReal = cantEmpresarios * self.scenario.tiempoVandalismo
            costeReal = cantEmpresarios * self.scenario.dineroVandalismo
            
            #Si tiene recursos suficientes, realiza la acción y salimos del bucle            
            if self.comprobarTiempoEnergiaFelicidadDinero(energia=energiaReal, tiempo=tiempoReal, dinero=costeReal):
                self.modificarVecinos(cantidadAgentes=cantEmpresarios, tipo="Empresario", felicidad=self.scenario.felicidadVandalismoEmpresario, dinero=self.scenario.dineroVandalismoEmpresario)

                #Actualizamos los recursos del Antisistema
                self.modificarEnergiaFelicidadDinero(energia=energiaReal, felicidad=self.scenario.felicidadVandalismo, dinero=costeReal)
                self.ocupar(tiempoReal)
                self.modificarOdioSocial(self.scenario.odioVandalismo)

                return True
            else:
                #Si no tiene recursos suficientes, intenta vandalizar a 1 empresario menos
                cantEmpresarios -= 1

        return False
        

    #Métodos relacionados con el flujo de los agentes
    def avanceDiarioEspecifico(self):
        '''Método que simula el paso de un día a otro para los Antisistema'''


    def avanceSemanalEspecifico(self):
        '''Método que simula el paso de una semana a otra para los Antisistema'''
        self.modificarOdioSocial(self.scenario.reduccionPasivaOdio)


    def step(self):
        #Sólo participa en el funcionamiento de la simulación si está vivo
        if self.estado != self.scenario.estadoMuerto:

            #Comprobamos si el agente es demasiado odiado
            self.comprobarOdioSocial()

            self.actualizarVecinos()

            #Si el agente no está realizando ninguna otra acción, puede decidir qué hacer
            if self.estaDisponible():            

                self.move()
                self.elegirAccion()

            else:
                #Si el agente está ocupado, simplemente permanece inactivo durante esta hora
                self.ocupado -= 1.0

            #Antes de acabar el paso, si no está feliz, contagia su infelicidad a los agentes cercanos
            self.contagiarOdio()
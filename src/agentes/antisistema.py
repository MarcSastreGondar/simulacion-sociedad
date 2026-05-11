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

        self.odioSocial = 0         #Cantidad de odio que sienten los demás miembros de la sociedad hacia él. Si tiene demasiado, se le expulsa de la sociedad


    #Métodos auxiliares
    def elegirAgentes(self):        #####NECESSARI???
        '''Método para elegir un vecino al que realizarle una acción'''

    def actualizarOdioSocial(self):
        '''Método que sirve para comprobar si el Antisistema es demasiado odiado, en cuyo caso es expulsado de la sociedad'''
        if self.odioSocial > self.scenario.maxOdio:
            self.eliminarAgente()

    def modificarOdioSocial(self, odio):
        '''Método para actualizar de manera controlada el valor del odio social'''
        self.odioSocial += odio

        #Comprobamos que el odioSocial no pase de las fronteras
        if self.odioSocial > self.scenario.odioMaximo:
            self.odioSocial = self.scenario.odioMaximo
        
        elif self.odioSocial < 0:
            self.odioSocial = 0


    #Acciones
    def atracar(self):#####
        '''Acción que representa que el Antisistema atraca a otro agente'''
    

    def quejarse(self):
        '''Acción de que el Antisistema transmita sus quejas sobre el sistema a los agentes que tenga cerca'''
        #Comprobamos que tenga los recursos necesarios para realizar la acción
        if self.comprobarEnergiaTiempoDinero(energia=self.scenario.energiaQuejarse, tiempo=self.scenario.tiempoQuejarse):
            
            #Reducimos la felicidad de todos los que lo escuchen
            self.modificarVecinos(felicidad=self.scenario.felicidadQuejarseReceptor)

            #Modificamos los recursos del Antisistema
            self.modificarEnergiaFelicidadDinero(energia=self.scenario.energiaQuejarse, felicidad=self.scenario.felicidadQuejarse)
            self.ocupar(self.scenario.tiempoQuejarse)

    
    def vandalismo(self):
        '''Acción de romper, pintar o ensuciar propiedades de Empresarios con el fin de tener un impacto negativo sobre estos'''
        #Obtenemos la cantidad de empresarios a los que puede vandalizar
        cantEmpresariosVandalizados = self.modificarVecinos(tipo="Empresario")      #Sólo recoje el contador
        
        while cantEmpresariosVandalizados > 0:

            #Calculamos los recursos necesarios para vandalizar a esta cantidad de empresarios
            energiaReal = cantEmpresariosVandalizados * self.scenario.energiaVandalismo
            tiempoReal = cantEmpresariosVandalizados * self.scenario.tiempoVandalismo
            costeReal = cantEmpresariosVandalizados * self.scenario.dineroVandalismo
            
            #Si tiene recursos suficientes, realiza la acción            
            if self.comprobarEnergiaTiempoDinero(energia=energiaReal, tiempo=tiempoReal, dinero= costeReal):

                self.modificarVecinos(tipo="Empresario", felicidad=self.scenario.felicidadVandalismoEmpresario, dinero=self.scenario.dineroVandalismoEmpresario)

                #Actualizamos los recursos del Antisistema
                self.modificarEnergiaFelicidadDinero(energia=energiaReal, felicidad=self.scenario.felicidadVandalismo, dinero=costeReal)
                self.ocupar(tiempoReal)
                self.modificarOdioSocial(self.scenario.odioVandalismo)

                ACABAR BUCLE
            else:
                #Si no tiene recursos suficientes, intenta vandalizar a 1 empresario menos
                cantEmpresariosVandalizados -= 1
        

    def step(self):
        self.actualizarOdioSocial()
        self.actualizarVecinos()
        self.move()

        self.actualizarDepresion()


    def avanceDiarioEspecifico(self):
        '''Método que simula el paso de un día a otro para los Antisistema'''

    def avanceSemanalEspecifico(self):
        '''Método que simula el paso de una semana a otra para los Antisistema'''

    def elegirAccion(self):
        """Método que define qué acciones puede tomar un Antisistema en un cierto momento"""
        print()
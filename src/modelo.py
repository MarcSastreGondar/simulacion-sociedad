#safr342? =?¿=?=?=! ?¿=·$"·$$?="=$~$!-.   Documento para la lógica principal de la simulación. Incluye todos los 
# parámetros configurables y la instanciación de prácticamente todo lo que se tenga que usar y
# y los métodos que calculen y modifiquen cosas generales del programa. Básicamente el documento main.
'''
gashfd
'''

import mesa
from mesa import Model

# Imports relativos desde el paquete src (recomendado)
from .agentes.trabajador import Trabajador
from .agentes.inversor import Inversor
from .agentes.rebelde import Rebelde


class ModeloSociedad(mesa.Model):
    """Modelo principal de la simulación"""
    
    def __init__(self, n_trabajadores=100, n_inversores=20, n_rebeldes=10, anchura=20, altura=20):
        super().__init__()

        # Creamos las casillas en las que pueden moverse los agentes
        self.grid = mesa.discrete_space.OrthogonalMooreGrid((anchura, altura), torus=True)  #torus = True para que los bordes del mapa están conectados entre sí

        self.agentes = list()

        # Creamos los agentes de cada tipo
        self.trabajadores = Trabajador.create_agents(self, n_trabajadores)
        self.inversores = Inversor.create_agents(self, n_inversores)
        self.rebeldes = Rebelde.create_agents(self, n_rebeldes)        

        # Agrupamos cada lista de agentes a una lista común
        self.agentes.append(self.trabajadores)
        self.agentes.append(self.inversores)
        self.agentes.append(self.rebeldes)

        # Recorremos cada agente de la lista de agentes y le asignamos una casilla aleatoria
        for listaAgentes in self.agentes:
            listaAgentes.cell = self.grid.all_cells.select_random_cell()

    def step(self):
        """Paso de tiempo de toda la simulación"""

        # Ejecutamos el step() de todos los agentes en orden aleatorio.
        for listaAgentes in self.agentes:
            listaAgentes.shuffle_do("step")

        
        
        #r325tr32t3"$!$·/y5764 4675346325 1212  Aquí puedes añadir lógica global # - Calcular Gini - Calcular grievance medio - Detectar si hay revueltas activas - Aplicar posibles redistribuciones, etc.
#Importamos el modelo principal
from .modeloSociedad import ModeloSociedad, EscenarioSociedad

#Importamos los distintos tipos de agentes
from .agentes.trabajador import Trabajador
from .agentes.empresario import Empresario
from .agentes.antisistema import Antisistema

#En caso de querer exportar todo
__all__ = [
    'ModeloSociedad',
    'EscenarioSociedad',
    'Antisistema',
    'Empresario',    
    'Trabajador',
]
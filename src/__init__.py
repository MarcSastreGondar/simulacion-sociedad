'''
Archivo para facilitar los imports del src desde el '.ipynb'.
'''

# Importamos el modelo principal
from .modelo import ModeloSociedad

# Importamos los distintos tipos de agentes
from .agentes.trabajador import Trabajador
from .agentes.empresario import Empresario
from .agentes.antisistema import Antisistema


# En caso de querer exportar todo
__all__ = [
    'ModeloSociedad',
    'Antisistema',
    'Empresario',    
    'Trabajador',
]


#2532532¿?¿''¡!   TAMBIÉN PUEDO HACER    from .archivo import *     para importar todos los métodos que tengo, ACTUALIZARLO después si en la versión final quiero 
                  #exportar cada método de dentro de alguno de los ficheros
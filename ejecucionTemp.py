import sys
from pathlib import Path

# Ruta relativa desde notebooks/ hasta la raíz del proyecto
project_root = Path.cwd().parent
sys.path.insert(0, str(project_root))

# Imports limpios gracias al __init__.py
from src import ModeloSociedad, Trabajador, Empresario, Antisistema

#from src import crear_visualizacion


from mesa.visualization import Slider

# Imports de métricas
#from src.metrics import calcular_gini, grievance_medio, detectar_revueltas_activas

# Parámetros de configuración de la simulación
#Tamaño del tablero en el que pueden estar los agentes
anchura = 20
altura = 20

#Semilla de la pseudoaleatoriedad para poder repetir resultados en las ejecuciones
semilla = 150


# Parámetros de configuración de los agentes en general
#Variables relacionadas con el tiempo del que dispone el agente para actuar cada día
tiempoMaxPosible = 24                                        #Tiempo en horas que el agente tiene disponibles en un dia
tiempoVital = 8                                              #Tiempo en horas que se utiliza en hacer acciones necesarias para la supervivencia (comida, higiene, etc.)

#Energia para realizar las acciones
energia = 100

#Cantidad de cada tipo de agente
cantTrabajadores = 100                  #Cantidad de trabajadores
cantEmpresarios = 20                    #Cantidad de empresarios
cantRebeldes = 10                       #Cantidad de rebeldes

porcentajeAleatorio = 0.5

# Parámetros de configuración de agentes específicos
#Trabajador
dineroInicialTrabajador = 500
insatisfaccionInicialTrabajador = 15

tiempoTrabajo = 8           #Horas que dedica a trabajar de manera directa
maxTiempoAlTrabajo = 1.5    #Cantidad máxima de tiempo en horas que puede tardar el agente en transportarse al trabajo (ida + vuelta)


#Empresario
dineroInicialEmpresario = 15000
insatisfaccionInicialEmpresario = 0


#Antisistema
dineroInicialAntisistema = 50
insatisfaccionInicialAntisistema = 50


parametrosModelo = {
    # Parámetros editables
    "n_trabajadores": Slider("Nº Trabajadores", cantTrabajadores, 10, 1000, 10),
    "n_empresarios": Slider("Nº Empresarios", cantEmpresarios, 1, 1000, 10),
    "n_rebeldes": Slider("Nº Rebeldes", cantRebeldes, 0, 1000, 10),
    "porcentajeAleatorio": Slider("Variabilidad Inicial", porcentajeAleatorio, 0.0, 1.0, 0.1),
    
    # Parámetros fijos
    "anchuraGrid": anchura,
    "alturaGrid": altura,
    "seed": semilla,
    "tiempoMaxPosible": tiempoMaxPosible,
    "tiempoVital": tiempoVital,
    "energia": energia,
    "dineroInicialT": dineroInicialTrabajador,
    "insatisfaccionInicialT": insatisfaccionInicialTrabajador,
    "tiempoTrabajo": tiempoTrabajo,
    "maxTiempoAlTrabajo": maxTiempoAlTrabajo,
    "dineroInicialE": dineroInicialEmpresario,
    "insatisfaccionInicialE": insatisfaccionInicialEmpresario,
    "dineroInicialA": dineroInicialAntisistema,
    "insatisfaccionInicialA": insatisfaccionInicialAntisistema
}


#Instanciamos la simulación
modeloSociedad = ModeloSociedad(n_trabajadores=cantTrabajadores, n_empresarios=cantEmpresarios, n_rebeldes=cantRebeldes, anchuraGrid=anchura, alturaGrid=altura, seed=semilla,
                                tiempoMaxPosible=tiempoMaxPosible, tiempoVital=tiempoVital, energia=energia, porcentajeAleatorio=porcentajeAleatorio,
                                dineroInicialT=dineroInicialTrabajador, insatisfaccionInicialT=insatisfaccionInicialTrabajador, tiempoTrabajo=tiempoTrabajo, maxTiempoAlTrabajo=maxTiempoAlTrabajo,
                                dineroInicialE=dineroInicialEmpresario, insatisfaccionInicialE=insatisfaccionInicialEmpresario,
                                dineroInicialA=dineroInicialAntisistema, insatisfaccionInicialA=insatisfaccionInicialAntisistema)



# visualizacion.py
"""
Componente de visualización usando SolaraViz directamente.
"""

from mesa.visualization import (
    SolaraViz,
    SpaceRenderer,
    make_plot_component,    
)
from mesa.visualization.components import AgentPortrayalStyle
from mesa.visualization.components import PropertyLayerStyle

def agent_portrayal(agent):
    # Determinamos color y tamaño según el tipo
    if agent.tipo == "Trabajador":
        color = "#1f77b4"
        size = 40
    elif agent.tipo == "Empresario":
        color = "#2ca02c"
        # Tamaño basado en riqueza (getattr evita errores si el atributo no existe aún)
        riqueza = getattr(agent, 'riqueza', 0)
        size = 50 + min(100, riqueza / 100)
    elif agent.tipo == "Antisistema":
        color = "#d62728"
        size = 60
    else:
        color = "#000000"
        size = 30

    size=200
    portrayal = AgentPortrayalStyle(color="blue", marker="^",size=200,x=agent.pos[0], y=agent.pos[1])
    portrayal.update("color", color)
    return portrayal
    
    return AgentPortrayalStyle(
        color=color,
        size=size,
        #marker="o",
        #zorder=10 if agent.tipo == "Antisistema" else 5
    )


#Función para quitar los bordes del gráfico de los agentes
def post_process(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.get_figure().set_size_inches(15, 15)


def propertylayer_portrayal(layer):
    return PropertyLayerStyle(color="lightblue", alpha=0.8, colorbar=False)


# Componentes
renderizador = SpaceRenderer(modeloSociedad, backend="matplotlib",).setup_agents(agent_portrayal)  
renderizador.draw_agents()

#Quitamos la leyenda del gráfico con los agentes
renderizador.post_process = post_process

renderizador.render()
graficoInsatisfaccionMedia = make_plot_component("Insatisfaccion_Media")


# Creamos y mostramos la visualización de la ejecución
page = SolaraViz(
        modeloSociedad,
        renderizador,
        components=[graficoInsatisfaccionMedia],
        model_params=parametrosModelo,
        name="Simulación Sociedad"
        )

page
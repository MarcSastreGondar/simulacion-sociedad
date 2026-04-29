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
    #portrayal = AgentPortrayalStyle(color="blue", marker="^",size=200,x=agent.pos[0], y=agent.pos[1])
    #portrayal.update("color", color)
    #return portrayal
    
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


def crear_visualizacion(modeloSociedad, parametrosModelo):
    # Componentes
    renderizador = SpaceRenderer(modeloSociedad, backend="matplotlib",).setup_agents(agent_portrayal)  
    renderizador.draw_agents()

    #Quitamos la leyenda del gráfico con los agentes
    renderizador.post_process = post_process

    renderizador.render()
    graficoInsatisfaccionMedia = make_plot_component("Insatisfaccion_Media")

    # Creamos y mostramos la visualización de la ejecución
    return SolaraViz(
            modeloSociedad,
            renderizador,
            components=[graficoInsatisfaccionMedia],
            model_params=parametrosModelo,
            name="Simulación Sociedad"
            )
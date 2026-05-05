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

    elif agent.tipo == "Antisistema":
        color = "#d62728"

    else:
        color = "#000000"

    
    return AgentPortrayalStyle(
        color=color,
        size=500,
        marker="o",
        edgecolors="black",
        linewidths=2
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
    graficoFelicidadMedia = make_plot_component("Felicidad_Media")

    # Creamos y mostramos la visualización de la ejecución
    return SolaraViz(
            modeloSociedad,
            renderizador,
            components=[graficoFelicidadMedia],
            model_params=parametrosModelo,
            name="Simulación Sociedad"
            )
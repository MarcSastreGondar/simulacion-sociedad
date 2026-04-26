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
        color = "gray"
        size = 30

    return AgentPortrayalStyle(
        color=color,
        size=size,
        marker="o",
        zorder=10 if agent.tipo == "Antisistema" else 5
    )



def crear_visualizacion(modeloSociedad, parametrosModelo):
    """
    modelo_clase: La clase del modelo (sin instanciar).
    model_params: Diccionario con Sliders y valores fijos.
    """
    # Componentes
    renderizador = SpaceRenderer(modeloSociedad, backend="matplotlib").setup_agents(agent_portrayal=agent_portrayal)
    renderizador.draw_agents()

    grafico = make_plot_component("Insatisfaccion_Media")
    grafico2 = make_plot_component("Insatisfaccion_Media")

    #Devolvemos la página
    return SolaraViz(
    model=modeloSociedad,
    renderer=renderizador,
    model_params=parametrosModelo,
    components=[grafico,grafico2],
    name="Simulación Sociedad"
)
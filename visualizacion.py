# visualizacion.py
"""
Componente de visualización SolaraViz.
"""

import solara
from mesa.visualization import SolaraViz, make_space_component, make_plot_component

def agent_portrayal(agent):
    if agent.tipo == "Trabajador":
        color = "#1f77b4"
        size = 7
    elif agent.tipo == "Empresario":
        color = "#2ca02c"
        size = 9 + min(15, getattr(agent, 'riqueza', 0) / 1200)
    elif agent.tipo == "Antisistema":
        color = "#d62728"
        size = 9
    else:
        color = "gray"
        size = 6

    alpha = 0.7 + (getattr(agent, 'insatisfaccion', 0) / 300)
    alpha = min(1.0, alpha)

    return {
        "color": color,
        "size": size,
        "alpha": alpha,
        "marker": "o",
        "zorder": 10 if getattr(agent, 'tipo', '') == "Antisistema" else 5
    }


space_component = make_space_component(agent_portrayal=agent_portrayal)
plot_insatisfaccion = make_plot_component("Insatisfaccion_Media")


@solara.component
def Visualizacion(model):
    """Componente SolaraViz que recibe un modelo ya instanciado."""
    return SolaraViz(
        model=model,
        model_params={},
        measures=[space_component, plot_insatisfaccion],
        name="Simulación de Sociedad",
        play_interval=160,
        height=920
    )
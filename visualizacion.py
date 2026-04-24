# visualizacion.py
"""
Componente de visualización usando SolaraViz directamente.
"""

from mesa.visualization import SolaraViz, make_space_component, make_plot_component

def agent_portrayal(agent):
    """Define cómo se dibuja cada agente en el grid."""
    if agent.tipo == "Trabajador":
        color = "#1f77b4"      # Azul
        size = 8
    elif agent.tipo == "Empresario":
        color = "#2ca02c"      # Verde
        size = 9 + min(15, getattr(agent, 'riqueza', 0) / 1200)
    elif agent.tipo == "Antisistema":
        color = "#d62728"      # Rojo
        size = 9
    else:
        color = "gray"
        size = 6

    # Opacidad según insatisfacción
    alpha = 0.7 + (getattr(agent, 'insatisfaccion', 0) / 300)
    alpha = min(1.0, alpha)

    return {
        "color": color,
        "size": size,
        "alpha": alpha,
        "marker": "o",
        "zorder": 10 if getattr(agent, 'tipo', '') == "Antisistema" else 5
    }


# Componentes
space_component = make_space_component(agent_portrayal=agent_portrayal)
plot_insatisfaccion = make_plot_component("Insatisfaccion_Media")


def crear_visualizacion(modelo):
    """Función que crea y devuelve la visualización SolaraViz."""
    return SolaraViz(
        model=modelo,
        model_params={},                    # No usamos sliders por ahora
        measures=[space_component, plot_insatisfaccion],
        name="Simulación de Sociedad",
        play_interval=180,                  # Velocidad de reproducción
        height=950                          # Altura grande
    )
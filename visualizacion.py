# visualizacion.py
"""
Aplicación web para visualizar la simulación.
Ejecutar con: solara run visualizacion.py
"""

import solara
from mesa.visualization import SolaraViz, make_space_component, make_plot_component

from src import ModeloSociedad


def agent_portrayal(agent):
    """Define cómo se dibuja cada agente."""
    if agent.tipo == "Trabajador":
        color = "#1f77b4"   # Azul
        size = 7
    elif agent.tipo == "Empresario":
        color = "#2ca02c"   # Verde
        size = 9 + min(15, getattr(agent, 'riqueza', 0) / 1200)
    elif agent.tipo == "Antisistema":
        color = "#d62728"   # Rojo
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


# Componentes visuales
space_component = make_space_component(agent_portrayal=agent_portrayal)
plot_insatisfaccion = make_plot_component("Insatisfaccion_Media")


# Parámetros ajustables en la interfaz
model_params = {
    "n_trabajadores": {"type": "SliderInt", "value": 120, "label": "Nº Trabajadores", "min": 50, "max": 500, "step": 10},
    "n_empresarios":  {"type": "SliderInt", "value": 30,  "label": "Nº Empresarios",   "min": 10, "max": 150, "step": 5},
    "n_rebeldes":     {"type": "SliderInt", "value": 20,  "label": "Nº Antisistema",   "min": 5,  "max": 120, "step": 5},
    "anchuraGrid":    {"type": "SliderInt", "value": 35,  "label": "Anchura Grid",     "min": 20, "max": 70, "step": 5},
    "alturaGrid":     {"type": "SliderInt", "value": 35,  "label": "Altura Grid",      "min": 20, "max": 70, "step": 5},
    "seed":           {"type": "SliderInt", "value": 42,  "label": "Semilla",          "min": 1,  "max": 9999, "step": 1},
}


# Crear la visualización
viz = SolaraViz(
    model_cls=ModeloSociedad,
    model_params=model_params,
    measures=[space_component, plot_insatisfaccion],
    name="Simulación de Sociedad - Desigualdad y Revueltas",
    play_interval=160,
    height=920
)


# Componente Solara (forma recomendada actualmente)
@solara.component
def Page():
    return viz


# Punto de entrada para solara run
if __name__ == "__main__":
    print("Iniciando visualización...")
    print("Abre tu navegador en: http://localhost:8765")
def propertylayer_portrayal(layer):
    return PropertyLayerStyle(color="lightblue", alpha=0.8, colorbar=False)

'''
'''

from mesa.visualization import (
    SolaraViz,
    SpaceRenderer,
    make_plot_component,
    Slider
)
from mesa.visualization.components import AgentPortrayalStyle, PropertyLayerStyle

from modeloSociedad import ModeloSociedad, EscenarioSociedad

# Definimos cómo se pintan los agentes
def agent_portrayal(agent):
    '''Define cómo se dibuja cada agente en la cuadrícula.'''
    # Determinamos color según el tipo
    if agent.tipo == "Trabajador":
        color = "#1f77b4"
    elif agent.tipo == "Empresario":
        color = "#2ca02c"
    elif agent.tipo == "Antisistema":
        color = "#d62728"
    else:
        color = "#000000"
    
    # Si el agente está muerto, se vuelve transparente
    opacidad = 1.0 
    if not agent.vivo:
        opacidad= 0.0

    return AgentPortrayalStyle(
        color=color,
        alpha=opacidad,
        size=500,
        marker="o",
        edgecolors="black",
        linewidths=2
    )

#Función para quitar los bordes del gráfico de los agentes
def post_process(ax):
    '''Limpia el gráfico de matplotlib eliminando ejes y ajustando tamaño.'''
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.get_figure().set_size_inches(15, 15)


# Instanciamos el escenario para obtener los valores por defecto
escenario = EscenarioSociedad()

parametrosModelo = {
    # Parámetros editables vía UI
    "n_trabajadores": Slider("Cantidad de Trabajadores", 10, 0, 1000, 10),
    "n_empresarios": Slider("Cantidad de Empresarios", 5, 0, 1000, 10),
    "n_antisistemas": Slider("Cantidad de Agentes Antisistema", 10, 0, 1000, 10),
    "visionAgente": Slider("Visión Agentes", escenario.visionAgente, 0, 20, 1),
    "porcentajeAleatorio": Slider("Variabilidad Inicial", escenario.porcentajeAleatorio, 0.0, 1.0, 0.1),
    
    # Parámetros fijos
    "anchuraGrid": escenario.anchuraGrid,
    "alturaGrid": escenario.alturaGrid,
    "rng": escenario.rng,
    "tiempoMaxPosible": escenario.tiempoMaxPosible,
    "tiempoVital": escenario.tiempoVital,
    "energiaMax": escenario.energiaMax,
    "energiaMaxObtenible": escenario.energiaMaxObtenible,
    "felicidadMax": escenario.felicidadMax,
    "umbralDepresion": escenario.umbralDepresion,
    "mesesSuicidio": escenario.mesesSuicidio,
    "movimientoAgente": escenario.movimientoAgente,
    "gastosDiarios": escenario.gastosDiarios,

    "dineroInicialT": escenario.dineroInicialT,
    "felicidadInicialT": escenario.felicidadInicialT,
    "tiempoTrabajo": escenario.tiempoTrabajo,
    "maxTiempoAlTrabajo": escenario.maxTiempoAlTrabajo,

    "dineroInicialE": escenario.dineroInicialE,
    "felicidadInicialE": escenario.felicidadInicialE,

    "dineroInicialA": escenario.dineroInicialA,
    "felicidadInicialA": escenario.felicidadInicialA,

    "horasMinimasDormir": escenario.horasMinimasDormir,
    "horasMaximasDormir": escenario.horasMaximasDormir,
    
    "energiaEntrenar": escenario.energiaEntrenar,
    "tiempoEntrenar": escenario.tiempoEntrenar,
    "cuotaGimnasio": escenario.cuotaGimnasio,
    "aumentoEnergiaMaxEntrenar": escenario.aumentoEnergiaMaxEntrenar,
    "aumentoFelicidadEntrenar": escenario.aumentoFelicidadEntrenar
}

# Instanciamos el modelo
modeloSociedad = ModeloSociedad(escenario=escenario)

# Configuramos el renderizador de espacio
renderizador = SpaceRenderer(modeloSociedad, backend="matplotlib").setup_agents(agent_portrayal)

renderizador.draw_agents()
renderizador.post_process = post_process

#Gráficos para enseñar la evolución de estadísticas
graficoFelicidadMedia = make_plot_component("Felicidad_Media")

# Lanzamos la visualización con SolaraViz
page = SolaraViz(
    modeloSociedad,
    renderizador,
    components=[graficoFelicidadMedia],
    model_params=parametrosModelo,
    name="Simulación Sociedad",
)

# Esto permite que solara reconozca el componente al ejecutar el archivo
page
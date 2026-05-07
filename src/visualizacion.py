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

#Obtenemos los valores variables (los que se actualizarán con los sliders)
n_trabajadores = 30
n_empresarios = 80
n_antisistemas = 100
visionAgente = escenario.visionAgente
porcentajeAleatorio = escenario.porcentajeAleatorio

escenario.n_trabajadores = n_trabajadores
escenario.n_empresarios = n_empresarios

print(n_trabajadores)


model_params = {
    # Parámetros editables en la interfaz gráfica
    "n_trabajadores": Slider("Cantidad de Trabajadores", n_trabajadores, 0, 1000, 10),
    "n_empresarios": Slider("Cantidad de Empresarios", n_empresarios, 0, 1000, 10),
    "n_antisistemas": Slider("Cantidad de Agentes Antisistema", n_antisistemas, 0, 1000, 10),
    "visionAgente": Slider("Visión Agentes", visionAgente, 0, 20, 1),
    "porcentajeAleatorio": Slider("Variabilidad Inicial", porcentajeAleatorio, 0.0, 1.0, 0.1),
    
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
print(n_trabajadores)
# Instanciamos el modelo
modeloSociedad = ModeloSociedad(cantTrabajadores=n_trabajadores,cantEmpresarios=n_empresarios, cantAntisistemas=n_antisistemas, escenario=escenario)

# Configuramos el renderizador de espacio
renderizador = SpaceRenderer(modeloSociedad, backend="matplotlib").setup_agents(agent_portrayal)

renderizador.draw_agents()
renderizador.post_process = post_process

#Gráficos para enseñar la evolución de estadísticas
graficoFelicidadMedia = make_plot_component("Felicidad_Media")

AVERIGUAR POR QUÉ NO SE PASAN LOS PARÁMETROS. A LO MEJOR COMPROBAR SI EN MI VERSIÓN ESA ANTIGUA SE MODIFICABAN LOS PARÁMETROS O NO (PERO MEJOR INTENTAR ARREGLAR ESTE APPROACH)
# Lanzamos la visualización con SolaraViz
page = SolaraViz(
    modeloSociedad,
    renderizador,
    components=[],#graficoFelicidadMedia],
    model_params=model_params,
    name="Simulación Sociedad",
)

# Esto permite que solara reconozca el componente al ejecutar el archivo
page
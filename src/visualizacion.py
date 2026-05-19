'''
'''

from mesa.visualization import (
    SolaraViz,
    SpaceRenderer,
    make_plot_component,
    Slider
)

import solara

from mesa.visualization.components import AgentPortrayalStyle, PropertyLayerStyle

from modeloSociedad import ModeloSociedad, EscenarioSociedad

# Definimos cómo se pintan los agentes
def agent_portrayal(agente):
    '''Define cómo se dibuja cada agente en la cuadrícula.'''
    # Determinamos color según el tipo
    if agente.tipo == "Trabajador":
        color = "#1f77b4"
    elif agente.tipo == "Empresario":
        color = "#2ca02c"
    elif agente.tipo == "Antisistema":
        color = "#d62728"
    else:
        color = "#000000"

    #Determinamos la opacidad dependiendo del estado en el que se encuentre el agente
    if agente.estado == agente.scenario.estadoFeliz:
        opacidad = 1.0
    elif agente.estado == agente.scenario.estadoDeprimido:
        opacidad = 0.6
    else:                   #Si está muerto, lo pintamos invisible
        opacidad = 0

    return AgentPortrayalStyle(
        color=color,
        alpha=opacidad,
        size=400,
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
    ax.get_figure().set_size_inches(13, 13)


def crearRenderizador(modelo) -> SpaceRenderer:
    '''Creamos y devolvemos el renderizador del modelo'''

    renderizador = SpaceRenderer(modelo, backend="matplotlib")
    renderizador.setup_agents(agent_portrayal)                      #Definimos cómo se pintarán los agentes
    renderizador.post_process = post_process                        #Ajustes de los ejes
    renderizador.draw_agents()

    return renderizador


def botonEntrenarAgentes(modelo):
    '''Botón para disparar el entrenamiento masivo episódico en segundo plano'''
    def clickEntrenar():

        print(f"\nEmpezando entrenamiento para {modelo.episodiosEntrenamiento} episodios...")
        modelo.entrenamientoAgentes()
        print("Entrenamiento finalizado. Ya se puede hacer una simulación con el conocimiento aprendido.")

    return solara.Button(label="Entrenar Agentes", on_click=clickEntrenar, color="success")

def botonExportarEntrenamiento(modelo):
    '''Botón para guardar exclusivamente la matriz de pesos del modelo RL en JSON.'''
    def clickExportarPesos():
        modelo.exportarPesosAgentes()

    return solara.Button(label=" Exportar Entrenamiento Agentes", on_click=clickExportarPesos, color="info")

def botonImportarEntrenamiento(modelo):
    '''Botón para forzar la inyección de matrices Q guardadas en el modelo.'''
    def clickImportar():
        modelo.importarDatos()

    return solara.Button(label="Importar Preentrenamiento de Agentes", on_click=clickImportar, color="secondary")


def botonExportarSimulacion(modelo):
    '''Botón para guardar exclusivamente los CSVs de métricas del DataCollector.'''
    def clickExportarMétricas():
        modelo.exportarDatosSimulacion()

    return solara.Button(label=" Exportar Datos Simulación Actual", on_click=clickExportarMétricas, color="primary")



# Instanciamos el escenario para obtener los valores por defecto
escenario = EscenarioSociedad()

#Obtenemos los valores por defecto de las variables (los que se actualizarán con los sliders)
n_trabajadores = escenario.n_trabajadores
n_empresarios = escenario.n_empresarios
n_antisistemas = escenario.n_antisistemas
porcentajeAleatorio = escenario.porcentajeAleatorio
episodiosEntrenamiento = escenario.episodiosEntrenamiento


#Definimos los parámetros que se utilizarán en las simulaciones
model_params = {
    # Parámetros editables en la interfaz gráfica
    "n_trabajadores": Slider("Cantidad de Trabajadores", n_trabajadores, 0, 1000, 10),
    "n_empresarios": Slider("Cantidad de Empresarios", n_empresarios, 0, 1000, 10),
    "n_antisistemas": Slider("Cantidad de Antisistema", n_antisistemas, 0, 1000, 10),
    "porcentajeAleatorio": Slider("Variabilidad Inicial", porcentajeAleatorio, 0.0, 1.0, 0.1),
    "episodiosEntrenamiento": Slider("Ciclos Entrenamiento", episodiosEntrenamiento, 10, 1000, 10),
    
    # Parámetros fijos
    "anchuraGrid": escenario.anchuraGrid,
    "alturaGrid": escenario.alturaGrid,
    "rng": escenario.rng,
    "estadoFeliz": escenario.estadoFeliz,
    "estadoDeprimido": escenario.estadoDeprimido,
    "estadoMuerto": escenario.estadoMuerto,
    "visionAgente": escenario.visionAgente,
    "tiempoMaxPosible": escenario.tiempoMaxPosible,
    "tiempoVital": escenario.tiempoVital,
    "energiaMax": escenario.energiaMax,
    "energiaMinObtenible": escenario.energiaMinObtenible,
    "energiaMaxObtenible": escenario.energiaMaxObtenible,
    "felicidadMax": escenario.felicidadMax,
    "umbralDepresion": escenario.umbralDepresion,
    "mesesSuicidio": escenario.mesesSuicidio,
    "reduccionDiariaFelicidad": escenario.reduccionDiariaFelicidad,
    "porcentajeGastosCuotidianos": escenario.porcentajeGastosCuotidianos,
    "gastosDiariosMin": escenario.gastosDiariosMin,
    "gastosDiariosMax": escenario.gastosDiariosMax,

    "movimientoAgente": escenario.movimientoAgente,
    "maxStepsCiclo": escenario.maxStepsCiclo,
    "alfaQ": escenario.alfaQ,
    "gammaQ": escenario.gammaQ,
    "epsilonQ": escenario.epsilonQ,
    "epsilonMinimo": escenario.epsilonMinimo,
    "porcentajeDineroRecompensa": escenario.porcentajeDineroRecompensa,
    "porcentajePocaEnergiaQ": escenario.porcentajePocaEnergiaQ,
    "porcentajeMediaEnergiaQ": escenario.porcentajeMediaEnergiaQ,
    "divisionPocoDinero": escenario.divisionPocoDinero,
    "multiplicacionMedioDinero": escenario.multiplicacionMedioDinero,

    "dineroInicialT": escenario.dineroInicialT,
    "felicidadInicialT": escenario.felicidadInicialT,
    "sueldoMinimo": escenario.sueldoMinimo,
    "sueldoMedio": escenario.sueldoMedio,
    "diasLaborablesSemanales": escenario.diasLaborablesSemanales,
    "diasLaborablesAlMes": escenario.diasLaborablesAlMes,
    
    "dineroInicialE": escenario.dineroInicialE,
    "felicidadInicialE": escenario.felicidadInicialE,
    
    "dineroInicialA": escenario.dineroInicialA,
    "felicidadInicialA": escenario.felicidadInicialA,
    "odioMaximo": escenario.odioMaximo,
    "reduccionPasivaOdio": escenario.reduccionPasivaOdio,

    "horasMinimasDormir": escenario.horasMinimasDormir,
    "horasMaximasDormir": escenario.horasMaximasDormir,
    "felicidadDormirMal": escenario.felicidadDormirMal,
    "felicidadDormirBien": escenario.felicidadDormirBien,
    "maxDormirPorDia": escenario.maxDormirPorDia,
    "energiaEntrenar": escenario.energiaEntrenar,
    "tiempoEntrenar": escenario.tiempoEntrenar,
    "cuotaGimnasio": escenario.cuotaGimnasio,
    "felicidadEntrenar": escenario.felicidadEntrenar,
    "aumentoEnergiaMaxEntrenar": escenario.aumentoEnergiaMaxEntrenar,
    "costeLujo": escenario.costeLujo,
    "felicidadLujo": escenario.felicidadLujo,
    "tiempoLujo": escenario.tiempoLujo,
    "energiaOcio": escenario.energiaOcio,
    "tiempoOcio": escenario.tiempoOcio,
    "costeOcio": escenario.costeOcio,
    "felicidadOcio": escenario.felicidadOcio,
    "energiaComidaBasura": escenario.energiaComidaBasura,
    "felicidadComidaBasura": escenario.felicidadComidaBasura,
    "maxComidasPorDia": escenario.maxComidasPorDia,
    "porcentajeAhorro": escenario.porcentajeAhorro,
    "reduccionEnergiaMaxComidaBasura": escenario.reduccionEnergiaMaxComidaBasura,

    "tiempoTrabajo": escenario.tiempoTrabajo,
    "maxTiempoAlTrabajo": escenario.maxTiempoAlTrabajo,
    "energiaTrabajar": escenario.energiaTrabajar,
    "felicidadTrabajar": escenario.felicidadTrabajar,
    "felicidadMaxTrabajar": escenario.felicidadMaxTrabajar,
    "energiaEstudiar": escenario.energiaEstudiar,
    "felicidadEstudiar": escenario.felicidadEstudiar,
    "costeEstudiar": escenario.costeEstudiar,
    "aumentoSueldoEstudiar": escenario.aumentoSueldoEstudiar,
    "aumentoFelicidadTrabajoEstudiar": escenario.aumentoFelicidadTrabajoEstudiar,
    "tiempoEstudiar": escenario.tiempoEstudiar,
    "reduccionEnergiaMaxDobleTrabajo": escenario.reduccionEnergiaMaxDobleTrabajo,
    "porcentajeSueldoTeletrabajo": escenario.porcentajeSueldoTeletrabajo,
    "porcentajeEnergiaTeletrabajo": escenario.porcentajeEnergiaTeletrabajo,
    "umbralContagiarFelicidadT": escenario.umbralContagiarFelicidadT,
    "felicidadContagiarT": escenario.felicidadContagiarT,

    "tiempoInvertir": escenario.tiempoInvertir,
    "energiaInvertir": escenario.energiaInvertir,
    "felicidadInvertir": escenario.felicidadInvertir,
    "porcentajeDineroInvertir": escenario.porcentajeDineroInvertir,
    "umbralFelicidadBonificacionMonetaria": escenario.umbralFelicidadBonificacionMonetaria,
    "dineroPorTrabajadorBonificacion": escenario.dineroPorTrabajadorBonificacion,
    "aumentoFelicidadTrabajadorBonificacion": escenario.aumentoFelicidadTrabajadorBonificacion,
    "tiempoBonificacion": escenario.tiempoBonificacion,
    "umbralContagiarFelicidadE": escenario.umbralContagiarFelicidadE,
    "felicidadContagiarE": escenario.felicidadContagiarE,
    "dineroPasivoPorTrabajador": escenario.dineroPasivoPorTrabajador,

    "porcentajeDineroRobado": escenario.porcentajeDineroRobado,
    "felicidadAtracado": escenario.felicidadAtracado,
    "tiempoAtracar": escenario.tiempoAtracar,
    "energiaAtracar": escenario.energiaAtracar,
    "felicidadAtracar": escenario.felicidadAtracar,
    "odioAtracar": escenario.odioAtracar,
    "felicidadQuejarse": escenario.felicidadQuejarse,
    "felicidadQuejarseReceptor": escenario.felicidadQuejarseReceptor,
    "energiaQuejarse": escenario.energiaQuejarse,
    "tiempoQuejarse": escenario.tiempoQuejarse,
    "felicidadVandalismo": escenario.felicidadVandalismo,
    "energiaVandalismo": escenario.energiaVandalismo,
    "dineroVandalismo": escenario.dineroVandalismo,
    "tiempoVandalismo": escenario.tiempoVandalismo,
    "odioVandalismo": escenario.odioVandalismo,
    "felicidadVandalismoEmpresario": escenario.felicidadVandalismoEmpresario,
    "dineroVandalismoEmpresario": escenario.dineroVandalismoEmpresario,
    "umbralContagiarOdio": escenario.umbralContagiarOdio,
    "felicidadContagiarA": escenario.felicidadContagiarA
}


# Instanciamos el modelo. Es vital para el correcto funcionamiento que el nombre de los parámetros que se pasen sea el mismo que el nombre de la variable que los recibe
modeloSociedad = ModeloSociedad(n_trabajadores=n_trabajadores,n_empresarios=n_empresarios, n_antisistemas=n_antisistemas, episodiosEntrenamiento=episodiosEntrenamiento)

#Gráficos para enseñar la evolución de estadísticas
#Gráficos generales
graficoFelicidadMedia = make_plot_component("Felicidad Media", page=1, backend="altair")
graficoEnergiaMedia = make_plot_component("Energia Media", page=1, backend="altair")
graficoDineroMedio = make_plot_component("Dinero Medio", page=1, backend="altair")

#Gráficos de los Trabajadores
graficoFelicidadMediaT = make_plot_component("Felicidad Media Trabajadores", page=2, backend="altair")
graficoEnergiaMediaT = make_plot_component("Energia Media Trabajadores", page=2, backend="altair")
graficoDineroMedioT = make_plot_component("Dinero Medio Trabajadores", page=2, backend="altair")

#Gráficos de los Empresarios
graficoFelicidadMediaE = make_plot_component("Felicidad Media Empresarios", page=3, backend="altair")
graficoEnergiaMediaE = make_plot_component("Energia Media Empresarios", page=3, backend="altair")
graficoDineroMedioE = make_plot_component("Dinero Medio Empresarios", page=3, backend="altair")

#Gráficos de los Antisistema
graficoFelicidadMediaA = make_plot_component("Felicidad Media Antisistema", page=4, backend="altair")
graficoEnergiaMediaA = make_plot_component("Energia Media Antisistema", page=4, backend="altair")
graficoDineroMedioA = make_plot_component("Dinero Medio Antisistema", page=4, backend="altair")

# Lanzamos la visualización con SolaraViz
page = SolaraViz(
    modeloSociedad,
    model_params=model_params,
    renderer=crearRenderizador(modeloSociedad),
    components=[
        botonEntrenarAgentes,
        botonExportarEntrenamiento,
        botonImportarEntrenamiento,
        botonExportarSimulacion,
        graficoFelicidadMedia, graficoEnergiaMedia, graficoDineroMedio,
        graficoFelicidadMediaT, graficoEnergiaMediaT, graficoDineroMedioT,
        graficoFelicidadMediaE, graficoEnergiaMediaE, graficoDineroMedioE,
        graficoFelicidadMediaA, graficoEnergiaMediaA, graficoDineroMedioA
    ],
    name="Simulación Sociedad"
)


page
'''
'''
import os

#Realizamos los imports de Mesa
from mesa.visualization import (
    SolaraViz,
    SpaceRenderer,
    make_plot_component,
    Slider
)

from mesa.visualization.components import AgentPortrayalStyle

import solara


from modeloSociedad import ModeloSociedad, EscenarioSociedad

# Definimos cómo se pintan los agentes
def agent_portrayal(agente):
    '''Define cómo se dibuja cada agente en la simulación'''

    #Cambimos su color según su tipo
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


def post_process(ax):
    '''Limpia el gráfico eliminando ejes innecesarios y ajustando el tamaño'''
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.get_figure().set_size_inches(13, 13)


def crearRenderizador(modelo) -> SpaceRenderer:
    '''Crea y devuelve el renderizador del modelo, que centraliza las distintas configuraciones de la visualización'''

    renderizador = SpaceRenderer(modelo, backend="matplotlib")
    renderizador.setup_agents(agent_portrayal)                      #Definimos cómo se pintarán los agentes
    renderizador.post_process = post_process                        #Ajustes de los ejes
    renderizador.draw_agents()

    return renderizador


#Creamos una variable reactiva global para almacenar el archivo para importar los pesos de los agentes seleccionado
archivoPesosSeleccionado = solara.reactive("")

def panelControl(modelo):
    '''Panel que contiene la visualización y control de los elementos encargados del entrenamiento, importación y exportación de este y
       la exportación de los datos de la simulación'''
    
    #Creamos las variables de estado que usaremos para transformar los botones para que representen visualmente que están realizando su acción
    ejecutandoEntrenamiento = solara.use_reactive(False)
    ejecutandoExportarPesos = solara.use_reactive(False)
    ejecutandoImportarPesos = solara.use_reactive(False)
    ejecutandoExportarSimulacion = solara.use_reactive(False)

    #Detectamos los archivos .json de la carpeta de resultados para poder importar las pesos a cargar
    rutaResultados = "../resultados"

    if os.path.exists(rutaResultados):

        #Filtramos los archivos JSON
        archivosPesosDisponibles = [f for f in os.listdir(rutaResultados) if f.endswith('.json')]

        #Los ordenamos alfabéticamente
        archivosPesosDisponibles.sort()
    else:
        archivosPesosDisponibles = []

    #Si el usuario no ha elegido ninguno manualmente, seleccionamos por defecto la última opción (la más reciente)
    if archivosPesosDisponibles and not archivoPesosSeleccionado.value:
        archivoPesosSeleccionado.value = archivosPesosDisponibles[-1]


    #Definimos las características y componentes del propio panel
    with solara.Card():
        with solara.Column(gap="16px"):  
            
            #Sección de entrenamiento de agentes
            #Botón Entrenar Agentes
            with solara.Column(gap="8px"):
                solara.Markdown("### Aprendizaje por Refuerzo")
                
                #Acción de clickar el botón
                def clickEntrenar():
                    ejecutandoEntrenamiento.set(True)
                    try:
                        print(f"\nEmpezando entrenamiento para {modelo.episodiosEntrenamiento} episodios.")
                        modelo.entrenamientoAgentes()
                        print("Entrenamiento finalizado. Ya se puede simular.")
                    finally:
                        ejecutandoEntrenamiento.set(False)

                #Características visuales
                solara.Button(
                    label="Entrenando agentes..." if ejecutandoEntrenamiento.value else "Entrenar Agentes desde Cero", 
                    on_click=clickEntrenar, 
                    color="success",
                    loading=ejecutandoEntrenamiento.value,
                    disabled=ejecutandoEntrenamiento.value
                )
                
            #Botón de exportar los pesos tras el entrenamiento
            with solara.Column(gap="8px"):

                #Acción al pulsar el botón
                def clickExportarPesos():
                    ejecutandoExportarPesos.set(True)
                    try:
                        pathArchivo = modelo.exportarPesosAgentes()
                        print(f"\nEntrenamiento de los agentes correctamente guardado en: {pathArchivo}")

                    finally:
                        ejecutandoExportarPesos.set(False)

                #Características visuales
                solara.Button(
                    label="Guardando JSON..." if ejecutandoExportarPesos.value else "Exportar Pesos Entrenamiento", 
                    on_click=clickExportarPesos, 
                    color="info",
                    loading=ejecutandoExportarPesos.value,
                    disabled=ejecutandoExportarPesos.value
                )

            solara.Markdown("---")      #Añadimos visualmente una separación

            #Botón de cargar los pesos de los agentes
            with solara.Column(gap="8px"):
                solara.Markdown("### Importar Pesos Entrenados anteriormente")
                
                if not archivosPesosDisponibles:
                    solara.Markdown("¡No se han detectado archivos de pesos en ../resultados! Puede crear alguno mediante el botón de 'ENTRENAR AGENTES DESDE CERO' seguido de pulsar el de 'EXPORTAR PESOS ENTRENAMIENTO'")
                else:
                    solara.Select(
                        label="Selecciona un archivo de pesos",
                        value=archivoPesosSeleccionado,
                        values=archivosPesosDisponibles
                    )
                    
                    #Acción al clickar sobre el botón
                    def clickImportar():
                        if archivoPesosSeleccionado.value:
                            ejecutandoImportarPesos.set(True)
                            try:
                                nombreArchivo = modelo.importarDatos(archivoPesosSeleccionado.value)
                                print(f"\nPesos preentrenados cargados con éxito desde {nombreArchivo}.")


                            finally:
                                ejecutandoImportarPesos.set(False)

                        #Control de errores
                        else:
                            print("¡Error: Ningún archivo seleccionado!")
                            
                    #Características visuales del botón
                    solara.Button(
                        label="Cargando pesos..." if ejecutandoImportarPesos.value else "Cargar pesos",
                        on_click=clickImportar,
                        color="success",  # ◄ Cambiado a verde (mismo color que el de entrenar)
                        loading=ejecutandoImportarPesos.value,
                        disabled=ejecutandoImportarPesos.value
                    )


            solara.Markdown("---")

            # Botón para exportar los datos de la simulación actual
            with solara.Column(gap="8px"):
                solara.Markdown("### Exportar datos de la Simulación Actual")
                
                #Accion al pulsar sobre el botón
                def clickExportarMetricas():
                    ejecutandoExportarSimulacion.set(True)
                    try:
                        modelo.exportarDatosSimulacion()
                    finally:
                        ejecutandoExportarSimulacion.set(False)

                #Características visuales del botón
                solara.Button(
                    label="Exportando CSVs..." if ejecutandoExportarSimulacion.value else "Exportar Datos", 
                    on_click=clickExportarMetricas, 
                    color="primary",
                    loading=ejecutandoExportarSimulacion.value,
                    disabled=ejecutandoExportarSimulacion.value
                )


#Instanciamos el escenario para obtener los valores de las variables
escenario = EscenarioSociedad()

#Obtenemos los valores por defecto de las variables que se actualizarán con los sliders
cantTrabajadores = escenario.cantTrabajadores
cantEmpresarios = escenario.cantEmpresarios
cantAntisistemas = escenario.cantAntisistemas
porcentajeAleatorio = escenario.porcentajeAleatorio
episodiosEntrenamiento = escenario.episodiosEntrenamiento

#####God

#Definimos los parámetros que se utilizarán en las simulaciones
model_params = {
    # Parámetros editables en la interfaz gráfica
    "cantTrabajadores": Slider("Cantidad de Trabajadores", cantTrabajadores, 0, 1000, 10),
    "cantEmpresarios": Slider("Cantidad de Empresarios", cantEmpresarios, 0, 1000, 10),
    "cantAntisistemas": Slider("Cantidad de Antisistema", cantAntisistemas, 0, 1000, 10),
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
    "maxStepsEpisodio": escenario.maxStepsEpisodio,
    "alfaQ": escenario.alfaQ,
    "gammaQ": escenario.gammaQ,
    "epsilonQ": escenario.epsilonQ,
    "epsilonMinimo": escenario.epsilonMinimo,
    "epsilonSimulacion": escenario.epsilonSimulacion,
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
modeloSociedad = ModeloSociedad(cantTrabajadores=cantTrabajadores,cantEmpresarios=cantEmpresarios, cantAntisistemas=cantAntisistemas, episodiosEntrenamiento=episodiosEntrenamiento)

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
        panelControl,
        graficoFelicidadMedia, graficoEnergiaMedia, graficoDineroMedio,
        graficoFelicidadMediaT, graficoEnergiaMediaT, graficoDineroMedioT,
        graficoFelicidadMediaE, graficoEnergiaMediaE, graficoDineroMedioE,
        graficoFelicidadMediaA, graficoEnergiaMediaA, graficoDineroMedioA
    ],
    name="Simulación Sociedad"
)


page
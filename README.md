Proyecto realizado por Marc Nadal Sastre Gondar a fecha de 31/05/2026

Prerrequisitos:
1. Tener Python ya instalado con la versión 3.12.10 (no se garantiza el funcionamiento correcto en otras versiones)
2. Tener instalado Visual Studio Code.

No se garantiza el correcto funcionamiento de la aplicación al ejecutarlo desde cualquier otro programa o usando versiones distintas a las mencionadas anteriormente.



Todos los comandos necesarios para crear y configurar el entorno virtual, el cual es necesario para poder ejecutar correctamente la aplicación, son los siguientes (ejecutarlos en orden):

1. Crear el entorno virtual:
python -m venv venv

2. Activar el entorno virtual:
·Windows:
venv\Scripts\activate

·Linux / macOS:
source venv/bin/activate

3. Actualizar pip a la versión más reciente:
python -m pip install --upgrade pip

4. Instalar todas las librerías necesarias:
pip install "mesa[rec]" numpy pandas matplotlib seaborn solara tqdm ipywidgets
pip install "starlette<0.46" --force-reinstall

5. Verificar que todas las librerías se instalaron correctamente:
pip list



Puede ser necesario seleccionar la versión 3.12.10 como Intérprete de Python en VS Code:
    1. Ctrl + Shift + P
    2. Seleccionar "Python: Select Interpreter"
    3. Seleccionar el venv que hemos creado   



Cómo usar este entorno después de crearlo y cómo ejecutar la aplicación:
1. Activar el venv:
venv\Scripts\activate     # Windows
source venv/bin/activate  # Linux / macOS:

2. Ejecutamos la simulación:
cd src
solara run .\visualizacion.py

3. Dentro de la simulación:
    3.1 

4. En el notebooks/...:
    4.1 Abrir el archivo
    4.2 Pulsar el botón de "Select Kernel" y elegir el venv que hemos creado
    4.3 Pulsar el botón de "Restart Kernel" y darle al botón de "Run All" 



Durante el desarrollo de la aplicación, se han detectado varios problemas que han sido imposibles de arreglar y por ende, problemas que hay que tener en cuenta, los cuales son:

    1. A veces, cuando el play interval es demasiado pequeño, al pausar y, posteriormente, reanudar la ejecución, el programa algunas veces tiene problemas al actualizar variables necesarias para la ejecución y da un error

    2. Al ejecutar los entrenamientos, no se reinicia correctamente de manera visual el contador de los Steps. No afecta al funcionamiento del programa pero, en caso de molestar, simplemente exportar los Pesos del Entrenamiento, pulsar el botón de "Reset" y cargar los Pesos del Entrenamiento.

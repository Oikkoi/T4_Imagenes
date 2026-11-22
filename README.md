# T4
## Funcionamiento general:
Cada pregunta, por separado, guarda los resultados de sus ejecuciones dentro de `Resultados/`, que se creará en medida que se realicen ejecuciones. Esta carpeta se ramifica en `P1/` y `P2/`, donde los distintos resultados se nombran en base a sus parámetros de ejecución.
## Requisitos de ejecución:
1. Debe existir la carpeta `files/` con los archivos `belgium.hdr`, `belgium.tif`, `bigFogMap.tif`, `cathedral.tif`, `HDR.fit`, `memorial.hdr` y `memorial.tif` en la misma carpeta que `PX.py`/`PX_exp.py`
2. Deben estar instaladas las librerías señaladas en **Librerías usadas**
# `auxiliares.py`
Archivo que contiene funciones auxiliares.
## Funciones incluidas:
1. `cargar_imagen(nombre: str, normalizar: bool = True)`: Función que recibe el string con el nombre del archivo objetivo (importante: en `files/`) y retorna el array (que puede estar normalizado según el parámetro *`normalizar`* de la función). Utiliza `cv2.imread` para casi todas las imágenes. Las de extensión **.fit** son tratadas con **astropy**. Se extraen los datos, se hacen las transposiciones correspondientes para que queden en formato (alto, ancho, dimensiones). Las imágenes **.fit** también se importan invertidas en el eje horizontal, por lo que se usa *`np.flipud`* para orientarla como la imagen original. Todas las imágenes son convertidas a un array de tipo **float64** para maximizar la presición. La conversión de **float32** será hecha solo de ser necesario
2. `visualizar(img: np.array, correccion_gamma: bool = True, cmap="gray", vmin=None, vmax=None)`:
la función recibe el array original, si se desea añadir corrección gamma para mejor visualización en el monitor y solicita valores para el mapa de visualización (por defecto en gris, ya que si la imagen tiene 3 dimensiones (es decir, no es gris) `plt.imshow()` usa un cmap correspondiente.) También al poner los valores de `vmin` y `vmax` en **None**, no se 'clipean' los valores.
3. `guardar_imagen(img: np.array, nombre_archivo: str, cmap="gray", vmin=None, vmax=None)`:
Tal como su nombre indica, guarda un array de numpy como una imagen visible de nombre **nombre_archivo** (como parámetro de la función). Al igual que en `visualizar()`, se asignan valores default para el `cmap`, `vmin` y `vmax` por si la imagen fuese en grayscale.

# P1 (`P1.py`, `P1_exp.py`)
## `P1.py`
## `P1_exp.py`
## Funciones importadas de las cápsulas:
### Semana XX:
- asd

# P2 (`P2.py`, `P2_exp.py`)
## `P2.py`
## `P2_exp.py`
## Funciones importadas de las cápsulas:
### Semana 12:
- asd
# Librerías usadas:
### Para matemática:
1. Numpy
2. Scipy
### Importar/transformar imágenes
3. OpenCV-Python
4. astropy
### Visualización
5. Matplotlib
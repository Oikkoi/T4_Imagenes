# T4
## Funcionamiento general:
Cada pregunta, por separado, guarda los resultados de sus ejecuciones dentro de `Resultados/`, que se creará en medida que se realicen ejecuciones. Esta carpeta se ramifica según el archivo que se ejecute (`P2/` para `P2.py`, `P2_exp/` para `P2_exp.py`, y análogo para las demás preguntas), donde los distintos resultados se nombran en base a sus parámetros de ejecución. Dentro de `P2_exp/`, cada experimento tiene su propia subcarpeta (`exp1/`, `exp2/` y `exp3/`).
## Requisitos de ejecución:
1. Debe existir la carpeta `files/` con los archivos `belgium.hdr`, `belgium.tif`, `bigFogMap.tif`, `cathedral.tif`, `HDR.fit`, `memorial.hdr` y `memorial.tif` en la misma carpeta que `PX.py`/`PX_exp.py`. Para la pregunta 2 se usan `bigFogMap.tif` y `memorial.hdr`.
2. Deben estar instaladas las librerías señaladas en **Librerías usadas**.

# `auxiliares.py`
Archivo que contiene funciones auxiliares. Define la variable de entorno `OPENCV_IO_ENABLE_HDR` antes de importar `cv2`, para poder leer archivos `.hdr`.
## Funciones incluidas:
1. `cargar_imagen(nombre: str, normalizar: bool = False, override_ruta=None)`: Recibe el string con el nombre del archivo objetivo (importante: en `files/`) y retorna el array de la imagen. Si se entrega `override_ruta`, busca el archivo en esa carpeta en lugar de `files/` y muestra la ruta por consola. Si el archivo no existe, levanta un **ValueError**. Utiliza `cv2.imread` con `cv2.IMREAD_UNCHANGED` para casi todas las imágenes, de modo que se conserve el rango original (por ejemplo, el de un `.hdr`); si la imagen tiene tres dimensiones, se queda con los tres primeros canales y los invierte para pasar de BGR a RGB. Las de extensión **.fit** son tratadas con **astropy**: se extraen los datos, se hacen las transposiciones correspondientes para que queden en formato (alto, ancho, canales) y se usa `np.flipud` para orientarla como la imagen original. Todas las imágenes son convertidas a **float64** con `np.asarray` para maximizar la precisión, y los `nan` y los infinitos se reemplazan por 0 con `np.nan_to_num`. Si `normalizar` es `True`, se divide por el máximo y se corta a [0, 1] con `np.clip`.
2. `visualizar(img: np.array, correccion_gamma: bool = True, cmap="gray", vmin=None, vmax=None)`: Recibe el array original, si se desea añadir corrección gamma (`img ** (1/2.2)`, sobre una copia) para mejor visualización en el monitor, y los valores para el mapa de visualización (por defecto en gris, ya que si la imagen tiene 3 dimensiones `plt.imshow()` ignora el `cmap`). También, al dejar `vmin` y `vmax` en **None**, no se 'clipean' los valores. Muestra la imagen con `matplotlib` y no retorna nada.
3. `calcular_ruta_guardado(nombre_archivo: str, ruta_adicional: str = None)`: Obtiene con `os.path.basename` el nombre del archivo que se está ejecutando (usando `__main__`) y le quita la extensión; ese nombre es la carpeta de destino dentro de `Resultados/`. Si se entrega `ruta_adicional`, se agrega como una subcarpeta más. Crea las carpetas con `os.makedirs` (con `exist_ok=True`) y retorna la ruta completa del archivo.
4. `guardar_imagen(img: np.array, nombre_archivo: str, cmap="gray", vmin=None, vmax=None, ruta_adicional: str = None)`: Tal como su nombre indica, guarda un array de numpy como una imagen visible de nombre **nombre_archivo**, en la ruta que entrega `calcular_ruta_guardado`. Si la imagen tiene 3 dimensiones, se corta a [0, 1] con `np.clip` (sobre una copia). Se guarda con `plt.imsave`. Al igual que en `visualizar()`, se asignan valores default para el `cmap`, `vmin` y `vmax` por si la imagen fuese en grayscale.
5. `log(texto: str, reiniciar: bool = False)`: Escribe el texto, con un salto de línea, en el archivo `log.md` de la carpeta del script que se está ejecutando (ruta de `calcular_ruta_guardado`), y además lo muestra por consola. Abre el archivo en modo agregar o, si `reiniciar` es `True`, lo sobrescribe.
## Uso:
No está pensado para ejecutarse directamente, sino para ser importado. Sin embargo, al final del archivo (desde la línea 86) hay un bloque de prueba que carga `HDR.fit`, `memorial.tif` y `belgium.hdr`, las guarda como `test_0.png`, `test_1.png` y `test_2.png` y las muestra con `visualizar()`.

# P2 (`P2.py`, `P2_exp.py`)
**Para hacer esta pregunta, fueron utilizadas las librerías `numpy`, `matplotlib` y `cv2`, junto con las funciones de `auxiliares.py`.**
## `P2.py`
Contiene los dos métodos de compresión de rango dinámico (adaptados de las cápsulas, ver más abajo) y las dos estrategias de reconstrucción de color. Se definieron las siguientes funciones propias:
1. `separar_canales(imagen_rgb: np.array)`: Recibe la imagen RGB y retorna los canales R, G y B por separado.
2. `unir_colores(R_filtrado: np.array, G_filtrado: np.array, B_filtrado: np.array)`: Recibe los tres canales y los une con `np.stack` en el último eje. Retorna la imagen RGB.
3. `filtrar_colores(imagen_rgb: np.array)`: Llama a `separar_canales` y aplica `filtro_homomorfico` y `durand` a cada canal por separado. Luego une los canales con `unir_colores` y reescala el resultado con `reescalar`. Retorna la imagen homomórfica y la de Durand. Son las imágenes de comparación que pide el enunciado.
4. `aplicar_homo_durand(canal_2D: np.array)`: Recibe un canal 2D y retorna, en ese orden, el resultado del filtro homomórfico y el del método de Durand.
5. `crominancia_por_canales(imagen_rgb: np.array, beta: float, e: float = 1e-12, clip: bool = True)`: Es la **estrategia 1** (razón de luminancia). Obtiene la luminancia Y con `extraer_luminancia` y las luminancias comprimidas Y' con `aplicar_homo_durand`. Luego, para cada Y' (primero la homomórfica y después la de Durand) y para cada canal C, calcula `C' = Y' * (C / (Y + e)) ** beta` y une los tres canales. Si `clip` es `True`, corta la imagen a [0, 1] con `np.clip`. Antes de cortar, escribe en el log el porcentaje de valores mayores a 1 y el porcentaje de píxeles con al menos un canal mayor a 1. Es un generador, por lo que entrega una imagen por cada método.
6. `estrategia_1(nombre_imagen: str, beta: float, ruta=None)`: Carga la imagen con `cargar_imagen` y llama a `crominancia_por_canales`. Luego aplica gamma 1/2.2 a ambos resultados y los guarda como `{imagen}_homomorfico_beta_{beta}.png` y `{imagen}_durand_beta_{beta}.png`, en la subcarpeta `ruta`. Retorna ambas imágenes (sin gamma).
7. `estrategia_2(nombre_imagen: str, alfa: float, ruta=None)`: Es la **estrategia 2** (ajuste del croma C* en CIELCh). Llama a `crominancia_por_canales` con `beta = 1` y `clip = False`, les aplica gamma 1/2.2 y guarda las imágenes de referencia como `{imagen}_referencia_homomorfica_beta_1.png` y `{imagen}_referencia_durand_beta_1.png`. Luego, para cada una, usa `cv2.cvtColor` con `cv2.COLOR_RGB2Lab` y separa `L`, `a` y `b` con `cv2.split`. Calcula el croma como `np.hypot(a, b) * alfa` y el tono como `np.arctan2(b, a)`, por lo que con `alfa = 1` la transformación es la identidad. Reconstruye `a' = C cos(h)` y `b' = C sin(h)`, junta `L`, `a'` y `b'` con `cv2.merge` y vuelve a RGB con `cv2.COLOR_Lab2RGB`. Antes de cortar, escribe en el log el porcentaje de valores fuera de [0, 1] (bajo 0 y sobre 1) y el de píxeles con distorsión por el corte. Finalmente corta con `np.clip` y guarda `{imagen}_{homomorfico|durand}_cielch_c_{alfa}.png`.
### Uso:
Se puede ejecutar el archivo directamente. Al final del archivo (desde la línea 230) se encuentra el bloque ejecutable. Para cada imagen de la tupla `imagenes`, compara la reconstrucción de `crominancia_por_canales` con `beta = 1` contra el resultado de `filtrar_colores`, para ambos métodos, usando `mostrar` con `correccion_gamma=True`. Los experimentos que generan las figuras del informe están en `P2_exp.py`.

## `P2_exp.py`
Ejecuta los tres experimentos de la pregunta 2. Los parámetros de los filtros homomórfico y de Durand se mantienen fijos, con los valores base de `P2.py`. Se definieron las siguientes funciones:
1. `exp1(parametros: tuple)`: Para cada `beta` y cada imagen llama a `estrategia_1`. Guarda `{imagen}_homomorfico_beta_{beta}.png` y `{imagen}_durand_beta_{beta}.png` en `Resultados/P2_exp/exp1/`. Se usaron `betas = (0.6, 1, 1.4)`: uno que reduce la saturación relativa, la referencia y uno que la aumenta.
2. `comparacion_exp2()`: Carga desde `Resultados/P2_exp/exp2/` la referencia (`beta = 1`) y las tres versiones con distinto `alfa` de cada método, para cada imagen, y las divide por 255. Luego llama a `mostrar` para formar una figura por método, con cuatro paneles (Referencia, alfa = 0.2, alfa = 1 y alfa = 1.8). Las guarda como `comparativa_{imagen}_comparacion_homomorfica.png` y `comparativa_{imagen}_comparacion_durand.png`, en `Resultados/P2_exp/`.
3. `exp2(parametros: tuple)`: Para cada `alfa` y cada imagen llama a `estrategia_2`, que guarda en `Resultados/P2_exp/exp2/` las referencias y las imágenes `{imagen}_{método}_cielch_c_{alfa}.png`. Al terminar llama a `comparacion_exp2`. Se usaron `alfas = (0.2, 1, 1.8)`, donde `1` es la identidad.
4. `croma_tono(img_rgb: np.array)`: Recibe una imagen sRGB en [0, 1]. La convierte a Lab con `cv2.cvtColor` (en `float32`) y retorna el croma `C* = np.hypot(a, b)` y el tono `h = np.arctan2(b, a)` en radianes, ambos píxel a píxel.
5. `diferencia_tono(h1: np.array, h2: np.array)`: Calcula la diferencia con `np.arctan2(np.sin(h1 - h2), np.cos(h1 - h2))`, para que quede entre -π y π y no haya saltos en el cruce entre 0° y 360°. Retorna el promedio del valor absoluto, en grados.
6. `cuantificar_color(etiqueta: str, og: np.array, est1: np.array, est2: np.array, beta: float, alfa: float)`: Recibe una etiqueta, el recorte de la imagen original, los recortes de la estrategia 1 y de la estrategia 2, y los valores de `beta` y `alfa` usados. Llama a `croma_tono` y `diferencia_tono` y escribe en el log dos líneas: el C* medio del recorte (original, estrategia 1 y estrategia 2) y el cambio de tono medio respecto a la original (estrategia 1 y estrategia 2). Las medidas se calculan sobre el recorte, no sobre la imagen completa.
7. `exp3(parametros: tuple)`: Para cada imagen calcula la original para visualizar (`reescalar(imagen) ** (1/2.2)`) y la luminancia comprimida de cada método con gamma 1/2.2. Luego, para cada método (`homomorfico` y `durand`), carga y divide por 255 las imágenes de su caso principal desde `exp1/` y `exp2/`. Con `mostrar` forma una figura de cuatro paneles (original, luminancia comprimida, estrategia 1 y estrategia 2), con `vmin = 0`, `vmax = 1` y los parámetros en los títulos, y la guarda como `comparativa_{imagen}_{método}_comparativa.png`. Repite la figura sobre cada uno de los dos recortes de la imagen (primero el de colores intensos y después el de transición de iluminación) y las guarda como `comparativa_{imagen}_{método}_recorte_1.png` y `comparativa_{imagen}_{método}_recorte_2.png`. Finalmente llama a `cuantificar_color` con cada recorte. Todo se guarda en `Resultados/P2_exp/exp3/`. **Requiere haber ejecutado antes los experimentos 1 y 2** con los valores de `beta` y `alfa` de los casos principales.
### Uso:
Se puede ejecutar el archivo directamente. Pide por consola el número del experimento: `1`, `2` o `3` para ejecutar uno solo, o `0` para ejecutar los tres en orden. Cualquier otro valor levanta un error.

Al final del archivo (desde la línea 181) se encuentran los parámetros modificables, agrupados por experimento en el diccionario `parametros`, siendo estos `imagenes`, `betas`, `alfas`, `recortes`, `casos_principales` y `ruta`.

`imagenes` es una tupla con los nombres (con su extensión) de las imágenes dentro de `files/`. Ejemplo: `("bigFogMap.tif", "memorial.hdr")`.

`betas` (experimento 1) y `alfas` (experimento 2) son tuplas con los valores a probar. Ejemplo: `(0.6, 1, 1.4)`.

`ruta` es el nombre de la subcarpeta de `Resultados/P2_exp/` donde se guarda cada experimento (`exp1`, `exp2` o `exp3`).

`recortes` (experimento 3) es un diccionario con las dos zonas de cada imagen, en formato `(nombre, (slice_filas, slice_columnas))`. La primera es de colores intensos y la segunda de transición fuerte de iluminación. Los usados son:
- `bigFogMap`: `colores intensos` en `[130:330, 230:430]` (follaje) y `transición fuerte` en `[270:470, 400:600]` (foco de luz, hojas y niebla).
- `memorial`: `vitrales / color` en `[430:560, 250:430]` (vitrales) y `borde luz/sombra` en `[70:220, 90:260]` (rosetón contra la cúpula oscura).

`casos_principales` (experimento 3) es el par `(beta, alfa)` que se muestra para cada método. Los usados son `(1.4, 1.8)` para el homomórfico y `(1, 1)` para Durand.
### Reproducción de las figuras del informe:
Con las imágenes en `files/`, se ejecuta `P2_exp.py` y se ingresa `0` (o `1`, `2` y `3`, en ese orden). Las imágenes quedan en `Resultados/P2_exp/exp1`, `exp2` y `exp3` (las comparaciones de `comparacion_exp2` quedan en `Resultados/P2_exp/`). Los porcentajes de clipping y las medidas de C* y de tono quedan en `Resultados/P2_exp/log.md`.

El archivo `log.md` se reinicia al comienzo de cada experimento, por lo que al ejecutar los tres seguidos solo queda el log del experimento 3. Para conservar los otros dos, hay que ejecutarlos por separado y guardar el archivo antes de continuar.

## Funciones importadas de las cápsulas:
### Semana 12:
Usadas en `P2.py`, con los parámetros base de las cápsulas.
- `extraer_luminancia(E)`: Retorna la luminancia Y como `0.177 R + 0.813 G + 0.011 B` (la fila Y de la matriz RGB a XYZ de la cápsula de espacios de color).
- `reescalar(g, p_bajo=0.5, p_alto=99.5)`: Lleva los percentiles `p_bajo` y `p_alto` (calculados con `np.percentile`) a 0 y 1, y corta con `np.clip` lo que quede fuera de [0, 1].
- `mostrar(imgs, titulos, cmap='gray', ncols=None, size=4, vmin=None, vmax=None, marco=False, correccion_gamma=False, nombre_guardado=None, log: bool = True, ruta_adicional=None)`: Crea con `matplotlib` una figura con todas las imágenes (en `ncols` columnas y paneles de tamaño `size`). Si `correccion_gamma` es `True`, aplica gamma 1/2.2 a cada imagen. `vmin` y `vmax` fijan una misma escala para todos los paneles. Si se entrega `nombre_guardado`, guarda la figura con `guardar_imagen` como `comparativa_{nombre_guardado}.png`, dentro de la subcarpeta `ruta_adicional` (parámetro agregado para ordenar las figuras por experimento). El argumento `log` indica si se escriben mensajes en el log.
- `H_homomorfico(forma, gamma_H=1.5, gamma_L=0.5, D0=30, c=1.0)`: Calcula con `np.mgrid` la distancia de cada punto al centro del espectro y retorna el filtro gaussiano `(gamma_H - gamma_L) * (1 - exp(-c * D^2 / D0^2)) + gamma_L`.
- `filtro_homomorfico(f, gamma_H=1.5, gamma_L=0.5, D0=30, c=1.0, eps=1e-6)`: Calcula el logaritmo de `f + eps` y lo extiende al doble de tamaño con `np.pad` en modo `symmetric`, para evitar artefactos en los bordes. Luego calcula la transformada con `np.fft.fft2` y `np.fft.fftshift`, la multiplica por `H_homomorfico` y vuelve al dominio espacial con `np.fft.ifft2`, quedándose con la parte real y recortando al tamaño original. Finalmente aplica `np.exp` y reescala con `reescalar`.
- `durand(f, sigma_s=None, sigma_r=0.4, contraste=30, filtro='bilateral', e=1e-12)`: Calcula `np.log10` de `f + e` y obtiene la capa base con `cv2.bilateralFilter`, usando `sigma_r` como `sigmaColor` y `sigma_s = 0.02 * max(f.shape)` (si no se entrega) como `sigmaSpace`. El detalle es la diferencia entre el logaritmo y la base. Luego comprime solo la base con el factor `k = log10(contraste) / (base.max() - base.min())`, reconstruye `10 ** (k * (base - base.max()) + detalle)` y reescala con `reescalar`. También acepta `filtro='gauss'`, pero no fue utilizado.

# Librerías usadas:
### Para matemática:
1. Numpy
2. Scipy
### Importar/transformar imágenes
3. OpenCV-Python
4. astropy
### Visualización
5. Matplotlib
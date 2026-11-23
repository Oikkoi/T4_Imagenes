import numpy as np
import __main__
import matplotlib.pyplot as plt
from astropy.io import fits
import os
os.environ["OPENCV_IO_ENABLE_HDR"] = "1"
import cv2  # noqa: E402  # isort: skip


def cargar_imagen(nombre: str, normalizar: bool = False, override_ruta=None):
    ruta = os.path.join(os.path.dirname(__file__), "files", nombre)
    if override_ruta:
        ruta = os.path.join(override_ruta, nombre)
        print(ruta)

    if not os.path.isfile(ruta):
        raise ValueError("No existe la imagen")

    if (".fit" in nombre.lower()) or (".fits" in nombre.lower()):
        with fits.open(ruta) as hdul:
            datos = hdul[0].data
        if datos is None:
            raise ValueError("El archivo está vacío")
        datos = np.transpose(datos, (1, 2, 0))
        datos = np.flipud(datos)
    else:
        datos = cv2.imread(ruta, cv2.IMREAD_UNCHANGED)
        if datos is None:
            raise ValueError(f"OpenCV no pudo decodificar: {ruta}")
        if datos.ndim == 3:
            datos = datos[..., :3][..., ::-1]
    imagen = np.asarray(datos, dtype=np.float64)
    imagen = np.nan_to_num(imagen, nan=0, posinf=0, neginf=0)
    if normalizar:
        imagen /= np.max(imagen)
        imagen = np.clip(imagen, 0, 1)
    print("Imagen cargada")
    return imagen


def visualizar(img: np.array, correccion_gamma: bool = True, cmap="gray", vmin=None, vmax=None):
    alto, ancho = img.shape[:2]
    fig, ax = plt.subplots(1, 1, figsize=(5.0, 5.0 * (alto / ancho)))
    if correccion_gamma:
        img = (img.copy()) ** (1/2.2)
    im = ax.imshow(img, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.axis("off")
    plt.tight_layout()
    plt.show()
    return


def calcular_ruta_guardado(nombre_archivo: str, ruta_adicional: str = None):
    file_name = os.path.basename(getattr(__main__, "__file__", ""))
    carpeta_exacta = file_name.split(".")[0]
    ruta_destino = os.path.join(
        os.path.dirname(__file__), "Resultados", carpeta_exacta
    )
    if ruta_adicional is not None:
        ruta_destino = os.path.join(ruta_destino, ruta_adicional)

    os.makedirs(ruta_destino, exist_ok=True)
    return os.path.join(ruta_destino, nombre_archivo)


def guardar_imagen(img: np.array, nombre_archivo: str, cmap="gray", vmin=None, vmax=None, ruta_adicional: str = None):
    img_copia = img.copy()
    if img_copia.ndim == 3:
        img_copia = np.clip(img_copia, 0, 1)
    ruta_completa = calcular_ruta_guardado(nombre_archivo, ruta_adicional)
    plt.imsave(ruta_completa, img_copia, cmap=cmap, vmin=vmin, vmax=vmax)
    return


def log(texto: str, reiniciar: bool = False):
    ruta_log = calcular_ruta_guardado("log.md")
    modo = "a"
    if reiniciar:
        modo = "w"
    with open(ruta_log, modo, encoding='utf-8') as f:
        f.write(texto + "\n")
    print(texto)
    return


if __name__ == "__main__":
    imagenes = ("HDR.fit", "memorial.tif", "belgium.hdr")
    for k, name in enumerate(imagenes):
        imagen = cargar_imagen(name)
        guardar_imagen(imagen, f"test_{str(k)}.png")
        visualizar(imagen)

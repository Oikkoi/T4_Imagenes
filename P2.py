import os
import numpy as np
import matplotlib.pyplot as plt

# ↓Línea para configurar cv2 y que pueda leer HDR
os.environ["OPENCV_IO_ENABLE_HDR"] = "1"
import cv2  # noqa: E402  # isort: skip

from auxiliares import cargar_imagen, visualizar, guardar_imagen, log  # noqa: #402

# Funciones importadas de la semana 12 de las cápsulas de código:


def extraer_luminancia(E):
    # Fila Y de la matriz RGB -> XYZ usada en la cápsula de espacios de color
    log("Terminada la extracción de luminancia")
    return 0.177 * E[..., 0] + 0.813 * E[..., 1] + 0.011 * E[..., 2]


def reescalar(g, p_bajo=0.5, p_alto=99.5):
    # Lleva los percentiles p_bajo y p_alto a 0 y 1, recortando los extremos
    lo, hi = np.percentile(g, [p_bajo, p_alto])
    return np.clip((g - lo) / (hi - lo), 0.0, 1.0)


def mostrar(imgs, titulos, cmap='gray', ncols=None, size=4, vmin=None, vmax=None, marco=False, correccion_gamma=False):
    log("iniciando función de visualización *mostrar*")
    if correccion_gamma:
        imgs = [np.clip(img, 0, None) ** (1/2.2) for img in imgs]
    n = len(imgs)
    ncols = ncols or n
    nrows = int(np.ceil(n / ncols))
    cmaps = cmap if isinstance(cmap, list) else [cmap] * n

    fig, axes = plt.subplots(
        nrows, ncols, figsize=(size * ncols, size * nrows))
    axes = np.atleast_1d(axes).ravel()
    for ax, img, titulo, cm in zip(axes, imgs, titulos, cmaps):
        ax.imshow(img, cmap=cm, vmin=vmin, vmax=vmax)
        ax.set_title(titulo)
    for ax in axes:
        if marco:
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            ax.axis('off')
    plt.tight_layout()
    plt.show()
    log(
        f"Finaliza la visualización del conjunto de {str(n)} imagenes")


def H_homomorfico(forma, gamma_H=1.5, gamma_L=0.5, D0=30, c=1.0):
    P, Q = forma
    v, u = np.mgrid[0:P, 0:Q]
    D2 = (u - Q / 2) ** 2 + (v - P / 2) ** 2
    return (gamma_H - gamma_L) * (1 - np.exp(-c * D2 / D0 ** 2)) + gamma_L


def filtro_homomorfico(f, gamma_H=1.5, gamma_L=0.5, D0=30, c=1.0, eps=1e-6):
    log("Inicio aplicación del filtro homomorfico")
    N, M = f.shape
    z = np.log(f + eps)
    z_pad = np.pad(z, ((0, N), (0, M)), mode='symmetric')
    H = H_homomorfico(z_pad.shape, gamma_H, gamma_L, D0, c)

    S = H * np.fft.fftshift(np.fft.fft2(z_pad))
    s = np.fft.ifft2(np.fft.ifftshift(S)).real[:N, :M]
    log("filtro homomorfico reescalado a [0, 1] aplicado")
    return reescalar(np.exp(s))


def durand(f, sigma_s=None, sigma_r=0.4, contraste=30, filtro='bilateral', e=1e-12):
    log("Inicio aplicación filtro de durand")
    # Recibe un canal 2D (luminancia Y, R, G o B por separado)
    logf = np.log10(f + e).astype(np.float32)
    if sigma_s is None:
        sigma_s = 0.02 * max(f.shape)

    if filtro == 'bilateral':
        base = cv2.bilateralFilter(
            logf, d=-1, sigmaColor=sigma_r, sigmaSpace=sigma_s)
    else:
        base = cv2.GaussianBlur(logf, (0, 0), sigma_s)
    detalle = logf - base

    k = np.log10(contraste) / (base.max() - base.min())
    L_out = 10 ** (k * (base - base.max()) + detalle)
    log("fin aplicación filtro de duran reescalado [0, 1]")
    return reescalar(L_out.astype(np.float64))


# Mi código

def separar_canales(imagen_rgb: np.array):
    R = imagen_rgb[:, :, 0]
    G = imagen_rgb[:, :, 1]
    B = imagen_rgb[:, :, 2]
    log("canales R G B de la imagen separados")
    return R, G, B


def unir_colores(R_filtrado: np.array, G_filtrado: np.array, B_filtrado: np.array):
    rgb_filtrada = np.stack([R_filtrado, G_filtrado, B_filtrado], axis=-1)
    log("Canales RGB unidos en una imagen")
    return rgb_filtrada


def filtrar_colores(imagen_rgb: np.array):
    log("iniciando aplicación del filtro de Durand y Homomórfico a la imagen")
    R, G, B = separar_canales(imagen_rgb)

    R_homomorfico = filtro_homomorfico(R)
    G_homomorfico = filtro_homomorfico(G)
    B_homomorfico = filtro_homomorfico(B)
    rgb_homomorfica = reescalar(unir_colores(
        R_homomorfico, G_homomorfico, B_homomorfico))
    print("Creada la imagen homomórfica por canal")

    R_durand = durand(R)
    G_durand = durand(G)
    B_durand = durand(B)
    rgb_durant = reescalar(unir_colores(R_durand, G_durand, B_durand))
    print("Creada la imagen durand por canal")
    log("Ambos filtros aplicados con éxito")
    return rgb_homomorfica, rgb_durant


def aplicar_homo_durand(canal_2D: np.array):
    durandeado = durand(canal_2D)
    homomorfico = filtro_homomorfico(canal_2D)
    return homomorfico, durandeado


def crominancia_por_canales(imagen_rgb: np.array, beta: float, e: float = 1e-12):
    log(
        f"## Iniciando aplicación de filtro de Durand y Homomótfico a los canales por separado")
    log(f"## 𝛽 = {str(beta)}")
    Y = extraer_luminancia(imagen_rgb)
    Y_homo, Y_durand = aplicar_homo_durand(Y)
    Y_primas = (Y_homo, Y_durand)
    R, G, B = separar_canales(imagen_rgb)
    nombres = ("homomorfica", "durand")
    for k, Y_prima in enumerate(Y_primas):
        print(f"Iniciando iteración de {nombres[k]}")
        croma_R = R / (Y + e)
        R_prima = Y_prima * (croma_R)**beta
        croma_G = G / (Y + e)
        G_prima = Y_prima * (croma_G)**beta
        croma_B = B / (Y + e)
        B_prima = Y_prima * (croma_B)**beta
        imagen_hecha = unir_colores(R_prima, G_prima, B_prima)
        imagen_clip = np.clip(imagen_hecha.copy(), 0, 1)
        log(
            f"Porcentaje de pixeles cortados por el clip [0, 1]: {np.mean(imagen_hecha > 1.0) * 100}")
        log(
            f"Píxeles con distorsión por el clip [0, 1]: {np.mean(np.any(imagen_hecha > 1.0, axis=-1)) * 100}")
        yield imagen_clip
    log("Aplicados ambos filtros a la imagen")


def estrategia_1(nombre_imagen: str, beta: float, ruta=None):
    log(f"## Iniciando trabajo para {nombre_imagen + "\n"}")
    imagen_rgb = cargar_imagen(nombre_imagen)
    crominancia_homo, crominancia_durand = crominancia_por_canales(
        imagen_rgb, beta)
    guardar_imagen(
        crominancia_homo**(1/2.2), f"{nombre_imagen.split(".")[0]}_homomorfico_beta_{str(beta)}.png", ruta_adicional=ruta)
    log(
        f"Guardada {nombre_imagen.split(".")[0]}_homomorfico_beta_{str(beta)}.png con gamma aplicado")
    guardar_imagen(crominancia_durand**(1/2.2),
                   f"{nombre_imagen.split(".")[0]}_durand_beta_{str(beta)}.png", ruta_adicional=ruta)
    log(
        f"Guardada {nombre_imagen.split(".")[0]}_durand_beta_{str(beta)}.png con gamma aplicado")

    log(f"{"\n"*2}")
    return crominancia_homo, crominancia_durand


def estrategia_2(nombre_imagen: str, beta: float, ruta=None):
    log(f"## Iniciando trabajo para {nombre_imagen}, 𝛽 = {str(beta)} \n")
    homo, durand = estrategia_1(
        nombre_imagen, 1, os.path.join(ruta, "crominancia"))
    homo = (homo**(1/2.2)).astype(np.float32)
    durand = (durand**(1/2.2)).astype(np.float32)
    homo_lab = cv2.cvtColor(homo, cv2.COLOR_RGB2Lab)
    durand_lab = cv2.cvtColor(durand, cv2.COLOR_RGB2Lab)

    for img_lab, tipo in ((homo_lab, "homomorfico"), (durand_lab, "durand")):
        L, a, b = cv2.split(img_lab)
        C = np.hypot(a, b) * beta
        h = np.arctan2(b, a)
        a_prima = C * np.cos(h)
        b_prima = C * np.sin(h)
        img_lab_prima = cv2.merge([L, a_prima, b_prima]).astype(np.float32)
        img_rgb_prima = cv2.cvtColor(img_lab_prima, cv2.COLOR_Lab2RGB)
        fuera_rango = (img_rgb_prima < 0.0) | (img_rgb_prima > 1.0)
        log(
            f"[{tipo} | C*={str(beta)}] Valores fuera de [0, 1]: {np.mean(fuera_rango) * 100:.4f}% "
            f"(bajo 0: {np.mean(img_rgb_prima < 0.0) * 100:.4f}%, "
            f"sobre 1: {np.mean(img_rgb_prima > 1.0) * 100:.4f}%)"
        )
        log(
            f"[{tipo} | C*={str(beta)}] Píxeles con distorsión por clip: "
            f"{np.mean(np.any(fuera_rango, axis=-1)) * 100:.4f}%"
        )
        img_clip = np.clip(img_rgb_prima, 0.0, 1.0)
        nombre_salida = f"{nombre_imagen.split(".")[0]}_{tipo}_cielch_c_{str(beta)}.png"
        guardar_imagen(img_clip, nombre_salida,
                       ruta_adicional=os.path.join(ruta, "CIELab"))
        log(f"Guardada {nombre_salida} (ya en espacio sRGB)")
    log("\n")


if __name__ == "__main__":
    log("", True)  # Ping reset
    imagenes = ("bigFogMap.tif", "memorial.hdr")
    for nombre_imagen in imagenes:
        log(f"# Iniciando trabajo para {nombre_imagen + "\n"*2}")
        imagen_rgb = cargar_imagen(nombre_imagen)
        crominancia_homo, crominancia_durand = crominancia_por_canales(
            imagen_rgb, 1)
        directo_homo, directo_durand = filtrar_colores(imagen_rgb)
        mostrar([crominancia_homo, directo_homo], [
                "homomorfica por crominancia", "homomorfica directo con filtrar_colores()"], correccion_gamma=True)
        mostrar([crominancia_durand, directo_durand], [
                "durand por crominancia", "durand directo con filtrar_colores()"], correccion_gamma=True)

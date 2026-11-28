import os
import numpy as np
import cv2
from P2 import (
    estrategia_1,
    estrategia_2,
    mostrar,
    extraer_luminancia,
    aplicar_homo_durand,
    reescalar,
)
from auxiliares import log, cargar_imagen, guardar_imagen


# Exp 1: Probar valores de 𝛽:
def exp1(parametros: tuple):
    imagenes = parametros["imagenes"]
    betas = parametros["betas"]
    ruta_adicional = parametros["ruta"]
    log("", True)  # Ping Reset
    log("# Experimento 1 - Pregunta 2:")
    for beta in betas:
        for imagen in imagenes:
            estrategia_1(imagen, beta, ruta_adicional)
    return


def comparacion_exp2():
    ruta = os.path.join(os.path.dirname(__file__),
                        "Resultados", "P2_exp", "exp2")
    imagenes = {
        "bigFogMap": (
            (
                "bigFogMap_durand_cielch_c_0.2.png",
                "bigFogMap_durand_cielch_c_1.png",
                "bigFogMap_durand_cielch_c_1.8.png"
            ),
            (
                "bigFogMap_homomorfico_cielch_c_0.2.png",
                "bigFogMap_homomorfico_cielch_c_1.png",
                "bigFogMap_homomorfico_cielch_c_1.8.png"
            )),
        "memorial": (
            (
                "memorial_durand_cielch_c_0.2.png",
                "memorial_durand_cielch_c_1.png",
                "memorial_durand_cielch_c_1.8.png"
            ),
            (
                "memorial_homomorfico_cielch_c_0.2.png",
                "memorial_homomorfico_cielch_c_1.png",
                "memorial_homomorfico_cielch_c_1.8.png"
            ))
    }
    for key in imagenes:
        referencia_homo = f"{key}_referencia_homomorfica_beta_1.png"
        referencia_homo = (cargar_imagen(
            referencia_homo, override_ruta=ruta))/255.0
        referencia_durand = f"{key}_referencia_durand_beta_1.png"
        referencia_durand = (cargar_imagen(
            referencia_durand, override_ruta=ruta))/255.0
        (durand_02, durand_1, durand_18), (homo_02,
                                           homo_1, homo_18) = imagenes[key]

        durand_02 = (cargar_imagen(durand_02, override_ruta=ruta))/255.0
        durand_1 = (cargar_imagen(durand_1, override_ruta=ruta))/255.0
        durand_18 = (cargar_imagen(durand_18, override_ruta=ruta))/255.0

        homo_02 = (cargar_imagen(homo_02, override_ruta=ruta))/255.0
        homo_1 = (cargar_imagen(homo_1, override_ruta=ruta))/255.0
        homo_18 = (cargar_imagen(homo_18, override_ruta=ruta))/255.0

        imgs_durand = (referencia_durand, durand_02, durand_1, durand_18)
        imgs_homo = (referencia_homo, homo_02, homo_1, homo_18)
        titulos = ("Referencia", "alfa = 0.2", "alfa = 1", "alfa = 1.8")
        mostrar(imgs_homo, titulos,
                nombre_guardado=f"{key}_comparacion_homomorfica", log=False, ruta_adicional="exp2")
        mostrar(imgs_durand, titulos,
                nombre_guardado=f"{key}_comparacion_durand", log=False, ruta_adicional="exp2")

    return


# Exp2: probar estrategia 2 con distintos valores de saturación de color (valores alfa)
def exp2(parametros: tuple):
    # str imagenes, multiplicadores para C*, ruta extra para el guardado
    imagenes = parametros["imagenes"]
    alfas = parametros["alfas"]
    ruta_adicional = parametros["ruta"]
    log("", True)
    log("# Experimento 2 - Pregunta 2:")
    for alfa in alfas:
        for imagen in imagenes:
            estrategia_2(imagen, alfa, ruta_adicional)
    comparacion_exp2()
    return


def croma_tono(img_rgb: np.array):
    lab = cv2.cvtColor(img_rgb.astype(np.float32), cv2.COLOR_RGB2Lab)
    L, a, b = cv2.split(lab)
    return np.hypot(a, b), np.arctan2(b, a)


def diferencia_tono(h1: np.array, h2: np.array):
    dif = np.arctan2(np.sin(h1 - h2), np.cos(h1 - h2))
    return np.degrees(np.abs(dif)).mean()


def cuantificar_color(etiqueta: str, og: np.array, est1: np.array, est2: np.array, beta: float, alfa: float):
    C_og, h_og = croma_tono(og)
    C_1, h_1 = croma_tono(est1)
    C_2, h_2 = croma_tono(est2)
    log(f"[{etiqueta}] C* medio: original {C_og.mean():.2f}, "
        f"β={beta} {C_1.mean():.2f}, alfa = {alfa} {C_2.mean():.2f}")
    log(f"[{etiqueta}] Cambio de tono medio: "
        f"β={beta} {diferencia_tono(h_og, h_1):.2f}°, "
        f"alfa = {alfa} {diferencia_tono(h_og, h_2):.2f}°")


# Exp 3: Mostrar og, luminancia comprimida y reconstrucciones en color
def exp3(parametros: tuple):
    ruta_global = os.path.join(os.path.dirname(
        __file__), "Resultados", "P2_exp")
    ruta_exp1 = os.path.join(ruta_global, "exp1")
    ruta_exp2 = os.path.join(ruta_global, "exp2")
    imagenes = parametros["imagenes"]
    recortes = parametros["recortes"]
    casos_principales = parametros["casos_principales"]
    ruta_adicional = parametros["ruta"]
    log("", True)
    log("# Experimento 3 - Pregunta 2:")
    for imagen in imagenes:
        key = imagen.split(".")[0]
        log(f"## Generando comparaciones principales para {imagen}")
        imagen_rgb = cargar_imagen(imagen)
        orig_vis = reescalar(imagen_rgb) ** (1 / 2.2)
        log(
            f"[{key}] Original mapeada con función reescalar y gamma = 1/2.2"
        )
        Y = extraer_luminancia(imagen_rgb)
        Y_homo, Y_durand = aplicar_homo_durand(Y)
        luminancias = {
            "homomorfico": Y_homo ** (1 / 2.2),
            "durand": Y_durand ** (1 / 2.2),
        }
        recorte_color, recorte_luz = recortes[key]
        nombre_c1, (sy1, sx1) = recorte_color
        nombre_c2, (sy2, sx2) = recorte_luz
        for tipo in ("homomorfico", "durand"):
            beta, alfa = casos_principales[tipo]
            Y_prima = luminancias[tipo]
            # Estos requieren los experimentos 1 y 2 antes
            arch_est1 = f"{key}_{tipo}_beta_{str(beta)}.png"
            arch_est2 = f"{key}_{tipo}_cielch_c_{str(alfa)}.png"
            img_est1 = cargar_imagen(
                arch_est1, override_ruta=ruta_exp1) / 255.0
            img_est2 = cargar_imagen(
                arch_est2, override_ruta=ruta_exp2) / 255.0

            imgs = (orig_vis, Y_prima, img_est1, img_est2)
            titulos = ("Original", "Luminancia comprimida",
                       f"β = {beta}", f"alfa = {alfa}")
            mostrar(imgs, titulos, vmin=0, vmax=1,
                    nombre_guardado=f"{key}_{tipo}_comparativa", log=False,
                    ruta_adicional=ruta_adicional)

            recortes_zonas = ((nombre_c1, sy1, sx1), (nombre_c2, sy2, sx2))
            for n, (nombre_c, sy, sx) in enumerate(recortes_zonas, 1):
                imgs_recorte = [img[sy, sx] for img in imgs]
                mostrar(imgs_recorte, titulos, vmin=0, vmax=1,
                        nombre_guardado=f"{key}_{tipo}_recorte_{n}", log=False,
                        ruta_adicional=ruta_adicional)
                cuantificar_color(f"{key} | {tipo} | {nombre_c}",
                                  imgs_recorte[0], imgs_recorte[2], imgs_recorte[3],
                                  beta, alfa)
    return


if __name__ == "__main__":
    imagenes_base = ("bigFogMap.tif", "memorial.hdr")

    parametros = {
        "1": {
            "imagenes": imagenes_base,
            "betas": (0.6, 1, 1.4),
            "ruta": "exp1",
        },
        "2": {
            "imagenes": imagenes_base,
            "alfas": (0.2, 1, 1.8),
            "ruta": "exp2",
        },
        "3": {
            "imagenes": imagenes_base,
            "recortes": {
                "bigFogMap": (
                    ("colores intensos", (slice(130, 330), slice(230, 430))),
                    ("transición fuerte", (slice(270, 470), slice(400, 600))),
                ),
                "memorial": (
                    ("vitrales / color", (slice(430, 560), slice(250, 430))),
                    ("borde luz/sombra", (slice(70, 220), slice(90, 260))),
                ),
            },
            "casos_principales": {
                "homomorfico": (1.4, 1.8),  # (beta, alfa)
                "durand": (1, 1),           # (beta, alfa)
            },
            "ruta": "exp3",
        },
    }

    experimentos = {
        "1": exp1,
        "2": exp2,
        "3": exp3,
    }

    max_exp = len(parametros)
    exp = input(
        f"Inserte el número de experimento que desea replicar (1-{max_exp}); 0 para ejecutar todos: "
    )
    exp_validos = ("0",) + tuple(parametros.keys())

    if exp not in exp_validos:
        raise ValueError(
            f"Valor Inválido. La respuesta debe ser un número entero entre 0 y {max_exp}"
        )

    if exp == "0":
        for i in parametros:
            experimentos[i](parametros[i])
    else:
        experimentos[exp](parametros[exp])

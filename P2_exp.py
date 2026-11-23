import numpy
import os
from P2 import estrategia_1, estrategia_2, mostrar
from auxiliares import log, cargar_imagen, guardar_imagen


# Exp 1: Probar valores de 𝛽:
def exp1(parametros: tuple):
    imagenes, betas, ruta_adicional = parametros
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
                nombre_guardado=f"{key}_comparacion_homomorfica", log=False)
        mostrar(imgs_durand, titulos,
                nombre_guardado=f"{key}_comparacion_homomorfica", log=False)

    return


# Exp2: probar estrategia 2 con distintos valores de saturación de color (valores alfa)
def exp2(parametros: tuple):
    # str imagenes, multiplicadores para C*, ruta extra para el guardado
    imagenes, alfas, ruta_adicional = parametros
    log("", True)
    log("# Experimento 2 - Pregunta 2:")
    for alfa in alfas:
        for imagen in imagenes:
            estrategia_2(imagen, alfa, ruta_adicional)
    comparacion_exp2()
    return


if __name__ == "__main__":
    requisitos = {
        "1": (("bigFogMap.tif", "memorial.hdr"), (0.6, 1, 1.4), "exp1"),
        "2": (("bigFogMap.tif", "memorial.hdr"), (0.2, 1, 1.8), "exp2"),
        # "3": (("bigFogMap.tif", "memorial.hdr"), )
    }
    experimentos = {
        "1": exp1,
        "2": exp2,
    }

    exp = input(
        "Inserte el número de experimento que desea replicar (1-X); 0 para ejecutar todos: ")
    exp_validos = ("0", "1", "2")
    if exp not in exp_validos:
        raise ValueError(
            "Valor Inválido. La resuesta debe ser un número entero entre 0 y X")
    if exp == "0":
        for i in ("1", "2"):
            parametros = requisitos[i]
            experimento = experimentos[i]
            experimento(parametros)
    else:
        parametros = requisitos[exp]
        experimento = experimentos[exp]
        experimento(parametros)

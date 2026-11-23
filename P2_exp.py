import numpy
from P2 import estrategia_1, estrategia_2
from auxiliares import log


# Exp 1: Probar valores de 𝛽:
def exp1(parametros: tuple):
    imagenes, betas, ruta_adicional = parametros
    log("", True)  # Ping Reset
    log("# Experimento 1 - Pregunta 2:")
    for beta in betas:
        for imagen in imagenes:
            estrategia_1(imagen, beta, ruta_adicional)
    return


"""
imagenes = ("bigFogMap.tif", "memorial.hdr")
betas = (0.6, 1, 1.4)
exp1(imagenes, betas)
"""

# Exp2: probar estrategia 2 con distintos valores de saturación de color


def exp2(parametros: tuple):
    imagenes, betas, ruta_adicional = parametros
    log("", True)
    log("# Experimento 2 - Pregunta 2:")
    for beta in betas:
        for imagen in imagenes:
            estrategia_2(imagen, beta, ruta_adicional)
    return


if __name__ == "__main__":
    # Exp 1-2
    requisitos = {
        "1": (("bigFogMap.tif", "memorial.hdr"), (0.6, 1, 1.4), "exp1"),
        "2": (("bigFogMap.tif", "memorial.hdr"), (0.6, 1, 1.4), "exp2"),
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

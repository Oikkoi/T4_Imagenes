import numpy as np
import __main__
import matplotlib.pyplot as plt
from astropy.io import fits
import os
# ↓Línea añadida porque tengo una extensión que formatea el código a PEP8 pero tengo que activar la capacidad de leer HDR en CV2
os.environ["OPENCV_IO_ENABLE_HDR"] = "1"
import cv2  # noqa: E402  # isort: skip

# Funciones importadas de la semana 12 de las cápsulas de código:


def luminancia(E):
    # Fila Y de la matriz RGB -> XYZ usada en la cápsula de espacios de color
    return 0.177 * E[..., 0] + 0.813 * E[..., 1] + 0.011 * E[..., 2]


def H_homomorfico(forma, gamma_H=1.5, gamma_L=0.5, D0=30, c=1.0):
    P, Q = forma
    v, u = np.mgrid[0:P, 0:Q]
    # D(u, v)^2, distancia al centro
    D2 = (u - Q / 2) ** 2 + (v - P / 2) ** 2
    return (gamma_H - gamma_L) * (1 - np.exp(-c * D2 / D0 ** 2)) + gamma_L


def filtro_homomorfico(f, gamma_H=1.5, gamma_L=0.5, D0=30, c=1.0, eps=1e-6):
    N, M = f.shape
    z = np.log(f + eps)                                       # ln
    # relleno por reflexión, P = 2N, Q = 2M
    z_pad = np.pad(z, ((0, N), (0, M)), mode='symmetric')
    H = H_homomorfico(z_pad.shape, gamma_H, gamma_L, D0, c)
    # DFT centrada y filtro
    S = H * fftshift(fft2(z_pad))
    # DFT inversa y recorte
    s = ifft2(ifftshift(S)).real[:N, :M]
    return np.exp(s)


def durand(E, sigma_s=None, sigma_r=0.4, contraste=30, s=0.6, filtro='bilateral'):
    Y = luminancia(E)
    logY = np.log10(Y + 1e-12).astype(np.float32)
    if sigma_s is None:
        # 2% del tamaño de la imagen
        sigma_s = 0.02 * max(Y.shape)

    if filtro == 'bilateral':
        base = cv2.bilateralFilter(
            logY, d=-1, sigmaColor=sigma_r, sigmaSpace=sigma_s)
    else:
        base = cv2.GaussianBlur(logY, (0, 0), sigma_s)
    detalle = logY - base

    k = np.log10(contraste) / (base.max() - base.min())
    L_out = 10 ** (k * (base - base.max()) + detalle)
    return a_pantalla(recolorear(E, Y, L_out, s)), base, detalle

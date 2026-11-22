import os
import numpy as np
import matplotlib.pyplot as plt

# ↓Línea para configurar cv2 y que pueda leer HDR
os.environ["OPENCV_IO_ENABLE_HDR"] = "1"
import cv2  # noqa: E402  # isort: skip

from auxiliares import cargar_imagen, visualizar, guardar_imagen  # noqa: #402

# Funciones importadas de la semana 12 de las cápsulas de código:


def luminancia(E):
    # Fila Y de la matriz RGB -> XYZ usada en la cápsula de espacios de color
    return 0.177 * E[..., 0] + 0.813 * E[..., 1] + 0.011 * E[..., 2]


def reescalar(g, p_bajo=0.5, p_alto=99.5):
    # Lleva los percentiles p_bajo y p_alto a 0 y 1, recortando los extremos
    lo, hi = np.percentile(g, [p_bajo, p_alto])
    return np.clip((g - lo) / (hi - lo), 0.0, 1.0)


def mostrar(imgs, titulos, cmap='gray', ncols=None, size=4, vmin=None, vmax=None, marco=False):
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


def H_homomorfico(forma, gamma_H=1.5, gamma_L=0.5, D0=30, c=1.0):
    P, Q = forma
    v, u = np.mgrid[0:P, 0:Q]
    D2 = (u - Q / 2) ** 2 + (v - P / 2) ** 2
    return (gamma_H - gamma_L) * (1 - np.exp(-c * D2 / D0 ** 2)) + gamma_L


def filtro_homomorfico(f, gamma_H=1.5, gamma_L=0.5, D0=30, c=1.0, eps=1e-6):
    N, M = f.shape
    z = np.log(f + eps)
    z_pad = np.pad(z, ((0, N), (0, M)), mode='symmetric')
    H = H_homomorfico(z_pad.shape, gamma_H, gamma_L, D0, c)

    S = H * np.fft.fftshift(np.fft.fft2(z_pad))
    s = np.fft.ifft2(np.fft.ifftshift(S)).real[:N, :M]
    return np.exp(s)


def durand(f, sigma_s=None, sigma_r=0.4, contraste=30, filtro='bilateral', e=1e-12):
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
    return L_out.astype(np.float64)

"""Filtres de couleur : seuls les canaux RGB changent, l'alpha est conservé."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from scipy import ndimage

# Layer sert aux annotations ; l'importer à l'exécution créerait un cycle.
if TYPE_CHECKING:
    from .classes import Layer

# Ces indices restent dans le fichier pour pouvoir échanger les filtres seuls.
R, G, B = 0, 1, 2


def grayscale(layer: Layer) -> Layer:
    """Transforme l'image en noir et blanc."""
    gray = (
        0.299 * layer.pixels[:, :, R]
        + 0.587 * layer.pixels[:, :, G]
        + 0.114 * layer.pixels[:, :, B]
    )
    gray = np.clip(np.rint(gray), 0, 255).astype(np.uint8)
    layer.pixels[:, :, :3] = gray[:, :, None]
    return layer


def swapBG(layer: Layer) -> Layer:
    """Echange le bleu et le vert de l'image."""
    layer.pixels[:, :, [G, B]] = layer.pixels[:, :, [B, G]]
    return layer


def brightness(layer: Layer, value: float) -> Layer:
    """Multiplie les couleurs : 0 donne du noir, 1 conserve la luminosité."""
    if value < 0:
        raise ValueError("La luminosité doit être positive ou nulle.")
    pixels = layer.pixels[:, :, :3].astype(np.float32) * value
    layer.pixels[:, :, :3] = np.clip(np.rint(pixels), 0, 255).astype(np.uint8)
    return layer


def contrast(layer: Layer, value: float) -> Layer:
    """Change le contraste de l'image."""
    if not 0 < value <= 5:
        raise ValueError("Le contraste doit être supérieur à 0 et inférieur ou égal à 5.")

    pixels = layer.pixels[:, :, :3].astype(np.float32)
    pixels += (1 - value) * (255 // 2 - pixels)
    layer.pixels[:, :, :3] = np.clip(np.rint(pixels), 0, 255).astype(np.uint8)

    return layer


def blur(layer: Layer, radius: int) -> Layer:
    """Flou moyen par convolution horizontale puis verticale."""
    if radius < 0:
        raise ValueError("Le rayon doit être positif ou nul.")
    if radius == 0:
        return layer

    size = 2 * radius + 1
    kernel = np.ones(size, dtype=np.float32) / size
    pixels = layer.pixels[:, :, :3].astype(np.float32)
    pixels = ndimage.convolve(pixels, kernel[None, :, None], mode="reflect")
    pixels = ndimage.convolve(pixels, kernel[:, None, None], mode="reflect")
    layer.pixels[:, :, :3] = np.clip(np.rint(pixels), 0, 255).astype(np.uint8)
    return layer


def black_border(layer: Layer, thickness: int = 10) -> Layer:
    """Ajoute une bordure noire sans changer la taille de l'image."""
    if thickness < 0:
        raise ValueError("L'épaisseur doit être positive ou nulle.")
    if thickness == 0:
        return layer

    layer.pixels[:thickness, :, :3] = 0
    layer.pixels[-thickness:, :, :3] = 0
    layer.pixels[:, :thickness, :3] = 0
    layer.pixels[:, -thickness:, :3] = 0
    return layer


def invert(layer: Layer) -> Layer:
    """Inverse les couleurs sans inverser la transparence."""
    layer.pixels[:, :, :3] = 255 - layer.pixels[:, :, :3]
    return layer


def sepia(layer: Layer) -> Layer:
    """Applique la matrice de transformation sépia classique."""
    pixels = layer.pixels[:, :, :3].astype(np.float32)
    red = pixels[:, :, R]
    green = pixels[:, :, G]
    blue = pixels[:, :, B]

    sepia = np.empty_like(pixels)
    sepia[:, :, R] = 0.393 * red + 0.769 * green + 0.189 * blue
    sepia[:, :, G] = 0.349 * red + 0.686 * green + 0.168 * blue
    sepia[:, :, B] = 0.272 * red + 0.534 * green + 0.131 * blue

    layer.pixels[:, :, :3] = np.clip(np.rint(sepia), 0, 255).astype(np.uint8)
    return layer


def gaussianBlur(layer: Layer, window: int, sigma: float) -> Layer:
    """Applique une convolution gaussienne 2D sans modifier le canal alpha."""
    x = np.arange(window) - (window - 1) / 2
    kernel1D = np.exp(-(x**2) / (2 * sigma**2))
    # Normaliser le noyau conserve la luminosité d'une couleur uniforme.
    kernel1D /= kernel1D.sum()
    kernel2D = np.outer(kernel1D, kernel1D)

    # Le dernier axe de taille 1 évite de mélanger les canaux RGB.
    pixels = layer.pixels[:, :, :3].astype(np.float32)
    pixels = ndimage.convolve(pixels, kernel2D[:, :, None], mode="reflect")
    layer.pixels[:, :, :3] = np.clip(np.rint(pixels), 0, 255).astype(np.uint8)
    return layer

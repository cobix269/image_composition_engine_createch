from __future__ import annotations

from typing import TYPE_CHECKING

# Layer sert aux annotations ; l'importer à l'exécution créerait un cycle.
if TYPE_CHECKING:
    from classes import Layer
from constants import R,G,B,A
import numpy as np
import scipy

def grayscale(layer: Layer) -> Layer:
    """Transforme l'image en noir et blanc."""
    gray = (
        0.299 * layer.pixels[:, :, R]
        + 0.587 * layer.pixels[:, :, G]
        + 0.114 * layer.pixels[:, :, B]
    )
    gray = np.clip(np.rint(gray), 0, 255).astype(np.uint8)
    layer.pixels = np.stack((gray, gray, gray, layer.pixels[:, :, A]), axis=2)
    return layer

def swapBG(layer: Layer) -> Layer:
    """Echange le bleu et le vert de l'image."""
    layer.pixels[:, :, [G, B]] = layer.pixels[:, :, [B, G]]
    return layer

def brightness(layer: Layer, value: float) -> Layer:
    """Change la luminosité de l'image."""
    pixels = layer.pixels.astype(np.float32)
    pixels += (1 - value) * (255 // 2 - pixels)
    layer.pixels = np.clip(np.rint(pixels), 0, 255).astype(np.uint8)
    return layer

def contrast(layer: Layer, value: float) -> Layer:
    """Change le contraste de l'image."""
    if value <= 0 or value >5 :
        raise ValueError("Le contraste doit être entre 0 et 5")
    
    pixels = layer.pixels.astype(np.float32)
    pixels += (1 - value) * (255 // 2 - pixels)
    layer.pixels = np.clip(np.rint(pixels), 0, 255).astype(np.uint8)
    
    return layer

def blur(layer: Layer, radius: int) -> Layer:
    """Flou moyen par convolution horizontale puis verticale."""
    if radius < 0:
        raise ValueError("Le rayon doit être positif ou nul.")
    if radius == 0:
        return layer

    size = 2 * radius + 1
    kernel = np.ones(size, dtype=np.float32) / size
    pixels = scipy.ndimage.convolve(layer.pixels, kernel[None, :, None], output=np.float32, mode="reflect")
    pixels = scipy.ndimage.convolve(pixels, kernel[:, None, None], mode="reflect")
    layer.pixels = np.clip(np.rint(pixels), 0, 255).astype(np.uint8)
    return layer

def gaussianblur(layer: Layer, window: int, sigma: float) -> Layer:
    """Flou gaussien horizontal puis vertical, sans modifier l'alpha."""
    positions = np.arange(window) - (window - 1) / 2
    kernel = np.exp(-positions**2 / (2 * sigma**2))
    kernel /= kernel.sum()

    pixels = layer.pixels[:, :, :3].astype(np.float32)
    pixels = scipy.ndimage.convolve(pixels, kernel[None, :, None], mode="reflect")
    pixels = scipy.ndimage.convolve(pixels, kernel[:, None, None], mode="reflect")
    layer.pixels[:, :, :3] = np.clip(np.rint(pixels), 0, 255).astype(np.uint8)
    return layer


def black_border(layer: Layer, thickness: int = 10) -> Layer:
    """Ajoute une bordure noire sans changer la taille de l'image."""
    if thickness < 0:
        raise ValueError("L'épaisseur doit être positive ou nulle.")
    if thickness == 0:
        return layer

    layer.pixels[:thickness, :, :] = 0
    layer.pixels[-thickness:, :, :] = 0
    layer.pixels[:, :thickness, :] = 0
    layer.pixels[:, -thickness:, :] = 0
    return layer

def invert(layer) -> Layer:
    """Inverse les couleurs"""
    pixels = layer.pixels.astype(np.float32)
    pixels = abs((pixels - 255))
    layer.pixels = np.clip(np.rint(pixels), 0, 255).astype(np.uint8)
    return layer

def sepia(layer) -> Layer:
    """Applique la matrice de transformation sépia classique."""
    pixels = layer.pixels.astype(np.float32)
    red = pixels[:, :, R]
    green = pixels[:, :, G]
    blue = pixels[:, :, B]

    sepia = np.empty_like(pixels)
    sepia[:, :, R] = 0.393 * red + 0.769 * green + 0.189 * blue
    sepia[:, :, G] = 0.349 * red + 0.686 * green + 0.168 * blue
    sepia[:, :, B] = 0.272 * red + 0.534 * green + 0.131 * blue

    layer.pixels = np.clip(np.rint(sepia), 0, 255).astype(np.uint8)
    return layer

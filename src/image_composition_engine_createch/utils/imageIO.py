"""Lecture et affichage d'images RGB/RGBA en uint8, entre 0 et 255."""

from pathlib import Path

import numpy as np
from PIL import Image


def arrayFromFile(path: str | Path, mode: str = "RGB") -> np.ndarray:
    """Charge une image RGB ou RGBA en uint8 (0 à 255)."""
    # Le tableau garde ses pixels en mémoire après la fermeture du fichier.
    with Image.open(path) as image:
        return np.array(image.convert(mode))


def arrayToImage(arr: np.ndarray) -> Image.Image:
    """Convertit des pixels de 0 à 255 en image RGB ou RGBA."""
    # Arrondir et borner avant la conversion évite les débordements en uint8.
    return Image.fromarray(np.clip(np.rint(arr), 0, 255).astype(np.uint8))


def showFromArray(arr: np.ndarray) -> None:
    """Ouvre l'image dans la visionneuse du système via Pillow."""
    arrayToImage(arr).show()

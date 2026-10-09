"""Lecture et affichage d'images, représentées en flottants entre 0 et 1."""

from pathlib import Path

import numpy as np
from PIL import Image


def arrayFromFile(path: Path) -> np.ndarray:
    """Charge une image en RGBA, de forme (hauteur, largeur, 4)."""
    with Image.open(path) as image:
        return np.asarray(image.convert("RGBA"), dtype=np.float32) / 255


def showFromArray(rgb: np.ndarray) -> None:
    """Affiche une image RGB dans la visionneuse du système, en 8 bits."""
    pixels = np.rint(np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(pixels).show()

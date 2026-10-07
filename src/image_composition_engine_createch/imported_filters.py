"""Filtres de l'autre groupe au même format que nos classes de filtres.

Les classes reçoivent des images RGB en flottants entre 0 et 1.
Layer se charge de la conversion et conserve le canal alpha du calque.
"""

from __future__ import annotations

import numpy as np
from pydantic import Field
from pydantic.dataclasses import dataclass
from scipy.ndimage import convolve

from .classes import Filter, Layer


@dataclass
class normal(Filter):
    def apply(self, image: np.ndarray) -> np.ndarray:
        return image


@dataclass
class blur(Filter):
    """Flou moyenneur ; la taille du noyau vaut 5 par défaut."""

    taille: int = Field(default=5, ge=1)

    def apply(self, image: np.ndarray) -> np.ndarray:
        t = self.taille
        noyau = np.ones((t, t)) / (t * t)
        return convolve(image, noyau[:, :, None], mode="nearest")


@dataclass
class gaussianblur(Filter):
    window: int = Field(ge=1)
    sigma: float = Field(gt=0)

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Applique un noyau gaussien window x window d'écart-type sigma."""
        window = self.window
        sigma = self.sigma
        ax = np.arange(window) - (window - 1) / 2
        xx, yy = np.meshgrid(ax, ax)
        noyau = np.exp(-(xx**2 + yy**2) / (2 * sigma**2))
        noyau /= noyau.sum()
        return convolve(image, noyau[:, :, None], mode="nearest")


@dataclass
class Grayscale(Filter):
    def apply(self, image: np.ndarray) -> np.ndarray:
        red, green, blue = image[:, :, 0], image[:, :, 1], image[:, :, 2]
        gray = 0.299 * red + 0.587 * green + 0.114 * blue
        new = image.copy()
        new[:, :, 0] = gray
        new[:, :, 1] = gray
        new[:, :, 2] = gray
        return new


@dataclass
class Sepia(Filter):
    def apply(self, image: np.ndarray) -> np.ndarray:
        matrice = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131],
        ])
        return np.clip(image @ matrice.T, 0, 1)


@dataclass
class blackborder(Filter):
    border_size: int = Field(ge=1)

    def apply(self, image: np.ndarray) -> np.ndarray:
        epaisseur = self.border_size
        image[:epaisseur, :, :] = 0
        image[-epaisseur:, :, :] = 0
        image[:, :epaisseur, :] = 0
        image[:, -epaisseur:, :] = 0
        return image


Layer.FILTERS.update({
    "importedNormal": normal,
    "importedBlur": blur,
    "importedGaussianBlur": gaussianblur,
    "importedGrayscale": Grayscale,
    "importedSepia": Sepia,
    "importedBlackBorder": blackborder,
})

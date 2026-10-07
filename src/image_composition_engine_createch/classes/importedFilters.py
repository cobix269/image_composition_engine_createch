"""Filtres de l'autre groupe ; les traitements identiques réutilisent nos classes."""

import numpy as np
from pydantic import Field
from pydantic.dataclasses import dataclass
from scipy.ndimage import convolve

from .base import Filter
from .filters import GaussianBlur, Grayscale, Normal, Sepia


@dataclass
class Blur(Filter):
    """Flou moyenneur ; la taille du noyau vaut 5 par défaut."""

    taille: int = Field(default=5, ge=1)

    def apply(self, image: np.ndarray) -> np.ndarray:
        t = self.taille
        noyau = np.ones((t, t)) / (t * t)
        return convolve(image, noyau[:, :, None], mode="nearest")


@dataclass
class BlackBorder(Filter):
    border_size: int = Field(ge=1)

    def apply(self, image: np.ndarray) -> np.ndarray:
        epaisseur = self.border_size
        image[:epaisseur, :, :] = 0
        image[-epaisseur:, :, :] = 0
        image[:, :epaisseur, :] = 0
        image[:, -epaisseur:, :] = 0
        return image


FILTERS = {
    "importedNormal": Normal,
    "importedBlur": Blur,
    "importedGaussianBlur": GaussianBlur,
    "importedGrayscale": Grayscale,
    "importedSepia": Sepia,
    "importedBlackBorder": BlackBorder,
}

"""Calque : couleurs, transparence, opacité et mode de fusion."""

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from ..utils.imageIO import arrayFromFile
from .base import Filter


@dataclass(eq=False)
class Layer:
    """Calque prêt à composer, en flottants entre 0 et 1.

    `rgb` a la forme (hauteur, largeur, 3) et `alpha` la forme
    (hauteur, largeur, 1), pour pouvoir les multiplier directement.
    """

    rgb: np.ndarray = field(repr=False)
    alpha: np.ndarray = field(repr=False)
    opacity: float = 1.0
    blend: str = "normal"

    @classmethod
    def fromFile(cls, path: Path, opacity: float = 1.0, blend: str = "normal") -> Layer:
        """Charge une image ; sans transparence, son alpha vaut 1 partout."""
        pixels = arrayFromFile(path)
        return cls(pixels[:, :, :3], pixels[:, :, 3:], opacity, blend)

    def applyFilter(self, imageFilter: Filter) -> None:
        """Remplace les couleurs par celles du filtre ; l'alpha ne change pas."""
        # Borner protège la composition d'un filtre importé qui sortirait de [0, 1].
        self.rgb = np.clip(imageFilter.apply(self.rgb), 0, 1)

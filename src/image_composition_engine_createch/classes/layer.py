"""Calques RGBA, registres et application des filtres."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

import numpy as np

from ..utils.imageIO import arrayFromFile
from .base import Blend, Filter
from .blends import BLENDS, BlendParams
from .filters import FILTERS
from .importedFilters import FILTERS as IMPORTED_FILTERS


@dataclass(eq=False)
class Layer:
    """Calque RGBA ; les filtres travaillent uniquement sur ses couleurs RGB."""

    src: str | Path
    opacity: float = 1.0
    blend: str = "normal"
    pixels: np.ndarray = field(init=False, repr=False)

    FILTERS: ClassVar[dict[str, type[Filter]]] = {**FILTERS, **IMPORTED_FILTERS}
    BLENDS: ClassVar[dict[str, type[Blend]]] = BLENDS

    def __post_init__(self) -> None:
        """Charge les pixels après l'affectation automatique des attributs."""
        self.pixels = arrayFromFile(self.src, "RGBA")
        self.blend = BlendParams(blend=self.blend).blend

    def applyFilter(self, imageFilter: Filter) -> Layer:
        """Applique une instance de filtre et conserve l'alpha du calque."""
        image = self.pixels[:, :, :3].astype(np.float32) / 255
        result = imageFilter.apply(image)
        self.pixels[:, :, :3] = np.clip(np.rint(result * 255), 0, 255).astype(np.uint8)
        return self

"""Calques, registre des classes de filtres et validation des modes de fusion."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

import numpy as np
from pydantic import BaseModel, ConfigDict, field_validator
from pydantic.dataclasses import dataclass as validatedDataclass

from .blend import blendFunctions
from .utils import array_from_file


@validatedDataclass(config=ConfigDict(strict=True, extra="forbid", allow_inf_nan=False))
class Filter(ABC):
    """Les dataclasses filles héritent des règles de validation Pydantic."""

    @abstractmethod
    def apply(self, image: np.ndarray) -> np.ndarray:
        """Reçoit une image RGB en flottants entre 0 et 1 et renvoie une image RGB."""
        pass


class BlendParams(BaseModel):
    """Définit les modes de fusion acceptés et le mode par défaut."""
    model_config = ConfigDict(strict=True, extra="forbid")
    blend: str = "normal"

    @field_validator("blend")
    @classmethod
    def validate_blend(cls, mode: str) -> str:
        if mode not in blendFunctions:
            available = ", ".join(blendFunctions)
            raise ValueError(f"Mode de blend inconnu : {mode!r}. Modes disponibles : {available}.")
        return mode


@dataclass(eq=False)
class Layer:
    """Calque RGBA ; les filtres travaillent uniquement sur ses couleurs RGB."""

    src: str | Path
    opacity: float = 1.0
    blend: str = "normal"
    pixels: np.ndarray = field(init=False, repr=False)

    FILTERS: ClassVar[dict[str, type[Filter]]] = {}

    def __post_init__(self) -> None:
        """Charge les pixels après l'affectation automatique des attributs."""
        self.pixels = array_from_file(self.src, "RGBA")
        self.blend = BlendParams(blend=self.blend).blend

    def applyFilter(self, imageFilter: Filter) -> Layer:
        """Applique une instance de filtre et conserve l'alpha du calque."""
        image = self.pixels[:, :, :3].astype(np.float32) / 255
        result = imageFilter.apply(image)
        self.pixels[:, :, :3] = np.clip(np.rint(result * 255), 0, 255).astype(np.uint8)
        return self


# Charger les filtres après la définition des bases pour éviter les imports circulaires.
# Chaque module enregistre ses classes dans Layer.FILTERS.
from . import filters, imported_filters

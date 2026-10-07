"""Contrats des filtres et blends, avec leurs règles Pydantic communes."""

from abc import ABC, abstractmethod

import numpy as np
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

parameterConfig = ConfigDict(strict=True, extra="forbid", allow_inf_nan=False)


@dataclass(config=parameterConfig)
class Filter(ABC):
    """Les dataclasses filles héritent des règles de validation Pydantic."""

    @abstractmethod
    def apply(self, image: np.ndarray) -> np.ndarray:
        """Reçoit une image RGB en flottants entre 0 et 1 et renvoie une image RGB."""
        pass


@dataclass(config=parameterConfig)
class Blend(ABC):
    """Base des modes de fusion ; les paramètres éventuels sont validés."""

    @abstractmethod
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        """Mélange deux images RGB entre 0 et 1, sans appliquer leur opacité."""
        pass

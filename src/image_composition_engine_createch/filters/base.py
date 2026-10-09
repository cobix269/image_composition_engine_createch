"""Contrat commun des filtres, à fournir avec nos filtres quand on les partage."""

from abc import ABC, abstractmethod

import numpy as np
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass


@dataclass(config=ConfigDict(strict=True, extra="forbid", allow_inf_nan=False))
class Filter(ABC):
    """Filtre d'image dont les paramètres sont les champs de la dataclass.

    Les sous-classes décorées par `@dataclass` héritent de cette configuration :
    types stricts, nombres finis et aucun paramètre inconnu.
    """

    @abstractmethod
    def apply(self, image: np.ndarray) -> np.ndarray:
        """Reçoit une image RGB (hauteur, largeur, 3) en flottants entre 0 et 1.

        Renvoie une image de même forme, entre 0 et 1. L'image reçue peut être
        modifiée sur place.
        """

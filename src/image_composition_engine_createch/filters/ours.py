"""Nos filtres ; chacun suit le contrat de `Filter` décrit dans base.py."""

import numpy as np
from pydantic import Field
from pydantic.dataclasses import dataclass
from scipy.ndimage import convolve

from .base import Filter


@dataclass
class Normal(Filter):
    """Laisse l'image inchangée."""

    def apply(self, image: np.ndarray) -> np.ndarray:
        return image


@dataclass
class Grayscale(Filter):
    """Niveaux de gris pondérés par la sensibilité de l'œil à chaque couleur."""

    def apply(self, image: np.ndarray) -> np.ndarray:
        gray = image @ [0.299, 0.587, 0.114]
        return np.repeat(gray[:, :, None], 3, axis=2)


@dataclass
class SwapBG(Filter):
    """Échange le bleu et le vert."""

    def apply(self, image: np.ndarray) -> np.ndarray:
        return image[:, :, [0, 2, 1]]


@dataclass
class Brightness(Filter):
    """Multiplie les couleurs : 0 donne du noir, 1 ne change rien, au-delà éclaircit."""

    value: float = Field(ge=0)

    def apply(self, image: np.ndarray) -> np.ndarray:
        return np.clip(image * self.value, 0, 1)


@dataclass
class Contrast(Filter):
    """Écarte les couleurs du gris moyen si value > 1, les en rapproche si value < 1."""

    value: float = Field(gt=0, le=5)

    def apply(self, image: np.ndarray) -> np.ndarray:
        return np.clip(0.5 + self.value * (image - 0.5), 0, 1)


@dataclass
class Blur(Filter):
    """Flou moyen sur un carré de côté 2 * radius + 1 ; radius = 0 ne change rien."""

    radius: int = Field(ge=0)

    def apply(self, image: np.ndarray) -> np.ndarray:
        # Une passe par ligne puis une par colonne équivaut au noyau carré, en plus rapide.
        size = 2 * self.radius + 1
        kernel = np.ones(size, dtype=np.float32) / size
        image = convolve(image, kernel[None, :, None], mode="reflect")
        return convolve(image, kernel[:, None, None], mode="reflect")


@dataclass
class GaussianBlur(Filter):
    """Flou gaussien sur une fenêtre window × window, d'écart-type sigma."""

    window: int = Field(ge=1)
    sigma: float = Field(gt=0)

    def apply(self, image: np.ndarray) -> np.ndarray:
        axis = np.arange(self.window) - (self.window - 1) / 2
        xx, yy = np.meshgrid(axis, axis)
        kernel = np.exp(-(xx**2 + yy**2) / (2 * self.sigma**2))
        kernel /= kernel.sum()
        # Le dernier axe de taille 1 évite de mélanger les canaux R, G et B.
        return convolve(image, kernel[:, :, None], mode="nearest")


@dataclass
class BlackBorder(Filter):
    """Bordure noire de thickness pixels, sans changer la taille de l'image."""

    thickness: int = Field(default=10, ge=0)

    def apply(self, image: np.ndarray) -> np.ndarray:
        height, width = image.shape[:2]
        t = self.thickness
        result = np.zeros_like(image)
        result[t : height - t, t : width - t] = image[t : height - t, t : width - t]
        return result


@dataclass
class Invert(Filter):
    """Négatif : chaque couleur devient son complément."""

    def apply(self, image: np.ndarray) -> np.ndarray:
        return 1 - image


@dataclass
class Sepia(Filter):
    """Matrice sépia classique."""

    def apply(self, image: np.ndarray) -> np.ndarray:
        matrix = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131],
        ])
        return np.clip(image @ matrix.T, 0, 1)

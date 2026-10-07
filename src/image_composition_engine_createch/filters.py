"""Filtres RGB en flottants entre 0 et 1 ; Layer conserve le canal alpha."""

import numpy as np
from pydantic import Field
from pydantic.dataclasses import dataclass
from scipy.ndimage import convolve

from .classes import Filter, Layer


@dataclass
class Normal(Filter):
    def apply(self, image: np.ndarray) -> np.ndarray:
        return image


@dataclass
class Grayscale(Filter):
    def apply(self, image: np.ndarray) -> np.ndarray:
        gray = 0.299 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 2]
        return np.repeat(gray[:, :, None], 3, axis=2)


@dataclass
class SwapBG(Filter):
    def apply(self, image: np.ndarray) -> np.ndarray:
        return image[:, :, [0, 2, 1]]


@dataclass
class Brightness(Filter):
    value: float = Field(ge=0)

    def apply(self, image: np.ndarray) -> np.ndarray:
        """0 donne du noir, 1 conserve les couleurs, > 1 éclaircit."""
        return np.clip(image * self.value, 0, 1)


@dataclass
class Contrast(Filter):
    value: float = Field(gt=0, le=5)

    def apply(self, image: np.ndarray) -> np.ndarray:
        # Conserver le centre historique de 127 dans notre espace normalisé.
        value = self.value
        return np.clip(image + (1 - value) * (127 / 255 - image), 0, 1)


@dataclass
class Blur(Filter):
    radius: int = Field(ge=0)

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Flou moyen par deux convolutions ; radius=0 conserve l'image."""
        size = 2 * self.radius + 1
        kernel = np.ones(size, dtype=np.float32) / size
        pixels = convolve(image, kernel[None, :, None], mode="reflect")
        return convolve(pixels, kernel[:, None, None], mode="reflect")


@dataclass
class GaussianBlur(Filter):
    window: int = Field(ge=1)
    sigma: float = Field(gt=0)

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Noyau gaussien 2D, avec le comportement nearest de blurRaph."""
        window = self.window
        sigma = self.sigma
        axis = np.arange(window) - (window - 1) / 2
        xx, yy = np.meshgrid(axis, axis)
        kernel = np.exp(-(xx**2 + yy**2) / (2 * sigma**2))
        kernel /= kernel.sum()
        return convolve(image, kernel[:, :, None], mode="nearest")


@dataclass
class BlackBorder(Filter):
    thickness: int = Field(default=10, ge=0)

    def apply(self, image: np.ndarray) -> np.ndarray:
        thickness = self.thickness
        result = image.copy()
        if thickness:
            result[:thickness, :, :] = 0
            result[-thickness:, :, :] = 0
            result[:, :thickness, :] = 0
            result[:, -thickness:, :] = 0
        return result


@dataclass
class Invert(Filter):
    def apply(self, image: np.ndarray) -> np.ndarray:
        return 1 - image


@dataclass
class Sepia(Filter):
    def apply(self, image: np.ndarray) -> np.ndarray:
        matrix = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131],
        ])
        return np.clip(image @ matrix.T, 0, 1)


Layer.FILTERS.update({
    "normal": Normal,
    "grayscale": Grayscale,
    "swapBG": SwapBG,
    "brightness": Brightness,
    "contrast": Contrast,
    "blur": Blur,
    "gaussianBlur": GaussianBlur,
    "blurRaph": GaussianBlur,
    "blackBorder": BlackBorder,
    "black_border": BlackBorder,
    "invert": Invert,
    "sepia": Sepia,
})

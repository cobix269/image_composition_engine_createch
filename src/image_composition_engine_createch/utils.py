from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PIL import Image

if TYPE_CHECKING:
    from .classes import Layer


def array_from_file(path: str, mode: str = "RGB") -> np.ndarray:
    """Charge une image RGB ou RGBA en uint8 (0 à 255)."""
    with Image.open(path) as image:
        return np.array(image.convert(mode))


def array_to_image(arr: np.ndarray) -> Image.Image:
    """Convertit des pixels de 0 à 255 en image RGB ou RGBA."""
    return Image.fromarray(np.clip(np.rint(arr), 0, 255).astype(np.uint8))


def show_from_array(arr: np.ndarray) -> None:
    array_to_image(arr).show()


def display_from_array(arr: np.ndarray) -> None:
    show_from_array(arr)


def array_from_file_RGBA(path: str) -> np.ndarray:
    return array_from_file(path, "RGBA")


def compose(layers: list[Layer]) -> np.ndarray:
    """Superpose des calques de pixels 0 à 255 sur un fond noir."""
    if not layers:
        raise ValueError("Il faut au moins un calque.")

    height, width = layers[0].pixels.shape[:2]
    result = np.zeros((height, width, 3), dtype=np.float32)

    for layer in layers:
        pixels = layer.pixels
        if pixels.ndim != 3 or pixels.shape[2] not in (3, 4):
            raise ValueError("Chaque calque doit être RGB ou RGBA.")
        if pixels.shape[:2] != (height, width):
            raise ValueError("Les calques doivent avoir les mêmes dimensions.")
        if not 0 <= layer.opacity <= 1:
            raise ValueError("L'opacité doit être comprise entre 0 et 1.")

        alpha = layer.opacity
        if pixels.shape[2] == 4:
            alpha = alpha * pixels[:, :, 3:4].astype(np.float32) / 255

        result = (1 - alpha) * result + alpha * pixels[:, :, :3]

    return np.clip(np.rint(result), 0, 255).astype(np.uint8)

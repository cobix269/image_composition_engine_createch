"""Chargement, affichage et superposition d'images avec des pixels de 0 à 255."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PIL import Image

# Layer sert uniquement aux annotations : cet import évite une dépendance
# circulaire à l'exécution, puisque classes.py importe aussi utils.py.
if TYPE_CHECKING:
    from .classes import Layer


def array_from_file(path: str, mode: str = "RGB") -> np.ndarray:
    """Charge une image RGB ou RGBA en uint8 (0 à 255)."""
    # Le tableau garde ses pixels en mémoire après la fermeture du fichier.
    with Image.open(path) as image:
        return np.array(image.convert(mode))


def array_to_image(arr: np.ndarray) -> Image.Image:
    """Convertit des pixels de 0 à 255 en image RGB ou RGBA."""
    # Arrondir et borner avant la conversion évite les débordements en uint8.
    return Image.fromarray(np.clip(np.rint(arr), 0, 255).astype(np.uint8))


def show_from_array(arr: np.ndarray) -> None:
    """Ouvre l'image dans la visionneuse du système via Pillow."""
    array_to_image(arr).show()


def display_from_array(arr: np.ndarray) -> None:
    """Même affichage que show_from_array, dans une fenêtre externe."""
    show_from_array(arr)


def array_from_file_RGBA(path: str) -> np.ndarray:
    """Charge les couleurs et le canal alpha (0 transparent, 255 opaque)."""
    return array_from_file(path, "RGBA")


def colorBurn(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    # Si le diviseur vaut zéro, le résultat est noir (sauf sur un fond blanc).
    ratio = np.divide(1 - background, foreground,
                      out=np.ones_like(background), where=foreground != 0)
    return np.where(background == 1, 1, 1 - np.clip(ratio, 0, 1))


def colorDodge(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    # Si le diviseur vaut zéro, le résultat est blanc (sauf sur un fond noir).
    ratio = np.divide(background, 1 - foreground,
                      out=np.ones_like(background), where=foreground != 1)
    return np.where(background == 0, 0, np.clip(ratio, 0, 1))


def overlay(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return np.where(
        background <= 0.5,
        2 * background * foreground,
        1 - 2 * (1 - background) * (1 - foreground),
    )


def softLight(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    # Approximation proposée dans la référence Deep Sky Colors.
    return np.where(
        foreground <= 0.5,
        background * (foreground + 0.5),
        1 - (1 - background) * (1.5 - foreground),
    )


def vividLight(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return np.where(
        foreground <= 0.5,
        colorDodge(background, 2 * foreground),
        colorBurn(background, 2 * foreground - 1),
    )


def pinLight(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return np.where(
        foreground <= 0.5,
        np.minimum(background, 2 * foreground),
        np.maximum(background, 2 * foreground - 1),
    )


# Chaque mode pointe vers sa formule : b = fond, f = nouveau calque.
blendFunctions = {
    "normal": lambda b, f: f,
    "darken": np.minimum,
    "multiply": np.multiply,
    "color_burn": colorBurn,
    "linear_burn": lambda b, f: b + f - 1,
    "lighten": np.maximum,
    "screen": lambda b, f: 1 - (1 - b) * (1 - f),
    "color_dodge": colorDodge,
    "linear_dodge": np.add,
    "overlay": overlay,
    "soft_light": softLight,
    "hard_light": lambda b, f: overlay(f, b),
    "vivid_light": vividLight,
    "linear_light": lambda b, f: b + 2 * f - 1,
    "pin_light": pinLight,
    "difference": lambda b, f: np.abs(b - f),
    "exclusion": lambda b, f: b + f - 2 * b * f,
}


def blend_colors(background: np.ndarray, foreground: np.ndarray, mode: str) -> np.ndarray:
    """Applique le mode de fusion aux couleurs RGB, sans modifier les entrées."""
    try:
        blendFunction = blendFunctions[mode]
    except KeyError as error:
        raise ValueError(f"Mode de blend inconnu : {mode!r}.") from error

    # Calculer entre 0 et 1 en flottants, puis revenir aux pixels de 0 à 255.
    background = background.astype(np.float32) / 255
    foreground = foreground.astype(np.float32) / 255
    blended = blendFunction(background, foreground)
    return np.clip(blended, 0, 1) * 255


def compose(layers: list[Layer]) -> np.ndarray:
    """Superpose les calques dans l'ordre de la liste, du fond vers le dessus.

    Les calques ont les mêmes dimensions, avec des pixels RGB ou RGBA de
    0 à 255 et des opacités de 0 à 1. Chaque calque indique son mode de blend.
    Le résultat est une image RGB en uint8 sur un fond noir ; les calques
    ne sont pas modifiés.
    """
    if not layers:
        raise ValueError("Il faut au moins un calque.")

    height, width = layers[0].pixels.shape[:2]
    # Le calcul en flottants conserve les nuances pendant les mélanges.
    result = np.zeros((height, width, 3), dtype=np.float32)

    for index, layer in enumerate(layers, start=1):
        pixels = layer.pixels
        if pixels.ndim != 3 or pixels.shape[2] not in (3, 4):
            raise ValueError("Chaque calque doit être RGB ou RGBA.")
        if not 0 <= layer.opacity <= 1:
            raise ValueError("L'opacité doit être comprise entre 0 et 1.")

        alpha = layer.opacity
        if pixels.shape[2] == 4:
            # En RGBA, combiner l'opacité du calque avec celle de chaque pixel.
            # 3:4 garde une forme (hauteur, largeur, 1) pour appliquer le même
            # coefficient aux trois canaux RGB grâce au broadcasting NumPy.
            alpha = alpha * pixels[:, :, 3:4].astype(np.float32) / 255

        # Le blend définit les couleurs, puis l'alpha dose leur contribution.
        try:
            blended = blend_colors(result, pixels[:, :, :3], layer.blend)
        except ValueError as error:
            raise ValueError(f"Calque {index} : {error}") from error
        result = (1 - alpha) * result + alpha * blended

    # Arrondir une seule fois, après toutes les superpositions.
    return np.clip(np.rint(result), 0, 255).astype(np.uint8)

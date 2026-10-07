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


BLEND_MODES = (
    "normal", "darken", "multiply", "color_burn", "linear_burn", "lighten",
    "screen", "color_dodge", "linear_dodge", "overlay", "soft_light",
    "hard_light", "vivid_light", "linear_light", "pin_light", "difference", "exclusion",
)


def _color_burn(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    # Si le diviseur vaut zéro, le résultat est noir (sauf sur un fond blanc).
    ratio = np.divide(1 - background, foreground,
                      out=np.ones_like(background), where=foreground != 0)
    return np.where(background == 1, 1, 1 - np.clip(ratio, 0, 1))


def _color_dodge(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    # Si le diviseur vaut zéro, le résultat est blanc (sauf sur un fond noir).
    ratio = np.divide(background, 1 - foreground,
                      out=np.ones_like(background), where=foreground != 1)
    return np.where(background == 0, 0, np.clip(ratio, 0, 1))


def blend_colors(background: np.ndarray, foreground: np.ndarray, mode: str) -> np.ndarray:
    """Calcule les couleurs du mélange (RGB de 0 à 255), sans l'opacité.

    Les entrées ne sont pas modifiées. Le calcul en flottants évite les
    débordements des opérations sur les tableaux uint8.
    """
    # Les formules de la référence utilisent des couleurs entre 0 et 1.
    background = background.astype(np.float32) / 255
    foreground = foreground.astype(np.float32) / 255

    if mode == "normal":
        blended = foreground
    elif mode == "darken":
        blended = np.minimum(background, foreground)
    elif mode == "multiply":
        blended = background * foreground
    elif mode == "color_burn":
        blended = _color_burn(background, foreground)
    elif mode == "linear_burn":
        blended = background + foreground - 1
    elif mode == "lighten":
        blended = np.maximum(background, foreground)
    elif mode == "screen":
        blended = 1 - (1 - background) * (1 - foreground)
    elif mode == "color_dodge":
        blended = _color_dodge(background, foreground)
    elif mode == "linear_dodge":
        blended = background + foreground
    elif mode == "overlay":
        blended = np.where(background <= 0.5,
                           2 * background * foreground,
                           1 - 2 * (1 - background) * (1 - foreground))
    elif mode == "soft_light":
        # Approximation proposée dans la référence Deep Sky Colors.
        blended = np.where(foreground <= 0.5,
                           background * (foreground + 0.5),
                           1 - (1 - background) * (1.5 - foreground))
    elif mode == "hard_light":
        blended = np.where(foreground <= 0.5,
                           2 * background * foreground,
                           1 - 2 * (1 - background) * (1 - foreground))
    elif mode == "vivid_light":
        # Reprend les deux branches du tableau fourni en référence.
        blended = np.where(foreground <= 0.5,
                           _color_dodge(background, 2 * foreground),
                           _color_burn(background, 2 * foreground - 1))
    elif mode == "linear_light":
        blended = background + 2 * foreground - 1
    elif mode == "pin_light":
        blended = np.where(foreground <= 0.5,
                           np.minimum(background, 2 * foreground),
                           np.maximum(background, 2 * foreground - 1))
    elif mode == "difference":
        blended = np.abs(background - foreground)
    elif mode == "exclusion":
        blended = background + foreground - 2 * background * foreground
    else:
        available = ", ".join(BLEND_MODES)
        raise ValueError(f"Mode de blend inconnu : {mode!r}. Modes disponibles : {available}.")

    # Borner avant l'opacité empêche un mode de produire des couleurs hors plage.
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

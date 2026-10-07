"""Modes de fusion : les formules travaillent sur des couleurs entre 0 et 1.

blendColors reçoit des pixels RGB entre 0 et 255, les normalise, applique
la formule choisie et renvoie les couleurs de 0 à 255, sans l'opacité.
"""

import numpy as np


def normal(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return foreground


def darken(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return np.minimum(background, foreground)


def multiply(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return background * foreground


def linearBurn(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return background + foreground - 1


def lighten(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return np.maximum(background, foreground)


def screen(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return 1 - (1 - background) * (1 - foreground)


def linearDodge(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return background + foreground


def hardLight(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return overlay(foreground, background)


def linearLight(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return background + 2 * foreground - 1


def difference(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return np.abs(background - foreground)


def exclusion(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return background + foreground - 2 * background * foreground


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


# Les clés gardent les noms utilisés dans le YAML.
blendFunctions = {
    "normal": normal,
    "darken": darken,
    "multiply": multiply,
    "color_burn": colorBurn,
    "linear_burn": linearBurn,
    "lighten": lighten,
    "screen": screen,
    "color_dodge": colorDodge,
    "linear_dodge": linearDodge,
    "overlay": overlay,
    "soft_light": softLight,
    "hard_light": hardLight,
    "vivid_light": vividLight,
    "linear_light": linearLight,
    "pin_light": pinLight,
    "difference": difference,
    "exclusion": exclusion,
}


def blendColors(background: np.ndarray, foreground: np.ndarray, mode: str) -> np.ndarray:
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

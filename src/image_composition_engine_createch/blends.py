"""Formules des modes de fusion, d'après le tableau Deep Sky Colors.

Chaque fonction reçoit le fond et le calque du dessus, en RGB entre 0 et 1,
et renvoie leur mélange. `compose` borne ce mélange puis applique l'opacité.
Pour ajouter un mode, écrire sa fonction puis lui donner un nom dans `BLENDS`.
"""

import numpy as np


def normal(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return foreground


def darken(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return np.minimum(background, foreground)


def multiply(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return background * foreground


def colorBurn(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    # Si le diviseur vaut zéro, le résultat est noir (sauf sur un fond blanc).
    ratio = np.divide(1 - background, foreground,
                      out=np.ones_like(background), where=foreground != 0)
    return np.where(background == 1, 1, 1 - np.clip(ratio, 0, 1))


def linearBurn(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return background + foreground - 1


def lighten(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return np.maximum(background, foreground)


def screen(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return 1 - (1 - background) * (1 - foreground)


def colorDodge(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    # Si le diviseur vaut zéro, le résultat est blanc (sauf sur un fond noir).
    ratio = np.divide(background, 1 - foreground,
                      out=np.ones_like(background), where=foreground != 1)
    return np.where(background == 0, 0, np.clip(ratio, 0, 1))


def linearDodge(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return background + foreground


def overlay(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return np.where(
        background <= 0.5,
        2 * background * foreground,
        1 - 2 * (1 - background) * (1 - foreground),
    )


def softLight(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    # Approximation proposée par la référence, différente de Photoshop.
    return np.where(
        foreground <= 0.5,
        background * (foreground + 0.5),
        1 - (1 - background) * (1.5 - foreground),
    )


def hardLight(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    # Overlay en inversant les rôles du fond et du dessus.
    return overlay(foreground, background)


def vividLight(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return np.where(
        foreground <= 0.5,
        colorDodge(background, 2 * foreground),
        colorBurn(background, 2 * foreground - 1),
    )


def linearLight(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return background + 2 * foreground - 1


def pinLight(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return np.where(
        foreground <= 0.5,
        np.minimum(background, 2 * foreground),
        np.maximum(background, 2 * foreground - 1),
    )


def difference(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return np.abs(background - foreground)


def exclusion(background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
    return background + foreground - 2 * background * foreground


# Noms utilisables pour `blend` dans le YAML.
BLENDS = {
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

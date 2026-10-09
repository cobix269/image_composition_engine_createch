"""Noms utilisables dans le YAML : `name` d'un filtre et `blend` d'un calque."""

from .classes import filters
from .classes import importedFilters as imported
from .utils import blends

FILTERS = {
    "normal": filters.Normal,
    "grayscale": filters.Grayscale,
    "swapBG": filters.SwapBG,
    "brightness": filters.Brightness,
    "contrast": filters.Contrast,
    "blur": filters.Blur,
    "gaussianBlur": filters.GaussianBlur,
    "blackBorder": filters.BlackBorder,
    "invert": filters.Invert,
    "sepia": filters.Sepia,
    # Filtres de l'autre groupe, préfixés pour ne pas masquer les nôtres.
    "importedNormal": imported.normal,
    "importedBlur": imported.blur,
    "importedGaussianBlur": imported.gaussianblur,
    "importedGrayscale": imported.Grayscale,
    "importedSepia": imported.Sepia,
    "importedBlackBorder": imported.blackborder,
}

BLENDS = {
    "normal": blends.normal,
    "darken": blends.darken,
    "multiply": blends.multiply,
    "color_burn": blends.colorBurn,
    "linear_burn": blends.linearBurn,
    "lighten": blends.lighten,
    "screen": blends.screen,
    "color_dodge": blends.colorDodge,
    "linear_dodge": blends.linearDodge,
    "overlay": blends.overlay,
    "soft_light": blends.softLight,
    "hard_light": blends.hardLight,
    "vivid_light": blends.vividLight,
    "linear_light": blends.linearLight,
    "pin_light": blends.pinLight,
    "difference": blends.difference,
    "exclusion": blends.exclusion,
}

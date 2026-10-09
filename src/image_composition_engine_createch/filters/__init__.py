"""Filtres utilisables dans le YAML, sous les noms donnés dans `FILTERS`."""

from . import imported, ours

FILTERS = {
    "normal": ours.Normal,
    "grayscale": ours.Grayscale,
    "swapBG": ours.SwapBG,
    "brightness": ours.Brightness,
    "contrast": ours.Contrast,
    "blur": ours.Blur,
    "gaussianBlur": ours.GaussianBlur,
    "blackBorder": ours.BlackBorder,
    "invert": ours.Invert,
    "sepia": ours.Sepia,
    # Filtres de l'autre groupe, préfixés pour ne pas masquer les nôtres.
    "importedNormal": imported.normal,
    "importedBlur": imported.blur,
    "importedGaussianBlur": imported.gaussianblur,
    "importedGrayscale": imported.Grayscale,
    "importedSepia": imported.Sepia,
    "importedBlackBorder": imported.blackborder,
}

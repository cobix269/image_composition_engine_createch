"""Création des calques, application des filtres et composition."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from ..classes import Layer


def applyFilters(layer: Layer, filterConfigs: list[dict], layerNumber: int) -> Layer:
    """Applique les filtres dans l'ordre et précise le contexte des erreurs."""
    for filterConfig in filterConfigs:
        name = filterConfig["name"]
        filterClass = layer.FILTERS[name]
        try:
            imageFilter = filterClass(**filterConfig.get("params", {}))
            layer.applyFilter(imageFilter)
        except (ValueError, TypeError) as error:
            raise ValueError(f"Calque {layerNumber}, filtre '{name}' : {error}") from error
    return layer


def createLayers(config: dict, basePath: str | Path) -> list[Layer]:
    """Crée les calques du YAML validé, avec leurs filtres, dans le même ordre."""
    basePath = Path(basePath)
    layers = []
    for layerNumber, layerConfig in enumerate(config["layers"], start=1):
        layer = Layer(
            src=basePath / layerConfig["image"],
            opacity=layerConfig.get("opacity", 1.0),
            blend=layerConfig.get("blend", "normal"),
        )
        applyFilters(layer, layerConfig.get("filters", []), layerNumber)
        layers.append(layer)
    return layers


def blendColors(background: np.ndarray, foreground: np.ndarray, mode: str) -> np.ndarray:
    """Mélange les couleurs RGB entre 0 et 255 ; l'opacité reste dans compose."""
    try:
        imageBlend = Layer.BLENDS[mode]()
    except KeyError as error:
        raise ValueError(f"Mode de blend inconnu : {mode!r}.") from error

    background = background.astype(np.float32) / 255
    foreground = foreground.astype(np.float32) / 255
    return np.clip(imageBlend.apply(background, foreground), 0, 1) * 255


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
            blended = blendColors(result, pixels[:, :, :3], layer.blend)
        except ValueError as error:
            raise ValueError(f"Calque {index} : {error}") from error
        result = (1 - alpha) * result + alpha * blended

    # Arrondir une seule fois, après toutes les superpositions.
    return np.clip(np.rint(result), 0, 255).astype(np.uint8)

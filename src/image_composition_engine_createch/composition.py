"""Création des calques décrits par le YAML, puis composition."""

from pathlib import Path

import numpy as np

from .blends import BLENDS
from .config import LayerConfig
from .layer import Layer


def createLayers(configs: list[LayerConfig], directory: Path) -> list[Layer]:
    """Charge chaque image, relative à `directory`, et lui applique ses filtres."""
    layers = []
    for number, config in enumerate(configs, start=1):
        try:
            layer = Layer.fromFile(directory / config.image, config.opacity, config.blend)
            for filterConfig in config.filters:
                layer.applyFilter(filterConfig.create())
        except (OSError, ValueError) as error:
            raise ValueError(f"Calque {number}, {error}") from error
        layers.append(layer)
    return layers


def compose(layers: list[Layer]) -> np.ndarray:
    """Superpose les calques du fond vers le dessus, sur un fond noir.

    Le blend donne la couleur mélangée, puis l'opacité du calque multipliée
    par l'alpha de chaque pixel dose sa contribution. Renvoie une image RGB
    entre 0 et 1 ; les calques ne sont pas modifiés.
    """
    result = np.zeros_like(layers[0].rgb)
    for layer in layers:
        blended = np.clip(BLENDS[layer.blend](result, layer.rgb), 0, 1)
        alpha = layer.opacity * layer.alpha
        result = (1 - alpha) * result + alpha * blended
    return result

"""Charge les calques, applique leurs filtres et affiche la composition."""

from pathlib import Path
import sys

# Autoriser aussi `python main.py` depuis le dossier du code.
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "image_composition_engine_createch"

from .classes import Layer
from .parseYaml import read_yaml
from .utils import compose, show_from_array


def main() -> None:
    config = read_yaml()
    script_dir = Path(__file__).resolve().parent
    layers = []

    for layer_number, layer_config in enumerate(config["layers"], start=1):
        layer = Layer(
            src=script_dir / layer_config["image"],
            opacity=layer_config.get("opacity", 1.0),
            blend=layer_config.get("blend", "normal"),
        )

        # Créer les instances dans l'ordre du YAML, puis appliquer chaque filtre.
        for filter_config in layer_config.get("filters", []):
            name = filter_config["name"]
            filterClass = Layer.FILTERS[name]
            try:
                imageFilter = filterClass(**filter_config["params"])
                layer.applyFilter(imageFilter)
            except (ValueError, TypeError) as error:
                raise ValueError(f"Calque {layer_number}, filtre '{name}' : {error}") from error

        layers.append(layer)

    show_from_array(compose(layers))


if __name__ == "__main__":
    main()

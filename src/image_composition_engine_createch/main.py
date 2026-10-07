"""Charge les calques, applique leurs filtres et affiche la composition."""

from pathlib import Path

from image_composition_engine_createch.classes import Layer
from image_composition_engine_createch.parseYaml import read_yaml
from image_composition_engine_createch.utils import compose, show_from_array


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

        # Chaque filtre reçoit le calque, puis les paramètres du YAML par nom.
        for filter_config in layer_config.get("filters", []):
            name = filter_config["name"]
            filter_function = Layer.FILTERS[name]
            try:
                layer = filter_function(layer, **filter_config["params"])
            except (ValueError, TypeError) as error:
                raise ValueError(f"Calque {layer_number}, filtre '{name}' : {error}") from error

        layers.append(layer)

    show_from_array(compose(layers))


if __name__ == "__main__":
    main()

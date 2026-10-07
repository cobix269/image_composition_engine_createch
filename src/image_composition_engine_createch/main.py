from pathlib import Path

from parseYaml import read_yaml
from classes import Layer
from utils import show_from_array, compose

config = read_yaml()
script_dir = Path(__file__).resolve().parent
layers = []

for layer_config in config["layers"]:
    layer = Layer(
        src=script_dir / layer_config["image"],
        opacity=layer_config.get("opacity", 1.0),
    )

    # Appliquer les filtres dans l'ordre où ils apparaissent dans le YAML.
    for filter_config in layer_config.get("filters", []):
        filter_function = Layer.FILTERS[filter_config["name"]]
        layer = filter_function(layer, **filter_config.get("params", {}))

    layers.append(layer)

# Superposer les calques dans le même ordre, avec leur opacité.
img = compose(layers)
show_from_array(img)

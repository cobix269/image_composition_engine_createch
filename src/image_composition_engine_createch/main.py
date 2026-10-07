"""Charge les calques, applique leurs filtres et affiche la composition."""

from pathlib import Path
import sys

# Autoriser aussi `python main.py` depuis le dossier du code.
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "image_composition_engine_createch"

from .utils.parseYaml import readYaml
from .utils.imageIO import showFromArray
from .utils.composition import compose, createLayers


def main() -> None:
    config = readYaml()
    layers = createLayers(config, Path(__file__).resolve().parent)
    showFromArray(compose(layers))


if __name__ == "__main__":
    main()

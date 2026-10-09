"""Point d'entrée : lit conf.yml, crée les calques et affiche leur composition."""

import sys
from pathlib import Path

# Autoriser aussi `python main.py` depuis le dossier du code.
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "image_composition_engine_createch"

from .utils.composition import compose, createLayers
from .utils.imageIO import showFromArray
from .utils.parseYaml import readConfig

# Les chemins d'images du YAML sont relatifs au dossier du paquet.
PACKAGE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = PACKAGE_DIR.parents[1] / "conf.yml"


def main() -> None:
    layers = createLayers(readConfig(CONFIG_PATH), PACKAGE_DIR)
    showFromArray(compose(layers))


if __name__ == "__main__":
    main()

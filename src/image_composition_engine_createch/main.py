"""Point d'entrée : lit conf.yml, crée les calques et affiche leur composition."""

from pathlib import Path

from .composition import compose, createLayers
from .config import readConfig
from .imageIO import showFromArray

# conf.yml est à la racine du dépôt ; ses chemins d'images sont relatifs à lui.
CONFIG_PATH = Path(__file__).resolve().parents[2] / "conf.yml"


def main() -> None:
    layers = createLayers(readConfig(CONFIG_PATH), CONFIG_PATH.parent)
    showFromArray(compose(layers))


if __name__ == "__main__":
    main()

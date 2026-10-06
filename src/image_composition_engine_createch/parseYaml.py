
from pathlib import Path

import yaml

def read_yaml(path: str | Path | None = None) -> list[str]:
    """Lit les chemins d'images, relatifs au dossier du fichier YAML."""
    # Le chemin par défaut ne dépend pas du dossier ouvert dans le terminal.
    config_path = Path(path) if path is not None else Path(__file__).resolve().parents[2] / "conf.yml"
    with config_path.open() as f:
        config = yaml.safe_load(f)

    images = [config_path.parent / layer["image"] for layer in config["layers"]]
    missing = [str(image.resolve()) for image in images if not image.is_file()]
    if missing:
        raise FileNotFoundError(
            "Images introuvables :\n" + "\n".join(missing)
            + "\nCorrige les chemins dans " + str(config_path.resolve())
        )
    return [str(image.resolve()) for image in images]

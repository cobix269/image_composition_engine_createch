
from pathlib import Path

import yaml

def read_yaml(path: str | Path | None = None) -> dict:
    """Renvoie la configuration YAML, avec les calques et leurs filtres."""
    script_dir = Path(__file__).resolve().parent
    # Le chemin par défaut ne dépend pas du dossier ouvert dans le terminal.
    config_path = Path(path) if path is not None else script_dir.parents[1] / "conf.yml"
    with config_path.open() as f:
        config = yaml.safe_load(f)

    return config

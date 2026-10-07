from dataclasses import asdict
from pathlib import Path

import yaml
from PIL import Image
from pydantic import ValidationError

from ..classes import BlendParams, Layer

SCRIPT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = SCRIPT_DIR.parents[1] / "conf.yml"


def validateStructure(config: dict) -> None:
    """Vérifie que le YAML contient une liste non vide de calques."""
    layers = config.get("layers") if isinstance(config, dict) else None
    if not isinstance(layers, list) or not layers:
        raise ValueError("La configuration doit contenir une liste 'layers' non vide.")
    if any(not isinstance(layer, dict) for layer in layers):
        raise ValueError("Chaque calque doit être un dictionnaire.")


def validateImages(config: dict) -> None:
    """Vérifie que les images sont lisibles."""
    for layerNumber, layer in enumerate(config["layers"], start=1):
        imagePath = layer.get("image")
        if not isinstance(imagePath, str) or not imagePath:
            raise ValueError(f"Calque {layerNumber} : chemin d'image manquant ou invalide.")

        try:
            with Image.open(SCRIPT_DIR / imagePath) as image:
                image.load()
        except (OSError, ValueError, SyntaxError) as error:
            raise ValueError(
                f"Calque {layerNumber} : image '{imagePath}' introuvable ou illisible."
            ) from error


def validateOpacity(config: dict) -> None:
    """Vérifie les opacités ; une opacité absente vaut 1, comme dans main.py."""
    for layerNumber, layer in enumerate(config["layers"], start=1):
        opacity = layer.get("opacity", 1.0)
        if type(opacity) not in (int, float) or not 0 <= opacity <= 1:
            raise ValueError(
                f"Calque {layerNumber} : l'opacité doit être un nombre entre 0 et 1."
            )


def validateBlendModes(config: dict) -> None:
    """Valide les modes de fusion avec Pydantic ; le défaut est normal."""
    for layerNumber, layer in enumerate(config["layers"], start=1):
        try:
            validated = BlendParams.model_validate({"blend": layer.get("blend", "normal")})
        except ValidationError as error:
            message = error.errors()[0]["msg"]
            raise ValueError(f"Calque {layerNumber}, blend : {message}.") from error
        layer["blend"] = validated.blend


def validateFilterParams(name: str, params: dict, layerNumber: int) -> dict:
    """Instancie la dataclass Pydantic et récupère ses paramètres validés."""
    if not isinstance(params, dict):
        raise ValueError(
            f"Calque {layerNumber}, filtre '{name}' : params doit être un dictionnaire."
        )
    try:
        imageFilter = Layer.FILTERS[name](**params)
    except ValidationError as error:
        detail = error.errors()[0]
        parameter = ".".join(map(str, detail["loc"])) or "params"
        raise ValueError(
            f"Calque {layerNumber}, filtre '{name}', {parameter} : {detail['msg']}."
        ) from error
    except TypeError as error:
        raise ValueError(
            f"Calque {layerNumber}, filtre '{name}' : {error}."
        ) from error
    return asdict(imageFilter)


def validateFilters(config: dict) -> None:
    """Vérifie les noms des filtres et leurs paramètres."""
    for layerNumber, layer in enumerate(config["layers"], start=1):
        filters = layer.get("filters", [])
        if not isinstance(filters, list):
            raise ValueError(f"Calque {layerNumber} : filters doit être une liste.")
        for filterConfig in filters:
            filterName = filterConfig.get("name") if isinstance(filterConfig, dict) else None
            if not isinstance(filterName, str):
                raise ValueError(f"Calque {layerNumber} : chaque filtre doit avoir un nom.")
            if filterName not in Layer.FILTERS:
                raise ValueError(
                    f"Calque {layerNumber} : filtre inconnu '{filterName}'. "
                    f"Filtres disponibles : {', '.join(Layer.FILTERS)}."
                )
            filterConfig["params"] = validateFilterParams(
                filterName, filterConfig.get("params", {}), layerNumber
            )


def readYaml(path: str | Path | None = None) -> dict:
    """Charge le YAML et valide les images, les opacités, les blends et les filtres."""
    if path is None:
        path = DEFAULT_CONFIG_PATH

    with Path(path).open(encoding="utf-8") as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as error:
            raise ValueError(f"Syntaxe YAML invalide dans '{path}' : {error}") from error

    validateStructure(config)
    validateOpacity(config)
    validateBlendModes(config)
    validateFilters(config)
    validateImages(config)
    return config

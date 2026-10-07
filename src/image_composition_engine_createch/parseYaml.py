from pathlib import Path

import yaml
from PIL import Image
from pydantic import ValidationError

from classes import BlendParams, Layer

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = SCRIPT_DIR.parents[1] / "conf.yml"


def validate_structure(config: dict) -> None:
    """Vérifie que le YAML contient une liste non vide de calques."""
    if not isinstance(config, dict) or not isinstance(config.get("layers"), list) or not config["layers"]:
        raise ValueError("La configuration doit contenir une liste 'layers' non vide.")
    if any(not isinstance(layer, dict) for layer in config["layers"]):
        raise ValueError("Chaque calque doit être un dictionnaire.")


def validate_images(config: dict) -> None:
    """Vérifie que les images sont lisibles."""
    for layer_number, layer in enumerate(config["layers"], start=1):
        image_path = layer.get("image")
        if not isinstance(image_path, str) or not image_path:
            raise ValueError(f"Calque {layer_number} : chemin d'image manquant ou invalide.")

        try:
            with Image.open(SCRIPT_DIR / image_path) as image:
                image.load()
        except (OSError, ValueError, SyntaxError) as error:
            raise ValueError(
                f"Calque {layer_number} : image '{image_path}' introuvable ou illisible."
            ) from error


def validate_opacity(config: dict) -> None:
    """Vérifie les opacités ; une opacité absente vaut 1, comme dans main.py."""
    for layer_number, layer in enumerate(config["layers"], start=1):
        opacity = layer.get("opacity", 1.0)
        if type(opacity) not in (int, float) or not 0 <= opacity <= 1:
            raise ValueError(
                f"Calque {layer_number} : l'opacité doit être un nombre entre 0 et 1."
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


def validate_filter_params(name: str, params: dict, layer_number: int) -> dict:
    """Valide les paramètres avec le modèle Pydantic associé au filtre."""
    model = Layer.FILTER_PARAMS[Layer.FILTERS[name]]
    try:
        validated = model.model_validate(params)
    except ValidationError as error:
        detail = error.errors()[0]
        parameter = ".".join(map(str, detail["loc"])) or "params"
        raise ValueError(
            f"Calque {layer_number}, filtre '{name}', {parameter} : {detail['msg']}."
        ) from error
    return validated.model_dump()


def validate_filters(config: dict) -> None:
    """Vérifie les noms des filtres et leurs paramètres."""
    for layer_number, layer in enumerate(config["layers"], start=1):
        filters = layer.get("filters", [])
        if not isinstance(filters, list):
            raise ValueError(f"Calque {layer_number} : filters doit être une liste.")
        for filter_config in filters:
            if not isinstance(filter_config, dict) or not isinstance(filter_config.get("name"), str):
                raise ValueError(f"Calque {layer_number} : chaque filtre doit avoir un nom.")
            filter_name = filter_config["name"]
            if filter_name not in Layer.FILTERS:
                raise ValueError(
                    f"Calque {layer_number} : filtre inconnu '{filter_name}'. "
                    f"Filtres disponibles : {', '.join(Layer.FILTERS)}."
                )
            filter_config["params"] = validate_filter_params(
                filter_name, filter_config.get("params", {}), layer_number
            )


def read_yaml(path: str | Path | None = None) -> dict:
    """Charge le YAML et valide les images, les opacités, les blends et les filtres."""
    if path is None:
        path = DEFAULT_CONFIG_PATH

    with Path(path).open() as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as error:
            raise ValueError(f"Syntaxe YAML invalide dans '{path}' : {error}") from error

    validate_structure(config)
    validate_opacity(config)
    validateBlendModes(config)
    validate_filters(config)
    validate_images(config)
    return config

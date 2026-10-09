"""Lecture et validation du YAML de composition."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from ..classes.base import Filter
from ..registry import BLENDS, FILTERS


class FilterConfig(BaseModel):
    """Entrée de `filters` : un nom de filtre et les paramètres de sa classe."""

    model_config = ConfigDict(strict=True, extra="forbid")

    name: str
    params: dict[str, Any] = {}

    @field_validator("name")
    @classmethod
    def knownFilter(cls, name: str) -> str:
        if name not in FILTERS:
            available = ", ".join(FILTERS)
            raise ValueError(f"filtre inconnu {name!r}. Filtres disponibles : {available}")
        return name

    def create(self) -> Filter:
        """Instancie le filtre ; sa dataclass Pydantic valide les paramètres."""
        try:
            return FILTERS[self.name](**self.params)
        except ValidationError as error:
            raise ValueError(f"filtre {self.name!r}, {describe(error)}") from error


class LayerConfig(BaseModel):
    """Entrée de `layers` ; les champs absents prennent ces valeurs par défaut."""

    model_config = ConfigDict(strict=True, extra="forbid")

    image: str
    opacity: float = Field(default=1.0, ge=0, le=1)
    blend: str = "normal"
    filters: list[FilterConfig] = []

    @field_validator("blend")
    @classmethod
    def knownBlend(cls, blend: str) -> str:
        if blend not in BLENDS:
            available = ", ".join(BLENDS)
            raise ValueError(f"mode inconnu {blend!r}. Modes disponibles : {available}")
        return blend


def readConfig(path: Path) -> list[LayerConfig]:
    """Lit le YAML et valide ses calques, du fond vers le dessus."""
    try:
        config = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ValueError(f"Syntaxe YAML invalide dans '{path}' : {error}") from error

    entries = config.get("layers") if isinstance(config, dict) else None
    if not isinstance(entries, list) or not entries:
        raise ValueError("La configuration doit contenir une liste 'layers' non vide.")

    layers = []
    for number, entry in enumerate(entries, start=1):
        try:
            layers.append(LayerConfig.model_validate(entry))
        except ValidationError as error:
            raise ValueError(f"Calque {number}, {describe(error)}") from error
    return layers


def describe(error: ValidationError) -> str:
    """Résume la première erreur Pydantic en « champ : message »."""
    detail = error.errors()[0]
    field = ".".join(map(str, detail["loc"]))
    message = detail["msg"].removeprefix("Value error, ")
    return f"{field} : {message}" if field else message

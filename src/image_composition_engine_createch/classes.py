from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .blend import blendFunctions
from .filters import (
    black_border,
    blur,
    brightness,
    contrast,
    gaussianBlur,
    grayscale,
    invert,
    sepia,
    swapBG,
)
from .utils import array_from_file


class BlendParams(BaseModel):
    """Définit les modes de fusion acceptés et le mode par défaut."""
    model_config = ConfigDict(strict=True, extra="forbid")
    blend: str = "normal"

    @field_validator("blend")
    @classmethod
    def validate_blend(cls, mode: str) -> str:
        if mode not in blendFunctions:
            available = ", ".join(blendFunctions)
            raise ValueError(f"Mode de blend inconnu : {mode!r}. Modes disponibles : {available}.")
        return mode


class FilterParams(BaseModel):
    """Base commune : types stricts, nombres finis, aucun paramètre inconnu."""
    model_config = ConfigDict(strict=True, extra="forbid", allow_inf_nan=False)


class BrightnessParams(FilterParams):
    value: float = Field(ge=0)


class ContrastParams(FilterParams):
    value: float = Field(gt=0, le=5)


class BlurParams(FilterParams):
    radius: int = Field(ge=0)


class GaussianBlurParams(FilterParams):
    window: int = Field(ge=1)
    sigma: float = Field(gt=0)


class BlackBorderParams(FilterParams):
    thickness: int = Field(default=10, ge=0)


class Layer:
    """Calque RGBA dont les filtres modifient les pixels et renvoient le calque."""

    # Associe chaque nom accepté dans le YAML à sa fonction.
    FILTERS = {
        "grayscale": grayscale,
        "swapBG": swapBG,
        "brightness": brightness,
        "contrast": contrast,
        "blur": blur,
        "gaussianBlur": gaussianBlur,
        "black_border": black_border,
        "invert": invert,
        "sepia": sepia,
    }

    # Associe chaque fonction au modèle qui décrit ses paramètres valides.
    # FilterParams seul correspond aux filtres sans paramètres.
    # Un filtre échangé peut être enregistré sans modèle de validation.
    FILTER_PARAMS = {
        grayscale: FilterParams,
        swapBG: FilterParams,
        brightness: BrightnessParams,
        contrast: ContrastParams,
        blur: BlurParams,
        gaussianBlur: GaussianBlurParams,
        black_border: BlackBorderParams,
        invert: FilterParams,
        sepia: FilterParams,
    }

    def __init__(self, src: str | Path, opacity: float = 1.0, blend: str = "normal") -> None:
        self.pixels = array_from_file(src, "RGBA")
        self.opacity: float = opacity
        self.blend: str = BlendParams(blend=blend).blend

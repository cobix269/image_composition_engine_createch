from PIL import Image
import numpy as np
from dataclasses import dataclass
import scipy.ndimage
from filters import grayscale, swapBG, brightness, contrast, blur, gaussianBlur, black_border, invert, sepia
from utils import array_from_file
from constants import R,G,B,A
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class BlendParams(BaseModel):
    """Définit les modes de fusion acceptés et le mode par défaut."""
    model_config = ConfigDict(strict=True, extra="forbid")
    blend: Literal[
        "normal", "darken", "multiply", "color_burn", "linear_burn",
        "lighten", "screen", "color_dodge", "linear_dodge", "overlay",
        "soft_light", "hard_light", "vivid_light", "linear_light",
        "pin_light", "difference", "exclusion",
    ] = "normal"


class FilterParams(BaseModel):
    """Base commune : types stricts, nombres finis, aucun paramètre inconnu."""
    model_config = ConfigDict(strict=True, extra="forbid", allow_inf_nan=False)


class BrightnessParams(FilterParams):
    value: float


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

    def __init__(self, src: str, opacity: float = 0.1, blend: str = "normal") -> None:
        
        self.pixels = array_from_file(src, "RGBA")
        self.opacity: float = opacity
        self.blend: str = BlendParams(blend=blend).blend

    def _grayscale(self) -> Layer:
        return grayscale(self)

    def _swapBG(self) -> Layer:
        return swapBG(self)

    def _brightness(self, value: float) -> Layer:
        return brightness(self)

    def _contrast(self, value: float) -> Layer:
        return contrast(self)
    
    def _blur(self, radius: int) -> Layer:
        return blur(self)

    def _black_border(self, thickness: int = 10) -> Layer:
        return black_border(self)
    
    def _invert(self) -> Layer:
        return invert(self)

    def _sepia(self) -> Layer:
        return sepia(self)

    def _gaussianBlur(self, window: int, sigma: float) -> Layer:
        return gaussianBlur(self, window, sigma)

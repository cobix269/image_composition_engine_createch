"""Classes de fusion RGB entre 0 et 1 ; l'opacité est gérée par compose."""

import numpy as np
from pydantic import BaseModel, ConfigDict, field_validator
from pydantic.dataclasses import dataclass

from .base import Blend


@dataclass
class Normal(Blend):
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        return foreground


@dataclass
class Darken(Blend):
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        return np.minimum(background, foreground)


@dataclass
class Multiply(Blend):
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        return background * foreground


@dataclass
class LinearBurn(Blend):
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        return background + foreground - 1


@dataclass
class Lighten(Blend):
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        return np.maximum(background, foreground)


@dataclass
class Screen(Blend):
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        return 1 - (1 - background) * (1 - foreground)


@dataclass
class LinearDodge(Blend):
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        return background + foreground


@dataclass
class HardLight(Blend):
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        return Overlay().apply(foreground, background)


@dataclass
class LinearLight(Blend):
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        return background + 2 * foreground - 1


@dataclass
class Difference(Blend):
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        return np.abs(background - foreground)


@dataclass
class Exclusion(Blend):
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        return background + foreground - 2 * background * foreground


@dataclass
class ColorBurn(Blend):
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        # Si le diviseur vaut zéro, le résultat est noir (sauf sur un fond blanc).
        ratio = np.divide(1 - background, foreground,
                          out=np.ones_like(background), where=foreground != 0)
        return np.where(background == 1, 1, 1 - np.clip(ratio, 0, 1))


@dataclass
class ColorDodge(Blend):
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        # Si le diviseur vaut zéro, le résultat est blanc (sauf sur un fond noir).
        ratio = np.divide(background, 1 - foreground,
                          out=np.ones_like(background), where=foreground != 1)
        return np.where(background == 0, 0, np.clip(ratio, 0, 1))


@dataclass
class Overlay(Blend):
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        return np.where(
            background <= 0.5,
            2 * background * foreground,
            1 - 2 * (1 - background) * (1 - foreground),
        )


@dataclass
class SoftLight(Blend):
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        # Approximation proposée dans la référence Deep Sky Colors.
        return np.where(
            foreground <= 0.5,
            background * (foreground + 0.5),
            1 - (1 - background) * (1.5 - foreground),
        )


@dataclass
class VividLight(Blend):
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        return np.where(
            foreground <= 0.5,
            ColorDodge().apply(background, 2 * foreground),
            ColorBurn().apply(background, 2 * foreground - 1),
        )


@dataclass
class PinLight(Blend):
    def apply(self, background: np.ndarray, foreground: np.ndarray) -> np.ndarray:
        return np.where(
            foreground <= 0.5,
            np.minimum(background, 2 * foreground),
            np.maximum(background, 2 * foreground - 1),
        )


# Les clés gardent les noms utilisés dans le YAML.
BLENDS = {
    "normal": Normal,
    "darken": Darken,
    "multiply": Multiply,
    "color_burn": ColorBurn,
    "linear_burn": LinearBurn,
    "lighten": Lighten,
    "screen": Screen,
    "color_dodge": ColorDodge,
    "linear_dodge": LinearDodge,
    "overlay": Overlay,
    "soft_light": SoftLight,
    "hard_light": HardLight,
    "vivid_light": VividLight,
    "linear_light": LinearLight,
    "pin_light": PinLight,
    "difference": Difference,
    "exclusion": Exclusion,
}


class BlendParams(BaseModel):
    """Définit les modes de fusion acceptés et le mode par défaut."""
    model_config = ConfigDict(strict=True, extra="forbid")
    blend: str = "normal"

    @field_validator("blend")
    @classmethod
    def validateBlend(cls, mode: str) -> str:
        if mode not in BLENDS:
            available = ", ".join(BLENDS)
            raise ValueError(f"Mode de blend inconnu : {mode!r}. Modes disponibles : {available}.")
        return mode

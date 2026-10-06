from PIL import Image
import numpy as np
from dataclasses import dataclass
import scipy.ndimage
from filters.py import grayscale
from utils.py import img2RGB

class Layer:
    def __init__(self, src: str, opacity: float = 0.1) -> None:
        
        self.pixels: img2RGB(src)
        self.opacity: float = opacity

    def grayscale(self) -> Layer:
        return grayscale(self)

    def swapBG(self) -> Layer:
        self.pixels[:, :, [G, B]] = self.pixels[:, :, [B, G]]
        return self

    def brightness(self, value: float) -> Layer:
        pixels = self.pixels.astype(np.float32)
        pixels += (1 - value) * (255 // 2 - pixels)
        self.pixels = np.clip(np.rint(pixels), 0, 255).astype(np.uint8)
        return self

    def contrast(self, value: float) -> Layer:
        if value <= 0 or value >5 :
            raise ValueError("Le contraste doit être entre 0 et 5")
        
        pixels = self.pixels.astype(np.float32)
        pixels += (1 - value) * (255 // 2 - pixels)
        self.pixels = np.clip(np.rint(pixels), 0, 255).astype(np.uint8)
        
        return self
    
    def blur(self, radius: int) -> Layer:
        """Flou moyen par convolution horizontale puis verticale."""
        if radius < 0:
            raise ValueError("Le rayon doit être positif ou nul.")
        if radius == 0:
            return self

        size = 2 * radius + 1
        kernel = np.ones(size, dtype=np.float32) / size
        pixels = scipy.ndimage.convolve(self.pixels, kernel[None, :, None], output=np.float32, mode="reflect")
        pixels = scipy.ndimage.convolve(pixels, kernel[:, None, None], mode="reflect")
        self.pixels = np.clip(np.rint(pixels), 0, 255).astype(np.uint8)
        return self

    def black_border(self, thickness: int = 10) -> Layer:
        """Ajoute une bordure noire sans changer la taille de l'image."""
        if thickness < 0:
            raise ValueError("L'épaisseur doit être positive ou nulle.")
        if thickness == 0:
            return self

        self.pixels[:thickness, :, :] = 0
        self.pixels[-thickness:, :, :] = 0
        self.pixels[:, :thickness, :] = 0
        self.pixels[:, -thickness:, :] = 0
        return self
    
    def invert(self) -> Layer:
        pixels = self.pixels.astype(np.float32)
        pixels = abs((pixels - 255))
        self.pixels = np.clip(np.rint(pixels), 0, 255).astype(np.uint8)
        return self

    def sepia(self) -> Layer:
        """Applique la matrice de transformation sépia classique."""
        pixels = self.pixels.astype(np.float32)
        red = pixels[:, :, R]
        green = pixels[:, :, G]
        blue = pixels[:, :, B]

        sepia = np.empty_like(pixels)
        sepia[:, :, R] = 0.393 * red + 0.769 * green + 0.189 * blue
        sepia[:, :, G] = 0.349 * red + 0.686 * green + 0.168 * blue
        sepia[:, :, B] = 0.272 * red + 0.534 * green + 0.131 * blue

        self.pixels = np.clip(np.rint(sepia), 0, 255).astype(np.uint8)
        return self

        

def compose(layers: list[Layer]) -> np.ndarray:
    """Superpose des calques RGB ou RGBA sur un fond noir."""
    if not layers:
        raise ValueError("Il faut au moins un calque.")

    height, width = layers[0].pixels.shape[:2]
    out = np.zeros((height, width, 3), dtype=np.float32)

    for layer in layers:
        pixels = layer.pixels

        if pixels.ndim != 3 or pixels.shape[2] not in (3, 4):
            raise ValueError("Chaque calque doit être RGB ou RGBA.")
        if pixels.shape[:2] != (height, width):
            raise ValueError("Les calques doivent avoir les mêmes dimensions.")
        if not 0 <= layer.opacity <= 1:
            raise ValueError("L'opacité doit être comprise entre 0 et 1.")

        src = pixels[:, :, :3].astype(np.float32)
        alpha = layer.opacity

        if pixels.shape[2] == 4:
            alpha = alpha * pixels[:, :, 3:4].astype(np.float32) / 255

        out = (1 - alpha) * out + alpha * src

    return np.clip(np.rint(out), 0, 255).astype(np.uint8)

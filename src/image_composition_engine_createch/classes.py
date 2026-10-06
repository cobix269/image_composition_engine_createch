from PIL import Image
import numpy as np
from dataclasses import dataclass
import scipy.ndimage
from filters.py import grayscale, swapBG, brightness, contrast, blur, black_border, invert, sepia
from utils.py import array_from_file
R = 0
G = 1
B = 2
A = 3

class Layer:
    def __init__(self, src: str, opacity: float = 0.1) -> None:
        
        self.pixels: array_from_file(src)
        self.opacity: float = opacity

    def _grayscale(self) -> Layer:
        return grayscale(self)

    def _swapBG(self) -> Layer:
        return swapBG(self)

    def _brightness(self, value: float) -> Layer:
        return 

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
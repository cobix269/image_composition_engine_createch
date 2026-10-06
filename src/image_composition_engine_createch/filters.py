from classes.py import Layer
import numpy as np

R = 0
G = 1
B = 2
A = 3

def grayscale(layer: Layer) -> Layer:
    gray = (
        0.299 * layer.pixels[:, :, R]
        + 0.587 * layer.pixels[:, :, G]
        + 0.114 * layer.pixels[:, :, B]
    )
    gray = np.clip(np.rint(gray), 0, 255).astype(np.uint8)
    layer.pixels = np.stack((gray, gray, gray, layer.pixels[:, :, A]), axis=2)
    return layer

